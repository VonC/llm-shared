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
dated 2026-11-11 and 2026-11-12 findings are reviewer observations and source analysis,
not requestor validation.

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
Claude positive-absence proof depends on the existing `tuitp` launch settings
or an already installed TUIOS integration. The deferred senv effort must
preserve those settings or affected Claude panes remain pending. The shared
command installs nothing and operates independently of the launcher; panes
without either source have no marker and remain pending.
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
absent (Q17=A). For Claude, the transcript tied to the pane's session id must
prove no background task remains running in that session under a validated
profile, including after a host restart. The candidate positive-absence
contract requires all of the following:

1. The transcript covers the complete current generation. The candidate origin
   marker is a recorded `hook_success` for `SessionStart:startup`, observed by
   the reviewer with a TUIOS executable command. It must be the first relevant
   session-start record after process creation, before any background start,
   under a validated source contract tying it to this process and proving
   complete lifecycle coverage. Timestamp proximity and the word `startup`
   alone cannot exclude an earlier session. `clear`, `fork`, unvalidated
   `resume`, an in-process switch, a missing prefix or an ambiguous boundary
   remain pending. The reviewer's 2026-11-11 source analysis traced the command
   to `tuitp`'s generated TUIOS hook settings, passed to Claude via `--settings`
   when that file exists. This is optional launcher behavior. A pane with
   neither those settings nor an installed TUIOS integration has no marker and stays
   pending. Installing a hook is not authorized; reading an existing recorded
   command installs nothing. Validate complete generation/session coverage
   before using the marker.
2. Every background start has a later validated terminal event for the same
   id. The profile must establish complete start/end persistence for every
   enabled background mechanism, not merely pair the events that happened
   to be present. Unrecognized task kinds or record shapes remain pending.
3. No restored or newly created session-scoped scheduled prompt remains
   unexpired, and no background subagent, `Monitor`, PowerShell task, moved
   foreground command or other supported background activity remains running.
   Unknown scheduling or task state remains pending.
4. The file is read completely, without missing bytes or a truncated last
   record. Fresh idle/empty-input evidence and stable session/process binding
   agree with the ledger. Refresh all required state under the execution
   guard immediately before delivery; it is never cached authorization.
5. Earlier-generation tasks are treated as ended only when the pinned host
   profile has validated cleanup for orderly exit, interruption, window close
   and forced termination on the supported platform. Include sessions moved
   to the background and later reattached: their tasks can survive the pane's
   process boundary and must not be counted as ended. General cleanup docs do
   not establish these lifecycle paths. A restarted, backgrounded or reattached
   session remains pending until its task continuity or cleanup is validated.

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

For Claude, establish complete start/end and typed-input shapes for ordinary
completion, explicit stop, host kill, `Ctrl+B` and timeout moves, PowerShell
and Bash tools, `Monitor`, background subagents and their commands, and
compaction. Determine whether subagent commands persist in the main transcript
or only a subagent transcript, and account for complete relevant history.
Exercise clear with running work, fork, orderly exit, launch-time resume,
in-process resume, background sessions, reattach, window close and forced
termination, checking only the disposable process tree. Validate that the
startup marker is the first relevant record of a `tuitp`-launched process
using its generated TUIOS hook settings and covers the complete generation
and session. Also validate an installed TUIOS integration without `tuitp`
settings, and both sources together, including duplicate or merged SessionStart
records. The recorded command cannot distinguish the sources; command-line
inspection is excluded because it reads process memory. Test neither settings
nor integration: no marker means pending. The source finding does not itself
validate that binding or coverage.
Test restored `CronCreate` prompts and scheduled wakeups,
notification persistence while idle and during an active turn, partial writes
and unknown mechanisms. Notification delay measurements cannot substitute for
current liveness. No current Claude watcher-liveness proof is available through
the permitted channels in this delivery; every potential wait remains pending.
A mechanism that can start without a
recognizable persisted record invalidates affirmative absence for that
profile; return the evidence gap to design review rather than guess.

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

## File-based IO cost clarification for resume-paused

Read the exact artifact-home declaration, prompt/receipt and selected exchange paths, plus the private journal index when needed. Index checkout/pane identities once per observation; avoid broad document or Markdown scans. Full latest-input proof may require reading candidate host session files, so account for bytes read and reject incomplete evidence. The Claude ledger reads the complete generation range and relevant restored-schedule history at each decision, with all bytes accounted. A Codex image digest is read through the identity-checked handle once per distinct image per invocation; process linkage, the retained-handle identity query and current bindings are still refreshed. Neither result is cached authorization. Re-read mutable prompt, receipt, routing, live pane/input and claim evidence at every safety boundary; never cache it as authorization. The bulk reader writes none of these files. Receiver-only persisted updates retain existing atomic replacement and locked claim semantics.

## Design decisions for resume-paused

These are the explicit user decisions reviewed in exchange 1 round 8. Q01-Q14 were
confirmed on 2026-11-09; Q15-Q17 were confirmed on 2026-11-10. Question IDs in
this table refer to this design; the coverage table above refers to the
requirement. The answered questions, options and discussion are preserved in
the pre-consolidation Git snapshot. No further design question is needed to
write the implementation and validation plans. The evidence gates above still
apply before enabling delivery or claiming release readiness.

Exchange 2 round 5 settled the Codex attribution and Claude lifecycle-evidence
contracts without reopening these decisions. Consolidation was explicitly
authorized on 2026-11-12. Both Codex and Claude remain required; neither profile
is supported yet, and Step 1 remains incomplete. The implementation agent must
revise Step 1 of both plans to these contracts before resuming validation in
disposable sessions. Reviewer observations do not replace that validation.

If validation finds a background mechanism whose start or end lacks a
recognizable record, Claude reviewer activation remains pending because the
ledger cannot prove that all background work ended. An additional channel
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
