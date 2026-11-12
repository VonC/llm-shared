# Design v0.14.0: resume paused agent panes

Reference requirement: [resume-paused feature request](feature-request.v0.14.0.resume-paused.md).
The requirement's [29 confirmed decisions](feature-request.v0.14.0.resume-paused.md#requirement-clarifications-for-resume-paused)
govern this design, including their later amendments.

## Context for v0.14.0 resume-paused

Persistent TUIOS sessions retain idle agent panes after a pause. A person
currently visits each pane to resume it. The proposed shared command turns
one human shell invocation into independently checked resume actions across
checkouts, restoring a saved review pair when its requestor takeover is proved.

The launch authorizes the resolved targets and required author or role
overrides. It must not lead to repeated confirmation or routing questions.
Saved routing identifies the targets; current evidence determines whether
input is permitted. Neither routing nor command acceptance proves ownership.

## Scope and deferred integration for resume-paused

The delivery includes a Python 3.12 compatible command and launcher for
existing Claude and Codex panes, automatic pause routing capture and
consumption, target-bound launch consent in both receiving resume workflows,
optional clearing, duplicate protection, and separate paired outcomes.

Agents never launch `resume_paused`, including previews and human-requested
shell escapes. Tests use an injected fake TUIOS runner. The command creates
no panes, claims no review role, and changes no prompt, receipt, journal or
exchange artifact. Receiving agents perform their normal authorized writes.

The [deferred senv checklist](feature-request.v0.14.0.resume-paused.md#deferred-senv-integration-follow-up)
remains unchecked. A separate senv effort must assess reusing the supported
shared interface from `tuitp` after this delivery is implemented and validated.
The implementation plan, validation plan and completion handoff must retain
that link and trigger. No later version or calendar reminder is assigned.

## Confirmed source facts for resume-paused

The source facts describe the checkout at `518080e`, before runtime
implementation. The explicitly dated host observations below were added on
2026-11-10 during the Step 1 feasibility investigation and independent review;
they establish candidate channels, not supported profiles. The separately
dated reviewer findings remain reviewer observations and source analysis.
The writer's disposable 2026-11-12 experiments below reproduce individual
primitives, without establishing supported profiles.

| Source | Confirmed behavior and design consequence |
| --- | --- |
| [Artifact configuration](../../tools/review_artifact_configuration.py) | `ReviewArtifactConfiguration.load` resolves and validates a declared home without preparing it. `prepare_home` writes missing directories and checks exact ignore bytes. The bulk reader must use the read path and validate existing ignore coverage without creating anything. |
| [Artifact helper](../../tools/artifact_home.py) | `artifact_home` prepares the home and `artifact_path` can move a legacy file. These convenience functions are unsuitable for read-only bulk discovery. |
| [Resume instruction](../../instructions/resume-session.md) and [receipt template](../../templates/resume-session.template.md) | The prompt digest, project root and schema 1/2 receipt govern reuse. Current cross-host continuation asks for explicit consent; arbitrary resume arguments are rejected. Bulk marker support is a required change. |
| [Pause instruction](../../instructions/pause-session.md) and [pause template](../../templates/pause-session.template.md) | This branch already documents automatic routing capture, separate historical/intended roles, and the pane/role replacement guard. That documentation does not provide a runtime routing parser. |
| [Review resume instruction](../../instructions/review-resume.md) | Exact selection, identity inspection and claim precede role dispatch. Conflicting recorded host identity currently requires Override or Stop. The marked route must add scoped launch consent while retaining manual behavior. |
| [Claim implementation](../../tools/review_resume_identity.py) | Claims validate the selected round and occurrence under the transition lock and reconcile host identity. Ownership capabilities are returned to the receiving session. The bulk tool cannot replace this transaction. |
| [Coordination record](../../tools/review_exchange_models_coordination.py) | Durable state records role natures, owner and monotonic ownership generation, but no receiving pane identity. Host identity alone cannot prove which same-host pane took over. |
| [Ownership service](../../tools/review_exchange_ownership.py) | Newly issued claims advance the generation; an idempotent claim does not. The coordination record contains only the current owner/generation and token digest, with no claim history. |
| TUIOS 0.12.1, commit `850335c`, read-only `tuios --version`, `agent-log --help` and sampled `agent-log --json --limit 256` | Help documents 256 entries per pane in daemon memory, one-line text and likely-secret masking. Sampled prompt entries reach 100 characters. These observations are limits of the current build, not proof that a new resume profile works. |
| Read-only `tuios list-agents --all-sessions --json` | Claude panes expose `agent_session_id`. Observed Codex panes lack a harness and agent session id; this writer's later sample has `program_status.app == codex`, unlike the reviewer's earlier sample. Profiles must handle either presence or absence without trusting stale working status. Pane ids in both samples are UUIDs. |
| Read-only `tuios capture-pane --help` and pane captures | `--unwrap` joins only rows wrapped by the pane, returning other rows as the program wrote them. A Claude capture retains interface-created breaks; Codex screen reconstruction also needs a tested layout profile. Unwrapping alone does not prove a complete long command. |
| Read-only Codex session-file metadata keys | An observed `session_meta` record has `id`, `session_id`, `cwd`, `timestamp` and `cli_version` (0.167.0). These are metadata facts, not proof that a file belongs to a particular pane. Conversation content was not inspected for this check. Q14=B selects this user-input record channel; its profile is still to be validated. |
| Read-only `tuios integration status codex` | Codex hooks are supported but not installed here. Hook installation and attribution to the correct pane under a shared app-server remain unvalidated; hooks were Q14's option C, which was not selected. |
| Read-only Windows image queries, independently reproduced on 2026-11-10 | For five pane-linked Codex child processes, `QueryFullProcessImageNameW` and `GetMappedFileNameW` resolve the running image to a versioned standalone release, and its `codex-package.json` agrees on version 0.167.0, target and entrypoint. Ordinary process listings expose the unversioned `current` junction instead. The manifest has `layoutVersion` 1 and eight keys, listed in the profile contract below. |
| Independent review's Windows updater observation on 2026-11-10 | Running Claude images had been renamed aside by the updater while a newer executable occupied the launch path. The launch-path file's version therefore cannot prove the running host's version. The reviewer also tested junction retargeting and release-directory renaming using a disposable sleeper; these are reviewer observations, not this writer's host-profile validation. |
| Independent reviewer observations on 2026-11-11, Windows image identity | `NtQueryInformationProcess` class 44 (`ProcessImageFileMapping`, undocumented by Microsoft) returned `STATUS_SUCCESS` for seven running Codex images. Disposable sleepers accepted the original and renamed original, but returned `STATUS_UNSUCCESSFUL` for unrelated, byte-identical and tunneled replacement files. Directory rename could leave a stale kernel name. Limited process-query rights or a read-only file handle returned `STATUS_ACCESS_DENIED`; the observed query needed `PROCESS_QUERY_INFORMATION` and file execute access. These are reviewer observations, not requestor validation of supported Windows builds or the updater lifecycle. |
| Independent reviewer observation on 2026-11-12, Windows 11 build 26200 | On a disposable sleeper, `EnumProcessModulesEx` was denied with error 5 under query rights alone and succeeded only with `PROCESS_VM_READ`. A query-rights-only `VirtualQueryEx` walk of 499 regions found exactly one `MEM_IMAGE` allocation whose `GetMappedFileNameW` name matched the native `QueryFullProcessImageNameW` name. This is reviewer observation, not requestor validation; the address-source contract and supported OS builds still need validation. |
| Independent reviewer observations on 2026-11-10 and launcher source analysis on 2026-11-11, Claude 2.1.321 | Eleven PowerShell-tool background starts use `taskType` `local_bash`. Existing SessionStart commands are recorded as `hook_success` with `SessionStart:startup` or `SessionStart:compact`; pane identity source is `report` although managed integration status says not installed. The reviewer traced the source to senv `tuitp_windows.py`, `write_claude_hooks`: it generates TUIOS Claude hooks in a temporary configuration and copies them into launcher-owned settings. `tuitp.pane.bat` passes that existing file via `--settings`; the reviewer's pane had 14 hook events invoking TUIOS Claude integration. This is optional launcher behavior, not universal TUIOS injection. The pinned [TUIOS integration documentation](https://github.com/Gaurav-Gosain/tuios/blob/850335c0c08bb8b802406fcc7f254355c89af04a/integrations/claude-code/README.md) describes settings hooks, and its [Claude event map](https://github.com/Gaurav-Gosain/tuios/blob/850335c0c08bb8b802406fcc7f254355c89af04a/internal/integration/hook_claude.go) maps SessionStart to identity and transcript reporting. Marker completeness and process-generation binding still require validation. |
| Writer-owned disposable Windows/Codex probes on 2026-11-12 | On build 26200, revision 9711, query-only image walks, same-handle hashes and class-44 identity succeeded for Codex 0.167.2. A renamed copied executable retained identity and a recreated identical file was rejected; full image-name corroboration failed after rename. One diagnostic input matched a unique complete session file and version. Updater, races, timestamp bounds and clear-result signatures remain unvalidated. See the [evidence companion](resume-paused.profile-evidence.md). |
| Writer-owned disposable Claude probes on 2026-11-12 | Claude 2.1.322 recorded launcher-settings startup, typed input, PowerShell and Monitor start/completion, and CronCreate/CronDelete. Monitor starts use `toolUseResult.taskId`, unlike PowerShell's `backgroundTaskId`. Forced host exit left owned commands alive immediately afterward. Startup and session-owner shapes supplied no explicit process-creation identity; complete-generation binding and all-mechanism coverage remain unvalidated. These observations neither prove invisible lifecycle transitions nor invalidate ordinary same-generation activation by themselves. |
| Independent reviewer observation on 2026-11-12, Claude 2.1.322, the reviewer's own `tuitp`-launched pane | The first timestamped record was the TUIOS startup `hook_success`, 41 seconds after process creation and after five untimestamped metadata records. A complete read found 17 record types, 20 attachment types and a `task_status` snapshot immediately after compaction. The pane record had no process field; its activity log had evicted its earliest entries. No user, project or local settings file held a TUIOS hook. Reviewer source analysis found temporary `CLAUDE_CONFIG_DIR` hook generation, root-only explicit settings, launch-time `--resume` and retries in the same pane shell. These are reviewer observations, not writer validation of generation binding or ledger completeness. |
| [Program status](../../tools/program_status.py) | OSC 7501 reports provide app state. They are supplementary evidence, not proof that an input was accepted. |

The [draft](draft.v0.14.0.resume-paused.md) supplies observed TUIOS delivery
behavior. Its agent-run experiment is historical evidence. No live bulk
delivery, supported Codex screen profile or new-conversation command has been
validated by writing this design.

## Target flow for the human launch

```text
Human shell invocation
  -> read all pane, prompt, receipt and duplicate evidence
  -> validate caller and all exclusion/switch names
  -> resolve saved routing and build a read-only plan
  -> independent checkout workers
       -> acquire checkout execution guard and refresh evidence
       -> optional confirmed clear of selected resumed pane
       -> deliver marked native resume; verify acceptance
       -> observe receiving workflow result
       -> for saved requestor with exact live exchange:
            prove consumption and requestor takeover
            -> leave a serving or waiting reviewer alone, deliver marked reviewer resume when no wait is running, or report the reviewer pending
  -> one result per prompt-bearing checkout, omitted-pane count, exit status
```

Preview executes discovery and classification through plan construction,
without acquiring an input action or delivering any keys. Reviewer activation
appears as conditional on takeover, never as an unconditional second command.

## Discovery and evidence model for resume-paused

Use a transport interface accepting argument arrays with `shell=False` and
returning typed discovery, log and capture observations. A clock and wait
interface separates deadlines from observation, allowing deterministic tests.
Malformed output, failed discovery or unsupported evidence is not absence.

Group panes by resolved checkout using filesystem path rules, including
Windows case and separator equivalence. `cwd` identifies the checkout;
optional tab titles are supplementary. Identify Claude by `claude-code` and
Codex by `program_status.app == codex`, falling back to a pane name matching
`^Codex(?: .+)?$` case-insensitively,
only when stronger evidence is absent. The fallback is a normal path when
Codex exposes neither harness nor app status. Contradictory host evidence
is a classification error.

Read the configured artifact home without preparation or legacy-file moves.
A missing home/prompt means no saved task to report. An existing invalid or
unreadable declaration, home, prompt or receipt is an error for that checkout.
Parse prompt metadata and legacy schema 1/2 receipts plus the new schema 3
marked receipt under the existing resume state table; hash exact prompt bytes
and normalize the digest to lowercase. A valid
receipt for different bytes permits a new prompt; malformed receipts and
wrong roots or basenames stop that checkout. Empty or incomplete prompts fail.

Keep evidence with its source, observed time and attributable pause identity.
Use the prompt's offset-bearing snapshot as the pause time. The session
journal supplies additional duplicate evidence, never prompt authority.
Proven older screen evidence is ignored; uncertain attribution prevents input
and fails classification. Report resumer identity/time only when known.

Review observation uses a pure validated snapshot boundary over the existing
artifact parsers (Q09=A). It exposes the exact exchange classification and
non-secret claim evidence without preparing an artifact home, migrating state,
claiming a role or returning a capability. Both the bulk observer and the
receiving validator use this boundary; parsing a general status launcher's
output is not the selected interface.

## Saved routing and role resolution for resume-paused

The routing model separates historical author, pausing pane and saved role
from intended assignments. Its logical fields are:

| Routing component | Required information |
| --- | --- |
| Pause identity | Resolved checkout, snapshot, author and historical session role. |
| Observation | Observation timestamp, source of assignment, and independent identity evidence. |
| Target | Intended role, host, session identity, full pane id, pane label and resolved checkout. |
| Pair | Resumed/requestor target, reviewer target and exact exchange, or explicit not-applicable with reason. |
| Exchange | Family, document or plan, implementation step when applicable, umbrella or none, and occurrence. Select the current round from verified live protocol state. |

The TUIOS session identity is the `session` string from each `list-agents`
agent record, the session name used by the selector, not an internal numeric
id. The saved pane label is supplementary. The bulk command has no separate
restoration mode. A saved pane UUID or session name that no longer matches a
live pane is an absent target and skips; a matching one still needs the host
and checkout checks. Proving that restoration keeps session names and pane
UUIDs attached to the same panes is evidence the deferred integration owes
before it relies on restored targets.

Use a versioned JSON routing block as the bulk reader's sole routing source,
with the human-readable table rendered from it for inspection. The table is
unreleased branch documentation; the canonical main template has no routing
section, and the branch table's free-prose cells have no strict grammar.
Table-only and routing-free prompts remain readable manually and are skipped
by bulk launch. Unknown fields preserve the
rest of a pause and cause unresolved-target skips. Contradictions between
representations, malformed records and unreadable required evidence are errors.

The user's confirmed Q01=B retains this JSON-only bulk boundary. A possible
pre-use conversion of older tables is studied separately below; bulk launch
does not rewrite a prompt or ask for migration.

Pause capture uses independent read-only pane evidence and recorded user
direction. It never contacts a counterpart. Known historical pane or role
differences guard replacement of an unused/new prompt at pause time, even
for the same host. Unknown values alone do not establish a difference.
Legacy checkpoints retain the host comparison. Declining preserves the old
checkpoint and stops that pause. Future intended assignments are not compared.

At launch, validate every selected target's checkout, TUIOS session, full pane
UUID and host against live observations. Require evidence tying the id to
that live pane, host, checkout and session; a matching name alone is
insufficient. A changed pane label alone is reported, not a conflict. Record
an agent session id as supporting evidence, not an
identity that must survive a conversation clear. A changed agent session id
alone is reported and revalidated, including after this run's clear. A known
host, checkout or TUIOS session reassignment remains a classification error;
unavailable identity evidence is an unresolved-target skip. The deferred
integration verifies whether restored sessions keep pane UUIDs unique and
attached to the same panes. No same-host restart permits skipping current
input protections.
Missing/unknown routing and absent targets are expected skips with candidates
reported. A known conflicting identity is an error. Never substitute another
pane, including a sole idle same-host candidate, or ask a migration question.
A saved UUID missing from discovery, or listed without an agent, is an absent
target and expected skip. A UUID now identifying a different agent host is a
known conflict and classification error. Failed discovery is never absence.

`--switch-roles` swaps the two saved targets only for a saved requestor pause
with a recorded pair. It changes roles without choosing new panes. Match its
comma-separated names exactly and case-insensitively against session names
and checkout folder basenames. An unmatched name prevents all input; a
matched inapplicable checkout fails without input while independent valid
checkouts can proceed. Resolve all names before starting workers.

## Legacy routing migration study

The user requested this study on 2026-11-09 with Q01=B. Migration would mean
turning an old table-only handoff into a valid JSON routing handoff before
using the bulk tool. The following is a proposal for later review, not an
approved converter implementation or a relaxation of requirement Q25.

1. Keep ordinary manual `resume-session` followed by a fresh pause as the
   available path. Fresh capture can record currently verified routing in the
   new format, including when old tables are incomplete or targets changed.
2. Assess a separate explicit converter for unused legacy pauses. Start with
   read-only inspection and a proposed diff. Recognize only documented table
   forms and explicit values; reject contradictions and leave missing values
   unresolved. Never use a label, first match or sole candidate to invent a
   pane, role or exchange assignment.
3. Require complete source assignments and independent live validation of
   checkout, host, TUIOS session, full pane UUID, intended roles and exact
   exchange or explicit not-applicable. A valid schema containing unknowns
   remains ineligible for bulk routing; conversion cannot repair missing
   historical intent by guessing it.
4. Before a possible write, check receipt validity, exact source bytes and
   concurrent resume activity again. Refuse consumed prompts and uncertain
   reuse evidence. Adding JSON changes the prompt SHA-256; a matching old
   receipt would cease to match and could make a consumed pause look unused.
   The installed `tuitp` would then also resume it at startup.
   Do not rewrite or delete receipts to manufacture eligibility.
5. Study atomic replacement only after an explicit reviewed conversion action,
   preserving the original task, first-line heading, `Session role`, historical
   author and snapshot. Record conversion time/source separately and render
   the readable routing table from JSON. A repeated conversion should detect
   valid JSON and leave it unchanged. Reject unsupported formats without
   modifying the original.

Before implementing such a converter, resolve its supported legacy grammar,
proof of original intent, concurrent-write protection, recovery and tests.
These points are study findings, not additional decided design questions.
No converter runs as part of bulk discovery, preview or delivery.

## Existing tuitp compatibility and later shared integration

Read-only inspection of the installed launcher on 2026-11-09 establishes:

| Source | Current behavior and consequence |
| --- | --- |
| senv `bin/tuitp_resume.py`, `waiting_prompt` | Reads the prompt heading, the `Session role` line, the exact prompt bytes, and the receipt's `Prompt`, `SHA-256` and `Project root` lines. It ignores `Schema`; a missing or malformed receipt line stops startup resumption for that checkout. It never parses the routing table. This is source analysis, not an integration test. |
| senv `bin/tuitp_resume.py`, `resume_plan` | Uses the first declared pane per agent/checkout, and schedules the opposite reviewer when the pause role contains requestor. It does not consume saved JSON targets or prove requestor takeover before scheduling the reviewer. |
| senv `bin/tuitp.py`, `apply_layout` | Default startup plans pause resumption only for created/restored sessions. `TUITP_RESUME=0` disables that path. Codex receives the command at startup; Claude receives queued input. Existing running agents are not the default startup targets. |
| senv `bin/tuitp.py`, `main` | The explicit `tuitp resume` mode restores native conversations instead of using pause prompts; it is distinct from default paused-task resumption. |

New JSON does not itself start another dispatcher. Existing unmarked native
commands retain manual resume behavior under requirement Q24/Q28, while the
new bulk path uses target-bound markers. The old launcher therefore remains
a different routing path even when it can read the same Markdown. Digest
changes during conversion are the concrete receipt compatibility hazard.

The separate senv effort linked in the scope section must assess one supported
shared planning/validation/delivery interface after new panes are ready. It
must account for restored pane identities, caller restrictions, startup prompt
delivery and reviewer sequencing; merely substituting `waiting_prompt` is
insufficient. Avoid two competing delivery paths for the same pause. Preserve
the intended default startup behavior, its opt-out and the separate native
conversation mode, with integration evidence before claiming compatibility.
Claude positive-absence proof uses existing explicit `tuitp` launch settings
only (Q18=A). The deferred senv effort must preserve those settings or affected
Claude panes remain pending. The shared command installs nothing and operates
independently of the launcher. An installed TUIOS integration, alone or combined
with launcher settings, and missing or uncertain provenance remains pending.
Validate launcher-only root/nested discrimination,
source exclusion, ordering and complete persistence before accepting a profile.
No senv code change is included in this design discussion.

The user's Q10=C qualification requires `tuitp` to keep working and to resume
all eligible sessions. This delivery owns non-regression of the installed
launcher: prompts keep their first-line heading and `- Session role:` line,
receipts keep the three lines it parses, and fixtures validate both grammars.
The deferred senv effort owns the completion condition of resuming all eligible
sessions through the shared interface. Neither condition is compatibility
already demonstrated by the new format.
Cover the full selected layout, both Claude and Codex, single-agent and paired
checkouts, and multiple independent sessions without duplicate consumption.
Keep default startup coverage of created/restored sessions; already running
eligible sessions remain resumable through the shared command. Preserve the
resume opt-out and explicit native-conversation restoration mode.

`apply_layout` reads resume information before the daemon restores sessions
and rewrites pane metadata; restored panes initially contain bare shells, then
the launcher starts their agents. The integration must preserve the required
pre-start evidence and independently validate target identities and supported
profiles after agents are ready, before marked delivery. Prove whether saved
pane UUIDs and TUIOS session identities survive restoration. If they change,
resolve that lifecycle in the integration specification and review any needed
contract amendment before implementation; never guess a replacement from pane
order, labels or a sole candidate, or silently weaken Q10's identity checks.

Integration evidence must cover multiple checkouts, both hosts, clears and
same-host restarts, daemon restoration, newly created sessions, already
running sessions, paired takeover, opt-out and native conversation mode.
Every eligible paused checkout must resume once with its separate role
outcomes reported; protected, excluded, used, legacy, unresolved or conflicting
cases retain their documented skip/error behavior and must be accounted for.
A blanket restored-session skip or absent identity evidence is not proof of
complete integration. This coverage remains unvalidated and must be carried
into the separate senv effort, later plans and completion handoff.

## Target-bound consent for receiving resume workflows

Deliver the native host command followed by `--resume-paused` and a single
compact versioned marker: a random launch id first, then the receiving pane
UUID, resolved role and SHA-256 binding over canonical UTF-8 JSON. The bound
model contains the resolved root, prompt SHA-256, receiving TUIOS session,
pane and host, resolved role, resolved pair, and exact exchange including
occurrence and selected round, or explicit not-applicable. Define canonical
field ordering, path normalization, role tokens, encoding and strict length
limits; reject unknown versions, duplicate fields and malformed values.
This digest is a scope binding, not encryption or an ownership capability.
The receiver reconstructs the assignment deterministically from its prompt,
saved pair, target pane/role and selected live exchange, then compares the
binding. An unresolved or changed selection stops, never acquires another
exchange and never guesses a missing binding. A tested host profile must keep
the launch id within its logged prefix, without masking it.

Both receiving workflows must validate the same marker contract before
consuming a prompt, recording a resume or claiming a role. Prove the receiving
pane independently: the host's complete-input channel tied to
that pane must show this exact marked command as the latest typed input in
the same checkout and host, recorded after delivery. Host notifications such
as Claude's `<task-notification>` entries are not typed input. The host
profile's truncated logged form, including the launch id, corroborates that
evidence but cannot alone prove the full command or its binding. Claude needs
its host transcript tied through the observed session id; screen capture only
corroborates. Codex uses Q14's selected session-file channel: the latest typed
user message must exactly equal the delivered marked command, in the same
checkout and after delivery. Its unique launch id must also appear in the
target pane's displayed command prefix followed by `Working`. Under confirmed
Q15=A, later protected writes keep this initial pane tie after the prefix
scrolls away: they re-prove the same unique session file, its unchanged latest
typed command and the live pane identity, using the carried session identity
and launch id. Reject missing
or ambiguous file matches and host notifications; file metadata alone does
not establish the pane tie. Read only defined metadata and user-input fields
in memory, never print or retain conversation content. Screen reconstruction
and mandatory hooks were the Q14 options not selected. No such marked-input
profile has been validated here. Unavailable complete proof stops before
consumption or claim, even if a prefix matches. An inherited
`TUIOS_PANE_ID` alone is insufficient, including under a shared Codex daemon.
Marker text quoted in a document or older scrollback grants no consent.

For initial resume, compare the current prompt digest and routing against the
resolved assignment, including any requested swap. For reviewer activation,
also require a matching requestor receipt and verified exact-exchange takeover.
A valid marker authorizes only necessary author/recorded-role overrides for
that selection, with no further question. A mismatch or unavailable identity
proof stops before consumption or claim and emits an explicit failure.
There is no fallback consent question. Unmarked manually typed commands keep
their current consent rules. Existing reuse and protocol-state gates remain.

Receiving agents retain migration, inspection, claim and ownership fencing.
An authorized override passes through the existing exact inspection and claim
interfaces; it does not waive damaged state or human convergence gates.
Capabilities stay in receiving-session memory and are never sent to the bulk
tool or written into routing, markers or result lines. Existing commands can
show a capability in pane output or log entries, so the bulk tool extracts
only defined marker, result and readiness patterns, retains raw evidence in
memory only, and never prints or stores it.
The marker creates no authorization file and grants no commit authority.

The capture/consumption and both receiving authorization contracts must be
implemented and validated before bulk input delivery becomes available.
Provider-specific Markdown adapters remain redirects to canonical workflows.

A separate read-only, agent-callable validator serves both receiving workflows;
it is not the human-only bulk command. It strictly parses the marker, proves
the current pane/input, recomputes bindings and reads a validated exchange
snapshot, returning typed non-secret JSON. Receivers call it immediately
before each protected write or claim. It does not consume, migrate, prepare
an artifact home, claim a role or return a capability. The existing locked
`claim_selected` transaction still rejects a changed round/occurrence;
the additional pre-claim check covers the digest, routing and receiving pane.
For Codex, confirmed Q15=A defines what later calls re-prove after the initial
displayed prefix is no longer visible. The receiver passes the session
identity and launch id from the first call; a missing or wrong value stops
before the write. Each later call proves the same uniquely matched file, its
latest complete typed command still unchanged, the checkout, live pane UUID,
host and TUIOS session, and recomputes the bindings and exchange snapshot.
Changed evidence, new typed input or ambiguity stops before the write. The
carried values contain no capability or conversation content; they retain the
initial Q14 tie without replacing Q11's and Q13's current pane and input proof.

If a binding or selection changes between consumption and claim, stop without
claiming another exchange. Retain any truthful completed consumption receipt
rather than undoing it or claiming that ownership was restored (Q11=A).

## Duplicate protection and safe input eligibility

Evaluate all panes of a checkout, including excluded and caller panes, for
duplicate evidence before considering delivery. Any matching receipt, resume
journal entry later than the pause, attributable counted resume input, or
pending author-override question suppresses another initial resume. Declined
or stopped counted attempts still suppress repetition, without proving takeover.

Classify `review-resume` by its selected role across native prefixes and
trailing context. Reviewer-only continuation does not suppress a non-reviewer
pause; it does count for a saved reviewer pause. Uncertain role evidence is an
error, not permission to deliver. Normal `resume-session` counts in every pane.

Match `--except` names exactly, case-insensitively, against full session names,
pane labels and checkout basenames. Session/folder matches exclude their
scope; a pane label excludes only its panes. Unmatched names prevent all input.
Recognized agent callers are rejected for both normal and preview runs with
a nonzero result. Absence of a pane outside TUIOS is not proof of human origin:
human-only use remains the contract there. Never remove inherited caller
variables to evade this rule. The human shell's own pane is always protected.

The target platform for caller detection is Windows, as confirmed with Q08=A.
`resume_paused` supports Windows only in this delivery.
Inspect known agent host markers and Windows process ancestry where available
to reject recognized agent callers. Unavailable ancestry does not prove a
human origin; retain the human-only contract without rejecting ordinary human
shells solely because origin cannot be proved.

Before every clear, resume, reviewer command or recovery Enter, refresh the
pause digest, duplicate signals, routing, selector and pane protections.
Never enter text into a question, draft input, blocked pane or active turn;
skip immediately rather than wait for busy panes. A supported fresh Codex
idle/empty-input capture may override stale working status, never blocked
status. Unsupported/ambiguous screen layouts do not permit input.

Serialize cooperating invocations per checkout with an OS execution guard
held across revalidation and delivery. Use an OS named lock or a lock file in
the user's temporary directory keyed by the canonical root digest, never in
the checkout or artifact home. The guard is not a review lease and
writes no authorization artifact. A held guard causes an immediate skip.
Within a run, process independent checkout workers concurrently, with at most
one input operation active per target pane. A pair keeps its requestor-first
ordering. Revalidation still protects against manual activity between runs;
it does not make terminal discovery and typing an atomic external operation.

## Clearing and delivery confirmation for resume-paused

Host behavior belongs to explicit supported profiles containing readiness,
acceptance, full-input proof, bounded result channels and clear-result
signatures. Independent version evidence comes from a pane's identifiable
host banner or process metadata tied to that pane, never the caller's installed
CLI version. TUIOS discovery alone supplies no Codex version. For Claude, the
transcript named by the pane's observed `agent_session_id` records `version`
and `cwd` on its user, assistant and system entries, giving pane-tied version
evidence before delivery once its profile is validated. Q14's selected
session-file lookup confirms `cli_version` only after delivery and cannot
justify the pre-delivery profile selection.

For the observed Windows standalone Codex layout, obtain the kernel image
name using `QueryFullProcessImageNameW` on the pane's single direct Codex
child, using `PROCESS_NAME_NATIVE`. Corroborate the native name with
`GetMappedFileNameW`. Locate the main image for that call with `VirtualQueryEx`
over the same process handle: exactly one committed `MEM_IMAGE` allocation
must map the native name returned by `QueryFullProcessImageNameW`. Group
regions by allocation base; incomplete walks, no match or multiple matching
allocations are unsupported evidence. Module enumeration, process environment
block reads and any other source needing `PROCESS_VM_READ` are excluded.
These queries inspect address-space metadata, never memory contents. Require
the resolved image to have this shape:

```text
<CODEX_HOME>/packages/standalone/releases/<version>-<target>/<entrypoint>
```

The root is derived from that image, never from the caller's environment.
The release root and its manifest are read through the same `\\?\GLOBALROOT`
prefixed native path.
Read the same release's `codex-package.json`. The observed schema is
`layoutVersion` 1 with exactly `entrypoint`, `execServer`, `layoutVersion`,
`pathDir`, `resourcesDir`, `target`, `variant` and `version`. A pinned profile
validates their types and values; require directory name, version, target and
entrypoint to agree, reject traversal or escaping paths, and match the
profile's SHA-256 for the mapped image. Unknown layouts or schema keys,
renamed or missing images, digest mismatch, API disagreement and ambiguous
pane/process linkage are unsupported evidence. This includes unvalidated npm
layouts. Never resolve `current`, use PATH or invoke a caller CLI as proof.
The banner remains a possible corroborating source.

The kernel path and manifest agreement are confirmed locally; an upstream
manifest compatibility guarantee has not been established. The reviewer's
2026-11-11 observations supply the strict loaded-image identity contract
within the approved process-metadata channel. Open the pane's single direct
Codex child with `PROCESS_QUERY_INFORMATION`, never memory-read rights. Open
the file at the corroborated kernel image name through the `\\?\GLOBALROOT`
prefix with read and execute access,
sharing read and delete only. Call `NtQueryInformationProcess` with information
class 44, `ProcessImageFileMapping`, using that file handle, and require
`STATUS_SUCCESS`. Every other status, failed open or missing file is
unsupported evidence. A missing stale path fails closed.

Hash through that same identity-checked handle and compare the profile's
pinned SHA-256; require agreement with the same release's manifest. Retain
the handle and cache the digest only within this invocation, keyed by process
id, process creation time and kernel image name. Before each input, recheck
the process creation identity, both image-name APIs and manifest bytes, and
repeat the identity query with the retained handle. Changed or contradictory
bindings fail closed. The identity query supersedes creation-time ordering:
neither matching bytes nor NTFS name tunneling makes a replacement the
original loaded image. No same-user replacement exception applies.

Microsoft does not document this information class. Each profile pins
validated OS build numbers, for example 26200, and records the update revision
observed during validation. The runtime reads the OS build number from the
`dwBuildNumber` that `RtlGetVersion` returns, requiring a valid decimal value.
System file versions, such as Python's
`sys.getwindowsversion().platform_version`, are not build evidence.
Missing or invalid metadata and a build outside the pinned set
are unsupported evidence with no input. The update revision is validation
evidence, not an additional runtime pin. Within a pinned build, unavailable or
denied queries and every non-success result still fail closed.
The strict attribution contract is resolved, but the
channel remains unsupported until Step 1 validates it and the rest of the
profile. No process memory is read; the reviewer's observations are not
requestor lifecycle validation.

The matched Q14 session file must subsequently report the same `cli_version`
as the pre-input proof. A difference is contradictory evidence: the receiver
stops before consumption or claim and reports evidence failure. This check
can detect a differing shared-server version; it never selects or repairs
the profile after input.

Step 1 must validate this channel and the remaining profile signatures before
support is enabled. Failed validation returns to design review; it does not
ship one host or add hooks silently. Requiring hooks for version evidence
would need the user to reopen Q14=B. Missing unique profile/version evidence
is a classification failure under confirmed Q06=A without input. Codex
new-conversation syntax must also be confirmed for the supported version;
do not try alternate commands in a live pane to discover it.

With `--clear`, clear only the selected resumed conversation. For Claude,
skip a redundant clear only when the current-pause log shows
`session started (clear)` with no later prompt; still deliver resume.
Otherwise confirm that event and readiness after `/clear`. For Codex, require
the supported new-conversation screen result. An unconfirmed clear fails that
planned action and prevents resume. Report a background-shell indicator when
present; do not enumerate, stop or duplicate shells. Never clear the counterpart.

Deliver with the proven selector transport:

```text
tuios ask-agent --select 'session:S name:N' --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <marked native command>
```

Use the live session name as `S` and the live name observed for the validated
UUID as `N`, immediately before delivery, rather than the saved pane label.
Selector spaces require the documented wildcard representation. Resolve the
result to exactly one full pane id immediately before delivery; wildcard
collisions or uncertain resolution are errors. Run TUIOS directly with an
argument list, avoiding shell parsing and MSYS argument rewriting.

Claude acceptance requires this run's marked input in the profile's logged
form as a `prompt` entry after delivery, plus complete typed-input proof from
the session-id-tied transcript. Codex acceptance requires the displayed command
prefix with this delivery's unique launch id followed by `Working`, plus Q14's
complete typed-input proof. A prefix or `Working` alone is insufficient.
An `ok` result or idle status alone is insufficient. Codex acceptance also
requires the Q14 version cross-check above; disagreement prevents receiving
consumption and claim, even if the marked text was accepted.
Bound the delivery and
acceptance observation by 100 seconds per action, including any recovery;
the transport's stall bound remains 60 seconds.
These and the separate 120-second post-acceptance bound are fixed documented
defaults, without human CLI timeout overrides (Q05=A). Tests inject clocks.
The call may exhaust the full 100-second action budget. Recovery runs only
within the remaining budget; when none remains, report unconfirmed delivery
without a recovery Enter. No second 100-second window is created.

Only Codex permits one recovery Enter for this run's proven unsubmitted
command. Retain the pre-input empty capture; after delivery require two
unchanged exact-command input captures, with neither placeholder below nor
Working. After fresh eligibility checks, target `send-keys` at the same full
pane id and send Enter once. Verify acceptance again, and the clear result
when relevant. Never retype, resend uncertain delivery, or repeat Enter.
Report recovery use; unproved acceptance fails. Claude has no Enter recovery.
An unsubmitted command is absent from the session file. Recovery requires a
tested Codex layout profile to prove the complete exact command in the input
box, beyond pane-level unwrapping. When a wrapped command cannot be proved,
send no recovery Enter and report unconfirmed delivery.

## Takeover observation and later reviewer continuation

Command acceptance, prompt consumption and ownership restoration are separate
states. After acceptance, observe the receiver for at most 120 seconds using
read-only evidence. Apply this separate post-acceptance bound to every
receiver, including a single agent, requestor takeover and an activated
reviewer. Reviewer acceptance does not prove reviewer completion.
Use event-driven observation where available, otherwise
bounded local reads with backoff up to five seconds. No busy-loop or new
assistant turn is needed for these observations.

Receiving workflows add non-secret bindings to existing durable records.
A schema 3 receipt retains root/digest/host and adds launch id, pane and
assignment binding. Schema 3 keeps the schema 2 `- Prompt:`, `- SHA-256:` and
`- Project root:` lines, with the same `- Name: value` grammar and values,
and only adds lines. The installed `tuitp` reads those three lines and ignores
`Schema`, so it keeps reading schema 3 receipts without a senv change.
A marked claim atomically records launch id, pane, host,
assignment binding, selected round/occurrence and its issued generation in
the existing coordination record. No claim history is assumed. Normal
transitions preserve that binding until another claim supersedes it; it never
permits reuse after a different claim. Legacy records remain readable, but
absence of these fields cannot prove a marked takeover. Receivers alone write
these records; the bulk tool only reads them. The new binding fields hold no
token or token digest; normal existing capability storage is unchanged.
Older review readers reject unknown coordination fields, and older
`resume-session` instructions stop on schema 3 receipts. This is expected
fail-closed behavior in a mixed install. The marked route ships with its
readers in one release, with no separate switch. Every llm-shared install
used by either host must run compatible `resume-session`, `pause-session`,
`status-session` and `list-session` instructions, review exchange tools, the
receiving validator and `resume_paused`. The external `tuitp_resume.py` reader
remains compatible through the preserved three-line grammar; it does not
require the deferred shared-interface integration before this route ships.
Legacy readability by new readers does not make new records readable by old
ones.

Each host profile also defines a compact non-secret result, at most 100
characters, containing launch id, outcome and optional claim generation.
On a stopping Claude turn it is the first line of the final response and is
observed through the `turn_end` logged form or the session-id-tied transcript.
A continuing turn's success is established through durable receipt/claim
records without waiting for turn end. Codex shows the result on screen,
counted only when the tested layout profile rebuilds it exactly, or reads it
from the Q14-matched session file restricted to the defined result pattern,
with the same durable success proof. Failure results must be emitted before
returning or asking an unexpected question; the observer also checks
blocked/question state. Log truncation, masking or eviction never becomes
positive proof.
No result contains an ownership token or its digest, and no new authorization
or continuation file is introduced.

Requestor takeover requires all of the following to agree freshly:

1. The receipt matches the intended digest/root and selected resumed host.
2. The receipt and marked claim bind that independently identified requestor
   pane, launch and assignment to successful consumption and the selected claim.
3. Read-only protocol evidence corroborates the selected exchange, role nature
   and current claim generation without damaged or conflicting state.
   Transitions by the current owner retain the generation; a newly issued
   claim advances it, including a pickup or a counterpart's wait claim.
   First apply the exact
   active-reviewer leave-alone check. Otherwise require the marked requestor
   claim generation still to be current; a competing pickup blocks activation.

A receipt, Working, a historical role record or former requestor context alone
cannot satisfy this proof. Missing proof after the bound reports reviewer
pending and does not alone fail. An observed marker mismatch or repeated
author/role/routing question fails. Single-agent processing still in progress
at the bound is reported as accepted with completion unconfirmed, without
claiming completed work. Missing command acceptance remains a delivery failure.

Only a saved requestor pause with an identifiable live exchange activates a
counterpart. A validated saved exact identity can select it among other live
exchanges. No live exchange makes pairing inapplicable; unresolved multiple
exchanges leave pairing ambiguous. Reviewer pauses resume only their saved
reviewer, and other saved roles resume only their selected agent.

Before activation, apply the leave-alone check. Leave a reviewer already
serving the exact exchange untouched when current pane and protocol evidence
agree. A global reviewer wait is not bound to one exchange and leaves no
durable waiter record. Prove that wait using the pane's complete-input channel
and current host waiting evidence (Q16=A): the latest typed input must be a
reviewer `review-resume` in this checkout, with no later typed input. For
Claude, that proof would require a background watcher started after that input
and still running in the same session, including one restarted after an answer.
No permitted channel supplies current Claude watcher liveness in this delivery:
the proved-global-wait branch is unavailable and every potential Claude wait
is reported pending without input. Requirement Q04=A excludes enumerating the
Claude process's background descendants. For
Codex, an active turn is already protected by the busy-pane skip. Leave a
proved waiting reviewer alone. A shell is never a counterpart.

The concrete Claude candidate is a transcript lifecycle ledger tied to the
pane's current `agent_session_id` and host-process generation. A generation
is the lifetime of the pane's own Claude process, identified by its creation
time and process identity. Reading that process's metadata does not enumerate
background shells. No hooks, waiter record or new durable artifact is added.

The independent reviewer observed these shapes in its own version 2.1.321
session, across compactions; they remain version-pinned profile candidates:

- The eleven observed starts came from the PowerShell tool, recorded with
  `taskType` equal to `local_bash`, and have
  `toolUseResult.backgroundTaskId`. Bash-tool starts remain unobserved.
- A terminal notification is a `queue-operation` enqueue carrying the same
  task id and terminal status, followed by a user record whose `origin.kind`
  is `task-notification` and `promptSource` is `system`. Validate exact status
  values, ordering, duplicate handling and notification-only cases.
- Typed input has `origin.kind` equal to `human` and `promptSource` equal to
  `typed`. Validate slash-command records separately; notifications cannot
  replace the latest typed reviewer entry.
- `task_status` attachments are individual snapshots, never a complete
  inventory or a zero-task assertion. The reviewer observed a host-killed
  watcher whose older snapshot still said `running`; a later terminal event
  takes precedence over that snapshot.

The ledger is a hypothesis to validate, not proof that every host transition
is persisted. For Q16, identify a watcher start for `wait-any-request` after
the latest typed reviewer `review-resume`, within this generation and with
no later terminal event. Such a start only names the pending reason.
A missing terminal event alone does not prove
current liveness. No permitted affirmative same-session current-liveness
channel is available in this delivery. Retain every potential Claude wait as
unknown and report pending without input. A background-shell indicator alone
is insufficient.

A measured terminal-persistence delay does not supply current liveness. Even
if a hard bound `D` existed, no terminal record by `t + D` could establish at
most that a task was running at the earlier time `t`; it might have ended
before the current decision. Finite timing samples also do not establish a
hard bound under arbitrary host scheduling. Treat these measurements as
validation data only. No affirmative current liveness channel is established
by this review. Both a proved wait and an unknown potential wait send no input;
activation depends solely on positive absence, never on a liveness timeout.

An unexpired session-scoped scheduled prompt, including `CronCreate` and
scheduled wakeups, or a background subagent can also produce reviewer work.
Treat validated current waiting evidence as waiting and incomplete evidence
as unknown; neither permits activation. Reconstruct restored schedules from
the complete relevant session history, including definitions before process
creation, rather than assuming a fresh process has no scheduled work.

Activation requires positive proof that the host's waiting mechanism is
absent (Q17=A). For Claude, complete transcript evidence for the pane's session
id and Q19's checkout history must prove absence of Claude-managed waiting mechanisms under a
validated profile, including after a host restart (Q20=A). This covers background
tasks, `Monitor`, subagents and their commands, schedules/wakeups and foreground
work moved into the background. Reviewer watchers must start through host
background mechanisms. Each activation report must disclose three residual
limits: processes detached by completed foreground commands or hooks may be
missed; earlier hook-handler configuration history is unavailable; backward
clock changes since the last OS boot can remain undetectable (Q21=A), including
offsetting changes. Ownership fencing
and lease expiry do not prove watcher absence. The candidate contract requires
all of the following:

1. The transcript covers the complete current generation under a validated
   ordering and source-exclusion contract. Resolve the pane shell's single
   direct Claude child with query-limited process rights, retain its process
   id and creation time, and recheck both after the complete ledger read.
   The pane's `agent_session_id` must have identity source `report`. The
   candidate file's first timestamped record must be the TUIOS
   `SessionStart:startup` `hook_success`, timestamped at or after process
   creation; untimestamped metadata may precede it. No maximum gap applies.
   Any later SessionStart other than `compact`, changed process/session,
   missing prefix or ambiguous boundary means pending. Launch-time `resume`
   remains pending until its own generation rule is validated; the launcher
   can restore conversations with `--resume`. Only existing explicit launcher
   settings are eligible (Q18=A); inspect documented sources and reject
   an installed TUIOS integration, alone or combined with launcher settings,
   and missing or uncertain provenance. A pane without a marker stays
   pending. Installing hooks remains excluded. The candidate uses ordering,
   never timestamp proximity. Its stale-root argument requires validation
   that an earlier root's recorded marker cannot fall after the next root's
   creation. The candidate assumes timestamps mark event creation and may
   be persisted late, making them earlier than their write; an exited root
   writes nothing itself. Validate a single-writer guarantee: no other
   process writes that transcript after the root exits, including backgrounded
   or reattached sessions and retries. A backward step between the earlier
   root's last write and the new root's creation is undetectable through
   approved sources and is an explicitly reported residual limit (Q20=A).
   Preserve ordering and timestamp-semantics validation within that limit.
   Do not require timestamps
   to increase in file order: healthy observed files persist them out of order.
   Require validated root-interactive record markings; test whether nested
   sessions can be distinguished by their own markings rather than assuming
   hook-file continuity. Timestamp semantics and markings remain to validate.
2. Classify the complete ledger under a version-pinned closed-world profile:
   every top-level record, attachment, tool name, call and result shape must
   be classified. Unknown records, tools or shapes and open tool calls mean
   pending. Foreground-only results need a validated contract excluding
   unresolved host-managed waits. Arbitrary detached external work is the
   reported Q20=A limit, not an absence guarantee.
   Recognized background starts include
   `toolUseResult.backgroundTaskId` for validated PowerShell/Bash versions
   and `toolUseResult.taskId` for validated `Monitor` versions. Each needs a
   later validated terminal enqueue with the same id and terminal status;
   stop/interface results require their own validated terminal shape.
   A foreground tool returning a task id is moved work and remains pending
   until its shape is validated. A background subagent needs its validated
   completion and complete command history. Compaction task-status snapshots
   are not inventories. Classification complements the requirement to prove
   complete start/end persistence for every enabled host-managed waiting
   mechanism (Q20=A). Classification cannot replace that proof.
   A known tool or hook could start work without a new record
   type, so unknown-type rejection alone is insufficient.
3. A `CronCreate` result id needs matching validated `CronDelete` or firing
   evidence. A recurring/durable schedule, an unexpired nonrecurring one or
   an unresolved scheduled wakeup means pending. Read restored definitions,
   including those before process creation. No background subagent,
   `Monitor`, PowerShell task, moved foreground command or other supported
   background activity may remain running. Only the validated TUIOS handler
   set is eligible; other current handlers, including skill/subagent frontmatter
   hooks, or uncertain source provenance mean pending. Inspect documented
   current hook sources; present contents or modification times alone
   cannot prove that no handler ran earlier: copies or renames can preserve
   old times, and skill/subagent hooks can appear mid-session. No approved
   source records handler configuration history. This unavailable history and
   detached hook work are reported residual limits under Q20=A. Binding still
   needs validated record-level discrimination of nested sessions. Unknown
   scheduling or incomplete evidence for in-scope task state remains pending.
4. The file is read completely, without missing bytes or a truncated last
   record. Fresh idle/empty-input evidence and stable session/process binding
   agree with the ledger. Records can be persisted late and out of order,
   so an idle screen does not prove the last turn is on disk. Require a
   validated turn-closure condition: every tool call has its result, every
   result has its call, and the turn's validated final record is present.
   Refresh all required state under the execution
   guard immediately before delivery; it is never cached authorization.
5. Read every transcript in this checkout's Claude project directory with
   activity since the last OS boot (Q19=A), plus complete relevant durable
   schedule definitions regardless of boot. Validate activity selection and
   complete reads with byte accounting. Missing history, uncertain activity,
   schedule restoration or uncertain boot semantics means pending; handle
   Windows fast startup conservatively. Under Q21=A, use a boot instant recorded
   once at boot from the creation time of a validated process that starts at
   boot, within the approved process-metadata channel. Validate that this
   timestamp stays fixed across clock changes; never use current time minus
   uptime as the selection boundary. Compare the fixed instant with current
   time minus uptime and keep detected net backward movement beyond a validated
   tolerance pending. Validate the concrete boot process, timestamp stability,
   uptime semantics, tolerance and fast-startup behavior. Report undetectable
   backward changes since boot, including offsetting changes, as Q20's widened
   clock limit. This approves no event-log or general extra channel.

   The uptime value must count time spent in sleep and hibernation. Validate this,
   and test suspension between boot and the decision. An uptime that excludes
   suspended time would hide a backward change of up to the suspended duration.

   Under Q22=A, exclude from the absence check only validated new work of the
   proved requestor pane's current process generation. Earlier starts, every
   other transcript and recognized reviewer watcher starts remain in scope.
   Read and classify the records needed to prove the exception; do not skip
   enumeration, byte accounting or watcher recognition. Uncertain requestor
   generation or ordering means pending. Refresh the exact takeover evidence
   and both panes' required process/session bindings before activation, on
   initial activation and later continuation. This exception does not discard
   earlier watchers, including a former reviewer's after `--switch-roles`.

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

   An unmatched in-scope start stays pending
   across host-process generation changes. A validated true OS boot can bound
   ordinary surviving processes, but never discards durable schedules. No
   observed field identifies how an earlier generation ended; the writer's
   2026-11-12 forced termination left background commands running. A validated
   recorded exit marker proving cleanup could change that conclusion, but
   none has been observed. Include backgrounded and reattached sessions.
   Current-file completeness also cannot exclude a surviving command whose
   start is in another session file after a launcher retry or manual restart.
   Include that older session within the agreed history scope; do not declare
   support until the scope and its persistence guarantees pass validation.

   The host's project-directory name encodes the path lossily, so distinct
   checkouts can share one directory. Validate each candidate transcript's
   recorded `cwd` against the resolved checkout using this design's path rules.
   Exclude a transcript as another checkout's only on that validated evidence;
   otherwise keep it in scope. Include project directories for sessions started
   in checkout subdirectories unless validation proves they cannot serve a
   reviewer watcher for this checkout. Incomplete directory enumeration stays
   pending. Validate this candidate set before claiming support.

   The ledger parses only classified structural fields it needs in memory:
   record and attachment types, tool names, call/result linkage, task ids and
   statuses, origin kinds, timestamps, recorded `cwd`, and typed reviewer-entry
   and watcher-start matches. It never prints or retains conversation content
   or tool payloads, and reports only counts and classified reasons.

These are proof obligations for the candidate ledger. A cleared, forked or
switched session cannot prove absence from its current transcript alone,
because earlier background work can survive a clear. A crash with unproved
cleanup, unsupported version, incomplete history or unknown lifecycle stays
pending. The host documentation describes cleanup on exit and retained work
when backgrounding a session; these descriptions are not a complete JSONL
schema or crash/restart contract.

For Codex, require a fresh supported capture proving an idle pane with empty
input and no active turn. Only then
deliver the target host's marked `review-resume as reviewer` after current
exact requestor takeover proof, all normal eligibility checks and the
later-continuation rules, preserving the conversation and normal claim
workflow. Never resend an uncertain prior reviewer delivery.

An idle Claude pane whose validated evidence proves its watcher has stopped
may therefore be activated; it is not automatically pending merely because
an earlier reviewer entry command exists. Missing indicators or ambiguous
evidence do not prove absence. If neither a wait nor its absence is proved,
send no input and report the reviewer pending with the reason. No host profile
or restart/absence evidence is claimed validated by these decisions.

A later invocation may perform only the verified missing reviewer action.
Reconstruct its state from the unchanged pause, bound receipt and exact
durable marked-claim evidence; pane results are supplementary. This survives
log eviction or daemon restart while the selected claim remains current.
Create no separate continuation file.
Reapply exclusions and protections without clearing/resuming the requestor.
An uncertain prior reviewer delivery is diagnosed rather than resent.

The resumed requestor must match the invocation's resolved assignment. A
switched continuation repeats `--switch-roles`. Mismatch with that explicit
flag fails without input; mismatch without it is an already-resuming skip
that explains the required flag. Prompt replacement or changed exchange
identity invalidates continuation rather than redirecting it.

## Reporting and exit semantics for resume-paused

Use one compact result line per checkout holding a prompt, including used
prompts. Include title, author/time, saved/unresolved routing and validation,
selected pane identities, clear/recovery use, and separate resumed/requestor
and reviewer outcomes. Indicate unknown resumer identity/time explicitly.
Omit prompt-less checkouts and non-target panes, then report omitted-pane count.
Preview includes the exact intended marked commands and conditional reviewer
dependency, while delivering nothing.

Every Claude reviewer activation outcome and every preview showing conditional
Claude activation carries `limits=claude-wait-scope`. Help and the reference
page define this fixed code as the three Q20=A limits: detached processes from
completed foreground commands/hooks may be missed, earlier hook configuration
history is unavailable, and backward clock changes since the last OS boot can
remain undetectable, including offsetting changes (Q21=A). This compact code
supplements the reviewer outcome; it never claims an absence guarantee outside
the confirmed scope. Detected net backward movement beyond the validated
tolerance keeps activation pending. Q22=A's narrow requestor-work exception
changes the absence-check scope, never these disclosed limits.

| Outcome class | Invocation result |
| --- | --- |
| Expected skips, protected caller, unsupported pauser, missing/unknown routing, empty plan, reviewer pending takeover, reviewer pending on incomplete waiting evidence (Q16), accepted with completion unconfirmed for any receiver (Q12) | Success when no independent failure exists. |
| Unreadable or contradictory required evidence, uncertain attribution/selector, malformed receipt | Failure for the invocation; independent valid checkouts continue. |
| Global discovery failure, unmatched exclusion or switch name, recognized agent caller | Failure with no input anywhere. |
| Matched switch without an applicable saved pair, or mismatch with explicitly switched continuation | Failure for that checkout with no input; independent valid checkouts continue. |
| Unconfirmed planned delivery/clear, marker mismatch, repeated automated-route confirmation | Failure; never retry uncertain input. |

Use exit 0 for success, 1 for classified execution failures, and 2 for invalid
CLI syntax. Expected pending observation is distinct from a completed pair.
Dry runs apply the same classification and name-validation failures.

## Acceptance examples and validation boundaries for resume-paused

| Scenario | Expected result |
| --- | --- |
| Several same-host panes; complete saved routing names one | Only that independently validated pane is eligible. Missing routing never falls back to a sole candidate. |
| Human requests a saved pair swap | Resume the former reviewer as requestor with scoped launch consent; activate the former requestor only after exact takeover proof. |
| Another pane has a declined resume attempt after the pause | Suppress initial resume checkout-wide, including evidence from excluded panes. Do not infer takeover. |
| Codex status is stale working, but supported capture proves idle empty input | Permit the fresh eligibility check; blocked status, questions and drafts remain protected. |
| Codex delivery leaves this run's exact text unsubmitted | One full-id Enter only after all ownership/non-submission checks; otherwise no recovery. |
| Marker names a different pane, digest, role or exchange | Receiver stops before receipt or claim; invocation fails without another consent question. |
| Reviewer already serves the selected exchange | Leave it untouched on initial and subsequent launches. |
| A Claude reviewer's watcher, restarted after an answer, still runs after its typed `review-resume` | Leave it untouched; report the reviewer pending unless validated current liveness proves the wait (Q16). No permitted current-liveness proof is available in this delivery. |
| Reviewer evidence neither proves a wait nor shows that none is running | Send no input; report the reviewer pending with the reason (Q16). |
| Reviewer evidence shows that no wait is running (Q17=A) | Deliver the marked reviewer resume after takeover proof, eligibility checks and later-continuation rules; never resend uncertain prior delivery. |
| Host records a watcher as `killed`, and the validated complete ledger proves every background activity ended | Positive absence permits activation after the remaining takeover and eligibility gates. |
| A Claude reviewer clears or switches sessions after starting background work | Current-transcript absence is unproved; reviewer stays pending. |
| An old `task_status` says `running`, followed by a validated terminal event | The task is ended; activation still requires complete absence proof for all activities. |
| A watcher start has no terminal event, but no fresh affirmative liveness proof | Potential wait is unknown; leave pending without input. |
| An unexpired restored scheduled prompt or unproved background subagent remains | Waiting or unknown; no reviewer activation. |
| A persistent `Monitor` has no validated terminal event | Pending without input. |
| An installed TUIOS integration is present, alone or with launcher settings | Pending without input (Q18=A). |
| An earlier checkout transcript active since boot has an unmatched in-scope start | Pending without input (Q19=A/Q22=A); no general other-pane exclusion. |
| An ordinary start predates a validated true boot | Discharged only under validated Q21=A fixed-boundary semantics; durable/restorable schedules remain in the read set (Q19=A). |
| The wall clock moves forward after boot | The validated recorded boot instant stays fixed; current time minus uptime never replaces the selection boundary (Q21=A). |
| Comparison detects net backward clock movement beyond the validated tolerance, or boot metadata is uncertain | Pending without input (Q21=A); disclose the residual undetectable-backward-change limit since boot. |
| The proved Claude requestor starts an answer wait after its marked resume | Q22=A excludes only starts proved created after the marker and their own lifecycle records; all remaining gates still apply. |
| A Claude requestor resumed with `--clear`, or after a manual clear, proves takeover and starts its answer wait | Q23=A permits Q22=A only after the marked-input file passes the validated startup-or-clear requestor binding; uncertainty means pending. Pre-clear history and all other gates remain in scope. |
| A requestor start from before its marked resume ends after it | The terminal record still matches the earlier start, including across a clear; only starts proved created after the marker are excluded (Q22=A). |
| A reviewer watcher start occurs in the proposed requestor exclusion, or an earlier watcher survives a role switch | Stays in scope under normal start/end matching and blocks until its validated terminal record; ambiguous review-exchange operations stay in scope (Q22=A). |
| Requestor generation binding or record order cannot be validated | Pending without input; do not apply the Q22=A exception. |
| A Claude reviewer is activated, or preview shows conditional activation | The result includes `limits=claude-wait-scope`, defined in help/reference as the three Q20=A limits, with Q21=A's since-boot clock scope. |
| A background subagent has no validated completion record | Pending without input. |
| A recurring/durable schedule or unresolved wakeup remains | Pending without input. |
| A record, attachment, tool or result shape is unclassified | Pending without input. |
| A moved foreground command has an unvalidated result shape | Pending without input. |
| A tool call has no matching complete result | Pending without input. |
| A tool result lacks its call, or the last turn lacks its validated closing record | Pending without input. |
| Codex mapped image is outside the pinned release layout, or its manifest/digest disagrees | Unsupported profile evidence; no input. |
| A different file, including a byte-identical copy or another pinned release, occupies the kernel image name after a rename | Identity query fails; unsupported evidence, no input. |
| The identity query is unavailable or denied on the Windows build | Unsupported evidence; no input. |
| The OS build number is not pinned by the Codex profile | Unsupported evidence; no input. |
| Post-delivery Codex `cli_version` differs from independent pre-input version | Receiver stops before consumption or claim; evidence failure, no resend. |
| Requestor receipt exists but pane-specific claim proof is missing | Do not activate reviewer. Report the missing proof. |
| Later switched continuation omits the switch flag | Expected already-resuming skip with the flag explained; no requestor input. |
| Two cooperating launches target one checkout | Only the execution-guard holder can revalidate and deliver; the other skips. |
| A pane id is reused or required evidence contradicts routing | No input to the checkout; classification failure rather than guessed routing. |
| Saved UUID is missing or its pane has no agent | Expected absent-target skip; do not substitute another pane. Discovery failure remains an error. |
| Saved UUID now identifies a different agent host | Classification failure; no input to that checkout. |
| Agent launches preview | Refuse without pane input and return nonzero. |

Validation must exercise these decisions through fake discovery, logs,
captures, time and delivery results, including multiple independent checkouts
and changing evidence before every input action. Cover custom artifact homes,
receipt schemas, malformed inputs, all protected panes, switch/exclusion scope,
single-agent observation, paired continuation and both marked receiving
workflows. Verify no writes by the bulk reader and no live TUIOS requirement.
Add fixtures proving that a schema 3 receipt preserves the installed
`tuitp` parser's three-line grammar and that the prompt keeps its first-line
heading and `- Session role:` line. These are current-delivery compatibility
checks without importing or changing senv code; they do not establish runtime
integration validation.
Include logged-form truncation/masking, host-created row breaks that survive
unwrapping, exact session-file input matching and ambiguous or missing matches,
pre-delivery version evidence and the all-readers compatibility rollout,
host notifications after delivery, a cleared Claude pane with a new agent
session id, Codex without app status, an activated reviewer stopping on marker
mismatch, exhausted recovery budgets, and later continuation after log eviction
or daemon restart. Cover a missing or wrong carried Codex session identity or
launch id, and new typed input between protected writes (Q15); a Claude
watcher restarted after an answer, later typed input after a reviewer resume,
a stopped watcher, and each leave-alone, pending and activation outcome
(Q16, Q17). Validate both hosts' profiles before release; the currently
observed evidence gaps are not permission to ship only one supported host.

Profile validation requires controlled disposable sessions, never live review
panes. Synthetic fixtures can verify a known contract but cannot establish a
host's persistence or lifecycle guarantees. Pin validated versions, layouts,
manifest schema and image digests before declaring a profile supported.

For Claude, establish complete start/end persistence for host-managed waiting
mechanisms (Q20=A) and typed-input shapes,
and classify every record, attachment, tool call and result for each pinned
version. Reproduce start, ordinary completion, `TaskStop` or interface stop,
and host kill for PowerShell, Bash, `Monitor`, background subagents and their
commands. Record exact terminal statuses, task-id fields, ordering and
duplicates; absence of a validated terminal shape means pending. Cover
`Ctrl+B` and timeout moves and compaction snapshots. Determine whether
subagent commands persist in the main or subagent transcript, and account
for complete relevant history. Classification alone does not establish that
known tools cannot leave unrecorded in-scope waits. Detached foreground or hook
processes remain an explicitly reported limit. Require reviewer watchers to
start through host background mechanisms; an optional validated rejection list
for recorded detaching launchers is defense in depth, never absence proof.
Exercise clear with running work, fork, orderly exit, launch-time resume,
in-process resume, background sessions, reattach, window close and forced
termination, checking only the disposable process tree. These experiments
establish record shapes; a generation change does not discharge unmatched
starts. Validate each of these generation-binding cases:

1. A `tuitp`-launched process has the candidate startup ordering against its
   direct-child process creation, including any untimestamped prefix.
2. After exit, plain Claude without launcher settings in the same disposable
   pane leaves the old reported session stale and rejected.
3. A nested print-mode Claude launched through the disposable session's tool
   cannot change the pane's reported session under launcher settings alone;
   record the nested session's marking and prove discrimination from the
   root's interactive marking. The reviewer observed `entrypoint: cli` on
   every record carrying that field in its own interactive session only.
4. Launcher `--resume` and early-failure retry paths record their markers and
   whether the session id changes. Restored panes remain pending until a
   separate launch-time resume rule validates.
5. `/clear` and `--fork-session` remain pending.

Validate timestamp semantics and single-writer behavior after root exit
across backgrounding, reattach and retry. The reviewer observed 43 of 703
timestamped records persisted after a later-stamped record, by up to 42.4
seconds; this proves disorder and lag, not a complete source contract. A clock
step between generations is unobservable through approved sources and must be
reported as a residual limit (Q20=A). Add turn-end experiments with and without a background start: record
persistence order, identify the final closing record, and validate both call
and result completeness before treating a turn as closed.
Inspect documented current hook sources; unavailable earlier configuration
history is a reported Q20=A limit. Current contents and
modification times alone are insufficient because copies/renames can preserve
old times and skill/subagent hooks appear mid-session. The reviewer observed
PreToolUse/PostToolUse execution without transcript records. Test root versus
nested record markings for binding; detached hook work is a reported limit.
Validate existing explicit launcher settings only (Q18=A). An installed TUIOS
integration, alone or combined with launcher settings, and missing or uncertain
provenance stays pending; inspect excluded sources without
installing hooks. The recorded command cannot distinguish the sources; command-line
inspection is excluded because it reads process memory. Neither settings
nor integration means no marker and pending. Validate Q19=A selection of all
checkout Claude transcripts active since the last OS boot and all relevant
durable schedule definitions regardless of boot. Account for every byte read;
missing history, uncertain activity or schedule restoration stays pending.
Validate true-boot semantics and treat Windows fast startup conservatively.
Validate Q21=A's fixed boot timestamp, concrete boot-process source, stability
under forward/backward changes, uptime semantics, comparison tolerance and fast
startup. Test detected net backward movement as pending and offsetting changes
as a disclosed limitation since boot.
The uptime value must count time spent in sleep and hibernation. Validate this,
and test suspension between boot and the decision. An uptime that excludes
suspended time would hide a backward change of up to the suspended duration.

Validate Q22=A's narrow proved-requestor current-generation exception on initial
activation and later continuation. Cover earlier starts, other transcripts,
reviewer watcher starts inside the proposed exception, role switches and
ambiguous binding/order. Preserve complete reads and byte accounting.
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

Validate each candidate transcript's recorded `cwd` using this design's
path rules because project-directory encoding is lossy. Exclude another
checkout's transcript only on validated `cwd` evidence; otherwise retain it.
Include checkout-subdirectory session directories unless validation proves
they cannot hold a reviewer watcher for this checkout. Incomplete enumeration
cannot prove absence.
Test restored `CronCreate` prompts and scheduled wakeups, including whether each
pinned version retains schedules at exit or restores them through launch-time
or in-process resume. A validated none makes the regardless-of-boot schedule
set empty by contract, never by assumption. Cover notification persistence
while idle and during an active turn, partial writes
and unknown mechanisms. Notification delay measurements cannot substitute for
current liveness. No current Claude watcher-liveness proof is available through
the permitted channels in this delivery; every potential wait remains pending.
A host-managed waiting mechanism that can start or end without a recognizable
persisted record invalidates affirmative absence for that profile. Keep it
pending and return the concrete in-scope gap to design review. Completed
foreground commands and hooks can detach work without host task records;
requirement Q04=A excludes looking for background descendants. Disclose this
limit, unavailable hook configuration history and undetectable backward clock
changes since boot at activation (Q20=A as qualified by Q21=A). Only Q21's
named boot-instant process metadata is additionally approved; event logs and
other channels remain excluded. All other
profile gates still require disposable validation before either host is supported.

For Codex, validate the identity query on every pinned OS build number,
record the observed update revision, and test runtime build-metadata parsing
and rejection outside the pinned set. Validate the query-rights-only
`VirtualQueryEx` allocation walk and native image-name comparison, including
incomplete walks, missing or ambiguous matches and excluded memory-read paths.
Test the identity query's required process/file access, unavailable/denied calls and every
non-success status. Test directory rename and stale paths, tunneled recreation,
byte-identical copies and another valid pinned release: replacement handles
must fail while the renamed original succeeds at the primitive query. The
full profile still requires its supported path/layout and manifest. Exercise
junction updates, the actual updater's rename and cleanup behavior, old-release
retention or refused deletion, manifest disagreements, both image-name APIs,
same-handle hashing, retained-handle and process races, process restart and
post-delivery version equality. These experiments remain outstanding.
A human owns later live validation under the implementation
plan; this design review performs read-only observations and documents the
required experiments without sending input to existing panes.

The selected final scope remains the whole suite; this design does not claim
an implementation or test pass.

| Confirmed requirement decisions | Design coverage |
| --- | --- |
| Q01, Q17, Q18, Q19, Q21, Q22, Q23, Q27 | Saved assignments, exact takeover, bounded observation and reviewer continuation. |
| Q02, Q03, Q04, Q11, Q12, Q13 | Protected panes, supported profiles, clearing, guarded input and one recovery Enter. |
| Q06, Q07, Q08, Q14, Q25, Q26 | Routing/evidence classification and checkout-wide semantic duplicate detection. |
| Q09, Q10, Q15 | Exact exclusions, per-checkout reporting and exit semantics. |
| Q16, Q20 | Human-only launch, including preview refusal from recognized agent callers. |
| Q24, Q28, Q29 | Scoped marked consent, independent receiver proof and pause-time replacement guard. |
| Q05 | Preserved deferred senv checklist and later-document handoff obligation. |

Requirement Q22=A's reviewer-after-takeover path uses design Q22=A's narrow
exception for validated current-generation requestor starts proved created
after marked resume, with their own lifecycle records. Earlier starts, other
transcripts and recognized reviewer watcher
starts remain in scope; uncertain attribution or ordering stays pending.
Design Q23=A supplies the cleared-requestor path through validated binding of
the marked-input file to the current requestor process, accepting its first
timestamped startup or clear marker under the full item 5 contract. The
reviewer's own complete-generation proof remains required; uncertain requestor
binding stays pending, including on later continuation.

## File-based IO cost clarification for resume-paused

Read the exact artifact-home declaration, prompt/receipt and selected exchange paths, plus the private journal index when needed. Index checkout/pane identities once per observation; avoid broad document or Markdown scans. Full latest-input proof may require reading candidate host session files, so account for bytes read and reject incomplete evidence. The Claude ledger reads every checkout Claude-project transcript active since the last OS boot, the complete relevant generation ranges and all relevant durable schedule definitions regardless of boot at each decision (Q19=A), with all enumeration and record bytes accounted. A Codex image digest is read through the identity-checked handle once per distinct image per invocation; process linkage, the retained-handle identity query and current bindings are still refreshed. Neither result is cached authorization. Re-read mutable prompt, receipt, routing, live pane/input and claim evidence at every safety boundary; never cache it as authorization. The bulk reader writes none of these files. Receiver-only persisted updates retain existing atomic replacement and locked claim semantics.

The Claude history candidate set also validates recorded `cwd` under the path
rules and includes checkout-subdirectory session directories unless validation
excludes their ability to hold a watcher for this checkout. Lossy project names
alone never establish checkout identity. Read and account for Q21=A's boot
process creation metadata, fixed timestamp and uptime comparison. Apply
Q22=A's exception only after reading and classifying the evidence needed for
current-generation ordering and reviewer-watcher recognition; excluded records
still count toward bytes read. Q23=A additionally reads and accounts for the
requestor's current reported session identity, marked-input file and process
creation/stability evidence on initial activation and later continuation.
Neither exception permits skipping required history, schedule definitions or
fresh mutable-binding checks.

The exception removes only starts that validated creation ordering places after
the marked resume input, with those starts' own lifecycle records. File position
alone never places a record after the marker. Terminal, stop and completion
records after the marker still match in-scope starts ordered before it. This
includes any such record the host writes into a later session file after a
clear. A start whose order relative to the marker is uncertain stays in scope.

The ledger parses only classified structural fields in memory: record and
attachment types, tool names, call/result linkage, task ids/statuses, origin
kinds, timestamps, recorded `cwd`, and typed reviewer-entry/watcher-start
matches. It never prints or retains conversation content or tool payloads;
report only counts and classified reasons, including all enumeration/read bytes.

## Design decisions for resume-paused

These are the explicit user decisions reviewed in exchange 1 round 8. Q01-Q14 were
confirmed on 2026-11-09; Q15-Q17 were confirmed on 2026-11-10. Question IDs in
this table refer to this design; the coverage table above refers to the
requirement. The answered questions, options and discussion are preserved in
the pre-consolidation Git snapshot. At consolidation, no further design
question was needed to write the plans. Step 1 feasibility review has since
raised Q18-Q20 below; the user confirmed A for each on 2026-11-12. Their
answers and the resulting contract/plan clarifications require fresh independent
review; this discussion does not authorize their consolidation.
Q19 widens Q17's session-tied Claude read scope, and Q20 limits its
no-background-task criterion to host-managed waiting mechanisms with disclosed
limits; the Q17 row is unchanged. Round 4 identified Q21-Q22 as new decisions
needed for the boot clock boundary and proved requestor work. The user confirmed
A for both on 2026-11-12. Q21 widens Q20's disclosed backward-clock limit to
since boot and selects a fixed boot-process timestamp with detection of net
backward movement where possible. Q22 narrows Q19's absence-check scope only
for the proved requestor's validated current-generation starts proved created
after marked resume and their own lifecycle records,
retaining reviewer watcher starts. Earlier answer records are historical where
these explicit later qualifications apply; all seventeen settled rows remain
unchanged. The new decisions and aligned documents require fresh review and
are not consolidated. Round 6 identified Q23's cleared-requestor binding as a
new human decision. The user confirmed Q23=A on 2026-11-12: the marked-input
file may establish the narrower requestor binding through a validated startup
or clear marker, while the reviewer retains its complete-generation rule.
The decision and aligned documents require fresh independent review; all
profile contracts still require disposable validation.
The evidence gates above still
apply before enabling delivery or claiming release readiness.

Exchange 2 round 5 settled the Codex attribution and Claude lifecycle-evidence
contracts without reopening these decisions. Consolidation was explicitly
authorized on 2026-11-12. Both Codex and Claude remain required; neither profile
is supported yet, and Step 1 remains incomplete. The implementation agent must
revise Step 1 of both plans to these contracts before resuming validation in
disposable sessions. Reviewer observations do not replace that validation.

If validation finds a background mechanism whose start or end lacks a
recognizable record among the mechanisms Q20 places in scope, Claude reviewer
activation remains pending because the
ledger cannot prove that all in-scope waiting work ended. An additional channel
means a specific further source of task-state evidence. The implementation
agent must return the gap to design review with a concrete proposal before
asking the human to approve that source. No unspecified channel is approved,
and this conditional review does not permit shipping only one supported host.

| Question | Decision and rationale | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | B: JSON alone governs bulk routing; render the readable table from it so free prose cannot invent a target. Study legacy conversion separately and preserve installed `tuitp` behavior. | [Saved routing](#saved-routing-and-role-resolution-for-resume-paused), [migration study](#legacy-routing-migration-study), [launcher compatibility](#existing-tuitp-compatibility-and-later-shared-integration). | A: Parsing old tables adds an unsupported prose grammar. Manual resume followed by a fresh pause remains available; conversion is a study, outside bulk execution. |
| Q02 | C: Use one strict compact versioned marker with leading launch id, pane UUID, role and canonical assignment digest. Full typed-command proof remains mandatory; logged prefixes only corroborate it. | [Target-bound consent](#target-bound-consent-for-receiving-resume-workflows). | A: Full encoded JSON is longer and still exceeds truncated logs. B: Named fields add escaping boundaries and input length. Prefix-only proof is insufficient. |
| Q03 | B: Extend the existing receipt and coordination record with non-secret marked bindings and issued generation. Durable evidence supports continuation after log eviction or restart while the claim remains current. | [Takeover and continuation](#takeover-observation-and-later-reviewer-continuation). | A: Pane output alone loses continuation evidence. No separate authorization/continuation file or claim history is added; compatible readers ship together. |
| Q04 | B: Apply the active-reviewer leave-alone check first, then require the marked requestor claim generation still to be current before activation. New claims supersede old proof; current-owner transitions retain it. | [Takeover and continuation](#takeover-observation-and-later-reviewer-continuation). | A: Reconstructing claim lineage depends on volatile output because no durable claim history exists. A competing pickup blocks activation. |
| Q05 | A: Fix delivery/acceptance at 100 seconds and post-acceptance observation at 120 seconds per receiver. Recovery uses only the remaining action budget; tests inject clocks. | [Delivery confirmation](#clearing-and-delivery-confirmation-for-resume-paused), [takeover observation](#takeover-observation-and-later-reviewer-continuation). | B: Human timeout overrides add configuration and reporting complexity; later reviewer-only continuation already handles slow processing. |
| Q06 | A: Select explicit tested profiles from independent pane-tied host/version evidence; absent or ambiguous support fails classification without input. Both hosts must validate before release. | [Profile selection](#clearing-and-delivery-confirmation-for-resume-paused), [validation boundaries](#acceptance-examples-and-validation-boundaries-for-resume-paused). | B: A screen signature alone can hide version-dependent behavior. Codex session-file version evidence after delivery cannot satisfy this earlier gate; failed read-only candidates return to design review. |
| Q07 | A: Use a nonblocking per-checkout OS guard keyed by canonical root, outside the checkout/artifact home. Immediate contention skips preserve independent checkout concurrency. | [Duplicate protection](#duplicate-protection-and-safe-input-eligibility). | B: One command-wide guard blocks unrelated checkouts behind a long action. The guard is not a review lease or an authorization artifact. |
| Q08 | A, qualified to Windows: inspect known agent markers and available process ancestry; reject recognized agents, including preview calls. Unknown origin retains the human-only contract without rejecting ordinary shells solely for missing proof. | [Caller protection](#duplicate-protection-and-safe-input-eligibility). | B: Marker-only detection recognizes fewer agent shell escapes. Lack of a TUIOS pane never proves human origin. |
| Q09 | A: Expose a pure validated review snapshot boundary over existing parsers, without preparation, migration, claims or capabilities. This makes read-only observation explicit and testable. | [Discovery and evidence](#discovery-and-evidence-model-for-resume-paused). | B: A general status launcher needs auditing for hidden preparation and expanded evidence output. |
| Q10 | C: Validate live pane UUID, host, checkout and TUIOS session; an agent session id only supports that identity. Report changed agent ids and revalidate; known conflicts fail, unavailable identity skips. Preserve installed `tuitp` grammars now and full eligible-session coverage in deferred integration. | [Saved target identity](#saved-routing-and-role-resolution-for-resume-paused), [launcher compatibility](#existing-tuitp-compatibility-and-later-shared-integration). | A: An incarnation requirement cannot survive routine clears or current Codex evidence. B: Exact saved context can disappear from a cleared/truncated pane. Restored UUID/session continuity still needs proof. |
| Q11 | A: Revalidate immediately before each protected mutation. A changed selection stops without claiming another exchange; retain truthful completed consumption evidence even if ownership restoration fails. | [Receiving validation](#target-bound-consent-for-receiving-resume-workflows). | B: Consumption-time validation alone leaves digest, routing and pane changes outside the existing claim transaction. The locked round/occurrence check remains required. |
| Q12 | A: Proved acceptance without observed failure may end as in progress with completion unconfirmed for any receiver. Fail observed marker/confirmation errors and unconfirmed delivery; do not equate acceptance with completion. | [Takeover observation](#takeover-observation-and-later-reviewer-continuation), [reporting](#reporting-and-exit-semantics-for-resume-paused). | B: Requiring completion within the observation budget treats slow valid processing as failure; later failures cannot be reported by the ended invocation. |
| Q13 | A: Share a separate read-only agent-callable validator between both receiving workflows. Strict deterministic parsing, current pane/full-input proof, bindings and snapshot checks return typed non-secret evidence or explicit failure. | [Receiving validator](#target-bound-consent-for-receiving-resume-workflows). | B: Instruction-only comparison is not deterministic or directly testable. The validator never consumes, prepares, migrates, claims or returns a capability; the bulk command stays human-only. |
| Q14 | B: Prove Codex complete input through exactly one session file whose latest typed message matches the marked command, checkout and post-delivery time. Tie it to the pane by the fresh unique launch-id prefix followed by `Working`. | [Input proof](#target-bound-consent-for-receiving-resume-workflows), [delivery confirmation](#clearing-and-delivery-confirmation-for-resume-paused). | A: Screen-only reconstruction depends on layout/break rules. C: Mandatory hooks require unproved installation and shared-daemon attribution. Missing/ambiguous file matches fail; Q06 and exact recovery-input gates remain. |
| Q15 | A: Carry the initially proved non-secret Codex session identity and launch id into later calls. Before each protected write, re-prove the same unique file, unchanged latest complete typed command, checkout, live pane UUID/host/session, bindings and snapshot. This preserves proof after the displayed prefix scrolls away. | [Repeated receiving validation](#target-bound-consent-for-receiving-resume-workflows). | B: Re-reading the prefix depends on scrollback depth and new exceptions for old evidence. C: Dropping later pane/input proof weakens the protected claim. Missing/wrong carried values, changes, new input or ambiguity stop the write. |
| Q16 | A: Prove a global wait from the latest reviewer `review-resume` input in this checkout, no later typed input, and current host waiting evidence. Claude needs a still-running same-session watcher started after that input, including after an answer; Codex active turns are already protected. Leave proved waits alone. | [Reviewer classification](#takeover-observation-and-later-reviewer-continuation). | B: Delivering whenever no exact reviewer claim exists can duplicate a running watcher. C: Durable waiter records violate the no-waiter-artifact boundary and can become stale. Uncertain evidence permits no input. |
| Q17 | A: Activate only after positive proof of no wait: Claude session-tied transcript/profile proves no background task remains running, including after restart; Codex fresh supported capture proves idle, empty input and no active turn. Keep current takeover, eligibility and no-resend continuation gates. | [Reviewer activation](#takeover-observation-and-later-reviewer-continuation), [acceptance examples](#acceptance-examples-and-validation-boundaries-for-resume-paused). | B: Requiring no earlier reviewer entry prevents Codex activation under Q14 and limits Claude to fresh conversations. C: Never activating contradicts requirement Q22=A/Q01=D. A proved stopped watcher may activate; missing or ambiguous absence evidence stays pending. |

## Open questions for the v0.14.0 resume-paused design

### Q18: Which Claude hook sources are eligible for positive absence?

Question description: The launcher supplies temporary explicit TUIOS settings
only to its root Claude process. An installed integration can also load into
nested Claude processes, which could report a different session for the same
pane. The recorded command does not distinguish these sources. Which source
scope should this delivery validate? Both hosts remain required; choosing a
scope does not itself validate Claude support. No hook installation has been
authorized.

#### BBQ for Q18

At a barbecue, the host gives the head cook a stamp for the attendance sheet.
If every helper also gets the stamp, a helper can replace the head cook's
entry. We can accept only the host's stamp arrangement, test the helpers'
arrangement in a separate kitchen, or wait until both arrangements are proved.
In this picture: the head cook is root Claude, helpers are nested Claude
processes, the stamp is the TUIOS hook, the attendance sheet is the pane's
reported session, and the separate kitchen is a disposable configuration.

#### Options for Q18

Historical options and recommendation below retain their pre-decision wording.
Q20=A now treats unavailable earlier configuration history as a reported limit;
current source/provenance checks and root/nested discrimination remain required.

- Option A: Accept only launcher explicit settings in this delivery.
  - Pro: Uses the user's existing launcher layout and installs nothing. Root-only settings offer a candidate way to exclude nested reports while installed-integration cases remain pending.
  - Con: Integration-only environments cannot activate. The profile must inspect every documented source, including user, project, local, managed, plugin, skill and subagent hooks, and establish any configuration continuity required by Q20's pending scope decision. Present contents and modification times alone are insufficient: copies or renames can preserve old times, and skill/subagent hooks appear mid-session. No approved source records handler history. Until Q20 is decided, unresolved provenance or other handlers means pending. Widening later needs review.
- Option B: Authorize validation-only integration hooks in a temporary `CLAUDE_CONFIG_DIR`.
  - Pro: Makes the installed-integration and combined-source experiments reachable without editing the user's normal settings.
  - Con: Explicitly authorizes hooks in a disposable profile and may require authentication there. Nested reports still need discrimination, so the integration case could remain pending after testing. This authorizes no production hook installation or new evidence channel.
- Option C: Keep the full source matrix mandatory under the existing authorization.
  - Pro: Preserves equivalent coverage for launcher-only, integration-only, combined and absent sources.
  - Con: Step 1 waits on integration experiments that cannot currently be performed without installing hooks. It offers no shortcut to both-host support.

#### Recommended option for Q18 (with arguments for this choice)

Option A: Validate the existing launcher layout first. Keep installed
integration and unknown provenance pending. Configuration continuity remains
required under the current scope, subject to Q20's explicit decision.
Support still requires the ordering, source-exclusion and complete-persistence
guarantees; a source restriction is not proof of those guarantees.

#### Answer to Q18: option A (confirmed source scope)

The original recommendation proposed A because it targets the actual launcher
layout without authorizing hook installation. The confirmed choice is now
aligned in both plans; validate root-only reporting and every excluded source.
Q20=A makes unavailable earlier configuration history a reported limit, while
remaining in-scope proof gaps keep activation pending and return to review.

User decision: confirmed: option A, existing explicit launcher settings only,
without hook installation. Confirmed by the user on 2026-11-12 with "A".
This matches the existing launcher and keeps integration-only or unknown
source provenance pending. Root-only reporting, nested-session exclusion,
source exclusion, ordering and complete persistence still need validation.
The separately confirmed Q20=A treats unavailable configuration history as a
reported limit. Both plans now reflect the complete Q18-Q20 decision batch.

### Q19: Should Claude absence proof inspect earlier sessions of the checkout?

Question description: A launcher retry, manual restart or another pane can
leave a background command running whose start is in a different transcript.
The writer observed commands surviving forced Claude termination. Reading
only the current session can therefore miss an earlier watcher. Should Q17's
session-tied scope widen to earlier sessions? Option A reads more files of
the existing Claude transcript channel, not a new source type, and needs an
explicit decision because that read scope grows.

#### BBQ for Q19

At the barbecue, a new shift's empty job sheet does not prove that the earlier
shift put out its grills. We can inspect all relevant shifts' sheets, inspect
only shifts since this table was set up, or inspect only the current sheet.
In this picture: shifts are Claude process generations, job sheets are native
session transcripts, burning grills are surviving background work, the table
is the pane shell, and putting out every grill is positive absence proof.

#### Options for Q19

- Option A: Also read every transcript in this checkout's Claude project directory with activity after the last OS boot. Starts recorded before the last boot are ended; durable schedule definitions are not, and stay in scope regardless of boot.
  - Pro: Covers orphaned and other-pane watchers using the approved record type. Ordinary processes from before a true reboot cannot still run; fast-startup shutdown leaves the reported boot time older and widens the scan conservatively.
  - Con: Increases file reads and byte accounting. Unmatched starts can keep the checkout pending until reboot. Reboot does not cancel a restored durable schedule: read its complete relevant definitions, including preboot history, and keep unresolved restoration or coverage pending. Validate file selection and boot semantics; missing history or uncertain activity cannot be skipped as empty.
- Option B: Bound the wider scan by the pane shell's creation time.
  - Pro: Narrows the history and byte cost compared with checkout-wide postboot coverage.
  - Con: Commands can survive their pane shell in a separate console host. This boundary requires proof that no relevant descendant or earlier watcher survives; the writer's forced-exit observation gives no such proof. Until proved, activation remains pending.
- Option C: Keep the current session-only read scope.
  - Pro: Retains the narrowest read scope and current Q17 wording.
  - Con: A clean session after retry or crash cannot exclude orphaned watchers or other-pane work. Under strict positive absence, those unresolved cases must stay pending; treating them as absent could duplicate a watcher.

#### Recommended option for Q19 (with arguments for this choice)

Option A: Widen the existing transcript read scope to cover the observed
cross-session gap. Validate boot and activity boundaries and preserve all
relevant restored-schedule history. This improves coverage without claiming
that classification or reboot alone establishes complete persistence.

#### Answer to Q19: option A (confirmed history scope)

The original recommendation proposed A because a fresh transcript cannot account
for surviving earlier commands. Both plans now include complete reads and byte
accounting for the wider candidate set, conservative handling of missing
history, and preboot definitions for potentially restored schedules. It
qualifies Q17's session-tied read scope and changes no other Q01-Q17 decision.

User decision: confirmed: option A. Confirmed by the user on 2026-11-12
with "A". Read every transcript in this checkout's Claude project directory
with activity after the last OS boot, and complete relevant durable schedule
definitions regardless of boot. This covers surviving earlier-session and
other-pane work through the existing transcript source. Include complete
reads and byte accounting; missing history, uncertain activity or schedule
restoration remains pending. Validate boot semantics, treating fast startup
conservatively. Q20 separately decides the absence guarantee's scope.

### Q20: What does Claude positive absence cover?

Question description: The current strict contract treats any mechanism
without recognizable persisted start/end records as invalidating absence.
A completed foreground command or synchronous hook can detach a process
without a host task record. Requirement Q04=A excludes descendant process
enumeration, and the design excludes command-line inspection. Hook handler
configuration history and a backward clock step between process generations
also have no approved evidence source. Keeping all three as proof obligations
makes Claude reviewer activation unreachable through the approved channels,
the outcome rejected by Q17 option C under requirement Q22=A/Q01=D.
Codex's criterion already covers the host's own idle/input/turn state.
Should Claude absence cover its host-managed waiting mechanisms, keep the
current strict obligations, or require separately proposed named sources?

#### BBQ for Q20

At the barbecue, the cook's job board can track every grill assigned through
the board, but a helper can light a separate grill without adding a ticket.
The board also cannot show who held the chalk earlier or whether the kitchen
clock was reset between shifts. We can certify the board's jobs and disclose
those limits, refuse to certify any shift, or propose extra observation.
In this picture: the job board is Claude's host-managed task ledger, assigned
grills are recorded waiting mechanisms, the helper's separate grill is work
detached by a completed command or hook, chalk history is handler configuration
history, the kitchen clock is the generation timestamp clock, shift
certification is reviewer activation, and extra observation is a named
additional evidence source requiring an explicit decision.

#### Options for Q20

- Option A: Define Claude positive absence over host-managed waiting mechanisms with validated complete start/end persistence.
  - Pro: Makes activation reachable while requiring complete evidence for tasks, `Monitor`, subagents, schedules, wakeups and moved commands. Aligns both hosts with Q17's host-waiting criterion and the user's both-host objective.
  - Con: Processes detached by completed foreground commands or hooks can be missed. Handler configuration history and backward clock steps between generations remain unobservable. Keep each limit visible in the activation report; ownership fencing allows only one claim and lease expiry bounds a stranded claim, but neither proves watcher absence.
- Option B: Retain every current proof obligation, leaving Claude reviewer activation pending in every profile.
  - Pro: Retains the strictest absence contract without accepting the three residual limits.
  - Con: Prevents the required Claude reviewer support through approved sources and effectively selects Q17's rejected never-activate outcome. May require reopening requirement Q22=A/Q01=D and the user's both-host objective.
- Option C: Return separate concrete proposals for named evidence sources covering each residual.
  - Pro: Allows the human to assess a specific source and its coverage before changing the strict obligations.
  - Con: No such source is approved or validated. Descendant enumeration remains excluded by requirement Q04=A, and command-line inspection remains excluded by the design. A time-change event source needs its own proposal and decision; Claude stays pending until every retained obligation is met.

#### Recommended option for Q20 (with arguments for this choice)

Option A: Cover the host's own waiting mechanisms, with validated complete
persistence for each and explicit activation-report limits for detached work,
handler configuration history and cross-generation clock reversal. Require
the reviewer workflow to start watchers only through host background
mechanisms. Optionally reject recorded foreground commands matching a
validated list of detaching launchers as defense in depth, never as proof
that arbitrary detached work is absent. This makes both-host support
reachable without claiming stronger evidence than the approved channels
provide. It still requires disposable validation and all other profile gates.

#### Answer to Q20: option A (confirmed absence scope)

The original recommendation was option A because it preserves a testable host-waiting contract
and exposes the residual limits instead of treating an unobservable condition
as validated. The confirmed choice aligns the contract, Q18's configuration-history
condition and both plans with that scope. Preserve complete persistence,
turn closure, single-writer validation, generation binding and Q19's explicit
history-scope decision. No additional source is approved and no profile
is supported by this decision alone.

User decision: confirmed: A, on 2026-11-12. Positive absence covers Claude-managed
waiting mechanisms with validated complete start/end persistence: background
tasks, Monitor, subagents and their commands, schedules/wakeups and foreground
work moved into background. Reviewer watchers must use host background
mechanisms. Report the three residual limits at activation: detached processes
from completed foreground commands/hooks may be missed; earlier hook-handler
configuration history is unavailable; backward clock changes between process
generations are unobservable. Ownership fencing and lease expiry do not prove
absence. Unknown or incomplete evidence for in-scope mechanisms stays pending.
Both hosts still require disposable validation and all remaining gates. No
new evidence channel is approved. Optional validated detaching-launcher
rejection is defense in depth, never proof of arbitrary detached-work absence.

### Q21: How is the boot boundary protected from wall-clock changes?

Question description: Q19=A selects checkout transcripts with activity since
the last OS boot and discharges ordinary starts before a validated true boot.
Both operations compare wall-clock times. Current time minus uptime moves when
the clock changes: a forward change could discharge still-running work. A boot
instant recorded once at boot avoids that movement, but a later backward clock
change could stamp new work before it. No approved source records clock-change
history. Q20=A accepts an unobservable backward change between process
generations only. How should the boot boundary behave without silently
widening that accepted limit or making Claude activation unreachable?

#### BBQ for Q21

At a barbecue, the cook marks the clock time when the kitchen opens and checks
job tickets against it. Recomputing opening time from today's clock can move
the mark after jobs that are still cooking. Keeping the original mark avoids
that, but turning the clock back can date new tickets before opening. In this
picture: kitchen opening is the true OS boot, the mark is the recorded boot
instant, job tickets are task-start records, cooking jobs are surviving waits,
and moving the clock is a system wall-clock change.

#### Options for Q21

- Option A: Use a boot instant recorded once at boot, never current time minus uptime as the selection boundary. Obtain it from approved process metadata, specifically the creation time of a validated process that starts at boot. Validate that the instant does not move with clock changes. Compare it with current time minus uptime and keep a detected net backward change beyond a validated tolerance pending. Disclose undetectable backward changes since the last boot as part of Q20's clock limit.
  - Pro: Keeps activation reachable while preventing a forward change from moving the boundary past still-running work. Uses a specifically named boot-instant source within process metadata.
  - Con: Widens the disclosed backward-clock limit from between process generations to since boot. Offsetting changes remain undetectable. The boot process, timestamp behavior, uptime semantics, tolerance and fast-startup behavior still require disposable validation; absent or uncertain evidence stays pending. This choice approves only that named boot-instant source, not event logs or another general channel.
- Option B: Treat every possible clock change since boot as uncertain boot semantics and keep Claude activation pending.
  - Pro: Keeps the strictest boot-boundary guarantee without widening the clock limit.
  - Con: No approved source can exclude all such changes, so Claude reviewer activation becomes unreachable, the outcome Q20 rejected. This conflicts with the required both-host objective.
- Option C: Return a concrete proposal for a named clock-change event source, such as Windows System log time-change events.
  - Pro: Could observe clock changes directly and support a stronger boundary contract.
  - Con: Such a source is neither approved nor validated. Its coverage and access need a specific proposal and human decision; Claude remains pending until both approval and validation succeed.

#### Recommended option for Q21 (with arguments for this choice)

Option A: Pin a recorded boot instant, detect net backward movement where
possible and explicitly disclose the remaining backward-clock limitation. This
keeps the both-host objective reachable without claiming approved sources can
observe all clock changes. The named boot-process metadata source and its
semantics still require validation; this recommendation approves nothing.

#### Answer to Q21: option A (confirmed boot-boundary contract)

The original recommendation was option A because a stable recorded boundary
prevents forward clock movement from incorrectly discharging surviving starts,
while an explicit residual limit describes what remains unobservable. The
confirmed choice requires alignment of item 5, validation, IO accounting,
reporting/help, acceptance examples, both plans and the companion before the
follow-up review. No tolerance, concrete boot process or profile is validated
by this decision.

User decision: confirmed: A, on 2026-11-12. Use a boot instant recorded once
at boot from the creation time of a validated process that starts at boot,
within the approved process-metadata channel. Never use current time minus
uptime as the history-selection boundary. Validate that the recorded instant
does not move with clock changes. Compare it with current time minus uptime;
a detected net backward change beyond a validated tolerance keeps activation
pending. Explicitly widen Q20's disclosed clock limitation from backward
changes between process generations to undetectable backward changes since
the last boot, including offsetting changes. The boot process, timestamp
stability, uptime semantics, tolerance and fast-startup behavior still require
disposable validation. Missing or uncertain evidence remains pending. This
choice approves only the named boot-instant metadata source, not event logs
or another general evidence channel. Both hosts and all other gates remain
required; this decision establishes no supported profile.

### Q22: Does checkout history include the proved requestor's work after takeover?

Question description: Q19=A includes every relevant checkout transcript active
since boot. A Claude requestor that proves takeover then starts its own
background wait for the review answer. That unmatched start blocks activation
of its Claude reviewer, whose answer is needed to end the wait. Without an
explicit exclusion, every Claude-requestor/Claude-reviewer pair stays pending
on first activation and later continuation, conflicting with requirement
Q22=A's reviewer-after-takeover behavior. Should only that proved requestor's
new work be excluded, should the command keep all work in scope, or should
the exclusion cover other active Claude panes too?

#### BBQ for Q22

At a barbecue, the head cook waits for the inspector's report, while the
inspector cannot enter until every waiting job is cleared. Counting the cook's
request for that very report makes both wait forever. We can exclude only the
identified cook's new request, keep the strict rule, or exclude other teams'
current jobs too. In this picture: the head cook is the proved requestor, the
inspector is its reviewer, the report request is the background answer wait,
the cleared-job check is positive absence, and other teams are other panes.

#### Options for Q22

- Option A: Exclude only records in the proved requestor pane's validated current generation that the validated ordering contract places after its marked resume input. Earlier records in that transcript and every other transcript remain in scope. A start recognized as reviewer `wait-any-request` still blocks. If the requestor pane's own generation binding cannot be validated, keep the reviewer pending.
  - Pro: Removes the systematic Claude/Claude block using the existing takeover proof. Earlier watcher starts, including a former reviewer's watcher after `--switch-roles`, orphaned work and other panes remain in scope.
  - Con: Requires validated generation binding and ordering in the requestor's own pane as well as the reviewer's. Any ambiguity preserves pending; this narrower exclusion will still let unrelated checkout work block activation.
- Option B: Retain the strict checkout-wide scope with no exclusion and report the blocking requestor wait.
  - Pro: Adds no exception or new attribution dependency.
  - Con: Claude/Claude pairs never activate through this command. The human must resume the reviewer manually, departing from requirement Q22=A for that pairing.
- Option C: Exclude the current generation of every other live, independently identified Claude pane after its latest typed input when that input is not reviewer `review-resume`.
  - Pro: Also prevents unrelated concurrent work in the checkout from blocking reviewer activation.
  - Con: Requires complete typed-input classification and generation binding for every affected pane, adds misattribution risks and exceeds the observed requestor-wait problem. Missing or ambiguous proof must remain pending.

#### Recommended option for Q22 (with arguments for this choice)

Option A: Restrict the exception to the proved requestor's new work after its
marked resume. It resolves the concrete circular wait while retaining earlier
and other-pane evidence and the explicit reviewer-watcher block. It needs
validation and a human choice; reviewer agreement does not authorize it.

#### Answer to Q22: option A (confirmed requestor-work exclusion)

The original recommendation was option A because the proved requestor's answer
wait must not prevent its own reviewer from being resumed. The confirmed
choice requires alignment of item 5, requirement coverage, validation, IO
selection, acceptance examples, both plans and the companion before fresh
independent review. The generation and ordering contracts remain unvalidated.

User decision: confirmed: A, on 2026-11-12. Exclude only records in the proved
requestor pane's validated current process generation that the validated
ordering contract places after its marked resume input. Earlier records in
that transcript and every other transcript remain in scope. A start recognized
as reviewer `wait-any-request` still blocks, including one in the proposed
excluded range. Unknown or ambiguous requestor generation binding or record
ordering keeps the reviewer pending. This exception removes the circular
answer wait without excluding earlier watcher starts, a former reviewer's
watcher after `--switch-roles`, orphaned work or other panes. Both hosts and
all other gates remain required; this decision establishes no supported profile.

### Q23: Which generation binding lets Q22's exception apply to a cleared Claude requestor?

Question description: The command's `--clear` path clears the requestor before
delivering its marked resume. A Claude clear changes the reported session id,
and the new session file starts with a clear SessionStart. Item 1's binding
accepts only startup as the first timestamped marker, so it cannot establish
Q22=A's current-requestor-generation exception after a clear. The requestor's
answer wait then keeps its Claude reviewer pending. A manual clear before the
run has the same problem. Which binding should apply to the requestor's new
work? Q19=A keeps pre-clear transcripts in scope whichever option is chosen.
Under the original startup-only rule, a cleared requestor keeps its reviewer
pending; the confirmed answer below supplies the chosen narrower binding.

#### BBQ for Q23

A cook changes the label on their work station before requesting an inspector's
report. The inspector must establish that the new request came from that same
cook. We can validate the replacement label, accept only the original label,
or skip the requested relabelling. Earlier unfinished jobs still need checking.
In this picture: the cook is the requestor's current Claude process, the label
is its reported session id, relabelling is clear, the report request is the
marked resume and subsequent answer wait, the inspector is the reviewer,
and earlier jobs are starts retained through Q19's pre-clear transcript scope.

#### Options for Q23

- Option A: Bind the requestor's post-marker range through the session file in which acceptance proved its marked resume. On initial activation and later continuation, require identity source `report` for the current session id; a first timestamped record that is the validated TUIOS SessionStart marker for `startup` or `clear`, at or after creation of the requestor shell's single direct Claude child; no later SessionStart other than `compact`; the proved marked input in that file; unchanged process identity across the read; and validated ordering and single-writer behavior. Item 1's complete-generation rule still governs the reviewer's absence proof. Missing or uncertain evidence remains pending.
  - Pro: Claude/Claude pairs resumed with `--clear`, or after a manual clear, can activate their reviewer using only the existing transcript and process-metadata channels. Earlier starts remain in scope.
  - Con: Step 1 must also validate the clear-marker shape, process precedence and matching across session files for task ends from before clear. The timestamp comparison falls within Q21's disclosed clock limitation; the choice itself validates none of these contracts.
- Option B: Apply item 1's startup-only binding to the requestor too.
  - Pro: Adds no binding rule and retains the existing complete-generation condition for both panes.
  - Con: A requestor whose current session began with clear keeps its Claude reviewer pending, including clear from this command's own `--clear`. Those Claude/Claude pairs depart from requirement Q22=A's reviewer-after-takeover behavior.
- Option C: Skip clear for a Claude requestor whose saved counterpart is a Claude reviewer. Deliver resume without clearing and report the skipped clear.
  - Pro: Activation stays reachable without a new binding rule when the retained startup binding and all other gates pass.
  - Con: Overrides the human's explicit `--clear`, and the requestor keeps its previous context. A prior manual clear still lacks the startup-only binding.

#### Recommended option for Q23 (with arguments for this choice)

Option A: Establish the requestor's new-work attribution through the session
file already used for marked-input acceptance, while keeping the reviewer's
complete-generation rule and all earlier starts in scope. This supports the
existing clear option and the both-host objective without another evidence
channel. It requires a human decision and disposable validation.

#### Answer to Q23: option A (confirmed cleared-requestor binding)

The user chose Option A because the requestor's post-marker exception needs
proof of current-process attribution, while Q19 already retains its earlier
work. The clear-marker and stable-process contract can supply that narrower
proof through existing sources if validated. Initial activation and later
continuation require every condition in Option A, conservative pending on
uncertainty, Q22's creation-order and lifecycle matching, and conservative
watcher recognition. The reviewer's complete-generation rule is unchanged.
Item 5, acceptance examples, validation, requirement coverage, IO accounting,
both plans and the evidence companion are aligned for fresh independent review.
The decision establishes no supported profile and authorizes no consolidation.

User decision: confirmed: A, on 2026-11-12. Bind the requestor's post-marker
range through the session file in which acceptance proved its marked resume.
On initial activation and later continuation, require identity source `report`
for the current session id; a first timestamped record that is the validated
TUIOS SessionStart marker for `startup` or `clear`, at or after creation of the
requestor shell's single direct Claude child; no later SessionStart other than
`compact`; the proved marked input in that file; unchanged process identity
across the read; and validated ordering and single-writer behavior. Item 1's
complete-generation rule still governs the reviewer's absence proof. Missing
or uncertain evidence remains pending. Q19=A keeps pre-clear transcripts in
scope, and Q22=A preserves earlier starts, cross-file lifecycle matching and
reviewer-watcher recognition. Step 1 must validate the clear marker, process
precedence and lifecycle matching. Q21=A's disclosed clock limitation still
applies. Both hosts and every other gate remain required; no new evidence
channel, hook installation or supported profile is approved by this decision.
