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

These facts describe the checkout at `518080e`, before runtime implementation.

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
before the write. Later calls keep Q11's and Q13's pane and input proof.

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
justify the pre-delivery profile selection. Within the confirmed choices,
the candidate Codex sources before input are the version banner in that
pane's attributable scrollback and process metadata tied to that pane's own
process. The first implementation step validates one of them read-only. If
neither validates, the work returns to design review; it does not ship one
host or add hooks silently. Requiring hooks for version evidence would need
the user to reopen Q14=B. Missing unique profile/version evidence is reported
as unsupported evidence and a classification failure under confirmed Q06=A,
without input. Codex new-conversation syntax must be confirmed for the
supported version before enabling that profile's clear action; do not try
alternate commands in a live pane to discover it.

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
An `ok` result or idle status alone is insufficient. Bound the delivery and
acceptance observation by 100 seconds per action, including any recovery;
the transport's stall bound remains 60 seconds.
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
agree. Confirmed Q16=A proves a global reviewer wait, which is not bound to
one exchange, from the pane's complete-input channel and current host waiting
evidence, and leaves a proved waiting reviewer alone. Q17 defines the evidence
that no wait is running; only then deliver the target host's marked
`review-resume as reviewer` for the exact selection, preserving its conversation
and normal claim workflow. Any other case is incomplete evidence: send no
input and report the reviewer pending with the reason. A shell is never a
counterpart. A background-shell indicator alone is not reviewer proof.
Confirmed Q17=A permits activation when current host evidence proves no wait
is running; missing or ambiguous evidence still permits no input.

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
| A Claude reviewer's watcher, restarted after an answer, still runs after its typed `review-resume` | Leave it untouched (Q16). |
| Reviewer evidence neither proves a wait nor shows that none is running | Send no input; report the reviewer pending with the reason (Q16). |
| Reviewer evidence shows that no wait is running (Q17=A) | Deliver the marked reviewer resume after takeover proof, eligibility checks and later-continuation rules; never resend uncertain prior delivery. |
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

## Open questions for the v0.14.0 resume-paused design

These questions concern design choices proposed above. Recommendations and
answer text remain proposals unless an explicit user decision is recorded
below. They do not reopen the requirement's 29 confirmed choices.

### Q01: Routing representation and compatibility boundary

How should versioned JSON coexist with the unreleased branch routing table without interpreting incomplete prose as a target? The canonical main template has no routing section; no released format needs table compatibility. Its branch table cells are free prose rather than a strict grammar.

#### BBQ for Q01

A dispatch card can have a printed form and a machine label. In this picture: the card is the pause prompt, the printed form is the existing routing table, and the label is the versioned JSON block.

#### Options for Q01

- Option A: Use JSON as authoritative for new captures; accept the existing table only through one documented complete grammar, and reject conflicting duplicate values.
  - Pro: Keeps already complete saved handoffs usable and gives future readers a stable contract.
  - Con: Requires compatibility parsing and clear equivalence checks.
- Option B: Require the JSON block for bulk routing; keep older table-only handoffs manual.
  - Pro: Creates one strict parsing surface.
  - Con: Table-only handoffs created from the unreleased branch template need ordinary manual resume.

#### Recommended option for Q01

Option B: One authoritative JSON block avoids inference from an unreleased prose table. The writer initially recommended A; the round 1 reviewer recommended B, and the writer adopts that proposal after checking the canonical main template. Neither recommendation is a user decision.

#### Answer to Q01: option B

Option B: Require the JSON block for bulk routing, render the table from it, and keep table-only or routing-free handoffs manual. This avoids interpreting unreleased prose as routing.

User decision: confirmed: B, on 2026-11-09.

User comment: Study a way to migrate older tables to the new format before
eventual tool use, and examine whether the format interferes with `tuitp`'s
default resume commands or its later reuse of the shared tool. The migration
study and launcher compatibility analysis above record these requests.
Conversion remains a proposal outside bulk execution; separate senv
integration remains deferred under requirement Q05=A.

### Q02: Marker transport contract and parser limits

Should launch consent use a full encoded marker, named plain-text fields or a compact scope binding? All choices must bind the exact digest, independently proved receiver, assignment and exchange. The current Claude prompt log retains only 100 characters and may mask text; Codex wraps long input. A launch-id prefix alone does not satisfy the confirmed exact-command proof requirement.

#### BBQ for Q02

A delivery note can be one sealed packet or several labeled cards. In this picture: the packet is the encoded marker, the cards are named marker fields, and the destination is the receiving pane and role.

#### Options for Q02

- Option A: Use one versioned base64url JSON marker with strict fields, duplicate-key rejection and a documented size bound validated before any delivery.
  - Pro: Moves paths, labels and exchange identity without whitespace ambiguity.
  - Con: Needs decoding, makes raw input harder to inspect and cannot be verified in full through the truncated Claude log alone.
- Option B: Use separate named fields with one canonical escaping grammar and the same validation rules.
  - Pro: Makes individual bindings visible in terminal input.
  - Con: Introduces more quoting boundaries and longer command syntax.
- Option C: Use one strict compact versioned marker containing launch id first, receiving pane UUID, role and a SHA-256 binding over the canonical complete assignment. Recompute the binding from independently observed pane identity, saved routing and live exact exchange. Require full-command capture or pane-bound transcript proof as well as the profile's logged prefix.
  - Pro: Reduces input length and keeps the correlation id inside the measured logged prefix while retaining all scope bindings.
  - Con: Does not make the full marker fit a 100-character log. Requires a tested complete-input channel and canonical reconstruction; a mismatch cannot identify the differing field from the marker alone.

#### Recommended option for Q02

Option C: The writer initially recommended A; the reviewer proposed C after measuring truncation. The writer adopts C with an explicit full-command proof gate. Prefix-only consent is rejected because it would weaken the confirmed requirement. No host profile is enabled until complete proof and canonical binding reconstruction are validated.

#### Answer to Q02: option C

Option C: Use a compact versioned marker with a leading launch id, receiving pane UUID, role and canonical assignment binding. Full typed-command proof remains mandatory; logged prefixes only corroborate it. Both workflows use the same strict validator.

Q14 selects the Codex complete-input channel. Pane-level `--unwrap` alone is
insufficient for this option's full-command proof gate.

User decision: confirmed: C, on 2026-11-09.

### Q03: Persistence of non-secret takeover evidence

A later invocation needs pane-specific claim evidence that the current coordination record does not contain. Should receiving workflows emit the proposed structured result in existing pane output, or extend existing durable resume evidence?

#### BBQ for Q03

A dispatcher needs proof that the assigned driver collected a parcel. In this picture: the driver is the receiving pane, the parcel is the exact pause, and the collection slip is the non-secret takeover result.

#### Options for Q03

- Option A: Emit structured results in existing pane output and reconstruct continuation only while attributable output and protocol evidence remain available.
  - Pro: Adds no durable continuation file or new receipt schema.
  - Con: Claude logs retain 256 entries in daemon memory, with prompt text capped at 100 characters; active observed panes approach capacity within about an hour. Eviction or daemon restart can prevent the required later continuation.
- Option B: Extend the existing receipt with launch id, pane and assignment binding through a new schema, and atomically record the same non-secret marked-claim binding and issued generation in the current coordination record. Receiving workflows alone write them; no claim history is assumed.
  - Pro: Allows later continuation when pane history is no longer available.
  - Con: Expands durable schemas and marked-claim inputs, with legacy parsing and receipt-before-claim ordering. A superseding claim must invalidate the old takeover binding.

Older llm-shared readers reject the new coordination fields or receipt schema;
the installed `tuitp` stays compatible through the preserved receipt lines.
The marked route ships only with every affected llm-shared reader updated.

#### Recommended option for Q03

Option B: The writer initially recommended A; the reviewer recommended revised B because volatile output cannot reliably support later continuation. The writer adopts B. Binding fields contain no token or token digest; the existing coordination token digest is not removed or duplicated. This adds no authorization or continuation file.

#### Answer to Q03: option B

Option B: Put non-secret launch/pane/assignment bindings in the existing receipt and marked claim's coordination record, with the issued generation. The bulk reader stays read-only, and later continuation survives volatile evidence loss while that claim remains current.

User decision: confirmed: B, on 2026-11-09.

### Q04: Takeover proof after normal protocol progress

What establishes that the selected requestor restored ownership after protocol progress? Generations advance only for newly issued claims, including a counterpart's wait claim; transitions by the current owner retain them. No durable claim history exists. Apply the exact active-reviewer leave-alone check first.

Confirmed Q16=A separately defines how the leave-alone check proves a global
reviewer wait, and confirmed Q17=A defines when a wait is excluded; neither
changes the confirmed generation rule.

#### BBQ for Q04

An inspector may arrive after a relay baton has already moved onward. In this picture: the baton is review ownership, the runner is the selected requestor, and the handoff record is exact-exchange claim evidence.

#### Options for Q04

- Option A: Correlate the pane result and claim generation with read-only exact-exchange transition evidence; accept later progress only when that lineage is demonstrated.
  - Pro: Supports quick legitimate progress while preserving pane-specific proof.
  - Con: No durable transition/claim history exists, so lineage would depend on volatile pane output and disappear after eviction.
- Option B: Require the selected requestor claim generation still to be current when the tool observes it.
  - Pro: Keeps the proof comparison simple.
  - Con: A newer claim blocks activation. An already active reviewer is handled first by the leave-alone check; a competing pickup correctly prevents using the earlier requestor claim.

#### Recommended option for Q04

Option B: The writer initially recommended A; the reviewer recommended B after checking generation issuance and the absence of history. The writer adopts B: current-owner transitions retain the generation, newly issued claims advance it, active reviewers are left alone first, and competing pickups must block activation.

#### Answer to Q04: option B

Option B: Apply the active-reviewer leave-alone check first, then require the selected requestor's durably bound claim generation still to be current before any reviewer activation. Current-owner transitions retain that proof; a newly issued claim supersedes it.

User decision: confirmed: B, on 2026-11-09.

### Q05: Observation and delivery time budgets

The design proposes a 100-second action budget and a separate 120-second receiving-result/takeover budget. Should these be fixed supported defaults or configurable human launch settings?

The delivery call can exhaust its 100 seconds. Under either option recovery and acceptance checks use only the remaining action budget; no remaining time means unconfirmed delivery without recovery. The 120-second observation bound applies independently to each accepted receiver, including an activated reviewer.

#### BBQ for Q05

A station has separate clocks for dispatch and arrival. In this picture: dispatch is command acceptance, arrival is receiver/takeover evidence, and the clocks are their observation budgets.

#### Options for Q05

- Option A: Use documented fixed defaults of 100 seconds for delivery/acceptance and 120 seconds after acceptance, with injected clocks for tests.
  - Pro: Keeps the CLI small and outcomes predictable across checkouts.
  - Con: Slow receivers may need a later reviewer-only continuation.
- Option B: Keep those defaults but offer bounded timeout overrides as additional human CLI options.
  - Pro: Accommodates different host speeds without changing code.
  - Con: Adds public configuration and makes timing reports more complex.

#### Recommended option for Q05

Option A: The required CLI already supports later continuation; fixed bounds avoid another tuning surface.

#### Answer to Q05: option A

Option A: Use documented fixed defaults of 100 seconds for delivery/acceptance and 120 seconds after acceptance, with injected clocks for tests. The required CLI already supports later continuation; fixed bounds avoid another tuning surface.

User decision: confirmed: A, on 2026-11-09.

### Q06: Supported host profile selection

Fresh Codex readiness and clear confirmation depend on version-specific screen behavior that has not been validated here. How should a runtime select a supported profile without probing commands in a live pane?

TUIOS discovery supplies no Codex version. Option A needs a version banner or process metadata independently tied to the target pane; the caller's CLI version does not prove it. Without such evidence A fails classification for that target, even when its pane appears usable. This consequence is stated explicitly, not silently changed to a skip; both host profiles must work before release.

Q14 option B confirms session-file `cli_version` after delivery, too late to
select the profile for that delivery. Within the confirmed choices, validate
the version banner in that pane's attributable scrollback or process metadata
tied to its own process read-only in the first implementation step. If neither
validates, return to design review before release; do not ship only one host
or add hooks silently. Mandatory hooks for version evidence would require the
user to reopen Q14=B. Q14 option B does not itself remove this evidence gap.

#### BBQ for Q06

A mechanic selects the correct instrument chart before reading a dashboard. In this picture: the chart is a host profile, the dashboard is the captured screen, and the vehicle identity is observed host/version evidence.

#### Options for Q06

- Option A: Select from explicit tested profiles using independent host/version evidence and fail classification when no unique compatible profile is established.
  - Pro: Makes supported readiness and clear behavior auditable and prevents live command probing.
  - Con: New or undatable versions, including observed Codex panes lacking version evidence, fail classification until a uniquely supported profile is proved.
- Option B: Select by a unique tested screen signature even when the exact version cannot be established, with the same failure on ambiguous signatures.
  - Pro: Can support unchanged interfaces across more versions.
  - Con: Visually similar versions can hide behavioral changes, especially around clearing.

#### Recommended option for Q06

Option A: Conservative profile selection fits the requirement to verify the Codex signature in use.

#### Answer to Q06: option A

Option A: Select from explicit tested profiles using independent host/version evidence and fail classification when no unique compatible profile is established. Conservative profile selection fits the requirement to verify the Codex signature in use.

User decision: confirmed: A, on 2026-11-09.

### Q07: Cross-invocation execution guard scope

The draft uses a per-checkout OS execution guard to stop cooperating launches passing the same fresh checks simultaneously. Should that guard be per checkout or command-wide?

Either guard uses an OS named lock or a root-digest-keyed lock file in the user's temporary directory, never the checkout or its artifact home. This preserves the no-checkout-writes boundary.

#### BBQ for Q07

Two dispatchers must not both send a driver to collect the same parcel. In this picture: dispatchers are concurrent invocations, the parcel is one checkout's pause, and the dispatch lock is the execution guard.

#### Options for Q07

- Option A: Use a nonblocking per-checkout OS guard keyed by canonical root, with a host-specific lock provider and an immediate contention skip.
  - Pro: Prevents cooperating duplicate delivery while preserving independent checkout concurrency.
  - Con: Needs equivalent lock semantics on each supported operating system.
- Option B: Use one command-wide OS guard while retaining concurrent checkout workers inside its holder.
  - Pro: Makes coordination between separate invocations simpler.
  - Con: An unrelated long-running checkout prevents every other launch from proceeding.

#### Recommended option for Q07

Option A: Its scope matches the protected resource and the requirement to let independent checkouts proceed.

#### Answer to Q07: option A

Option A: Use a nonblocking per-checkout OS guard keyed by canonical root, with a host-specific lock provider and an immediate contention skip. Its scope matches the protected resource and the requirement to let independent checkouts proceed.

User decision: confirmed: A, on 2026-11-09.

### Q08: Human caller evidence outside TUIOS

The human-only contract also applies outside TUIOS, where absence of a pane cannot prove a human launch. What additional caller evidence should the implementation inspect without pretending to establish certainty it does not have?

#### BBQ for Q08

A desk can reject a known automated courier without identifying every visitor. In this picture: the courier is an agent caller, the desk is the launch guard, and visitor identity is available process/host evidence.

#### Options for Q08

- Option A: Inspect known agent host markers and process ancestry where available, reject recognized agents, and document the remaining human-only contract when origin cannot be proved.
  - Pro: Strengthens refusal outside TUIOS without blocking ordinary human shells merely because proof is unavailable.
  - Con: Cannot reliably identify every possible agent-origin process.
- Option B: Use recognized TUIOS caller classification and explicit agent host markers only, retaining the outside-TUIOS contract.
  - Pro: Avoids dependence on platform-specific process inspection.
  - Con: Recognizes fewer agent shell escapes when their markers are absent.

#### Recommended option for Q08

Option A: It improves enforceable caller refusal while stating the limits accurately and retaining normal outside-TUIOS use.

#### Answer to Q08: option A

Option A: Inspect known agent host markers and process ancestry where available, reject recognized agents, and document the remaining human-only contract when origin cannot be proved. It improves enforceable caller refusal while stating the limits accurately and retaining normal outside-TUIOS use.

User decision: confirmed: A, on 2026-11-09.

User qualification: Platform Windows. Apply the host-marker and available
process-ancestry checks on Windows; the human-only rule and its stated
detection limits remain unchanged.

### Q09: Read-only review state interface

Takeover and active-reviewer proof require strict exchange classification. Should the bulk tool call a dedicated read-only snapshot interface or invoke an existing status launcher and parse its output?

#### BBQ for Q09

A visitor needs to read a control panel without touching its controls. In this picture: the visitor is the bulk observer, the panel is exchange state, and the controls are migration, preparation and ownership operations.

#### Options for Q09

- Option A: Expose a pure validated snapshot boundary using existing artifact parsers, with no home preparation, migration, claim or capability output.
  - Pro: Makes the no-write contract explicit and keeps unsafe operations outside observation.
  - Con: Requires a clearly maintained boundary around shared review classification.
- Option B: Use a documented read-only status launcher contract that returns all required non-secret snapshot evidence.
  - Pro: Reuses an established process interface and JSON result.
  - Con: The launcher contract must be audited for hidden preparation and expanded where pane/claim evidence is absent.

#### Recommended option for Q09

Option A: A pure snapshot boundary is easier to verify against the bulk reader's strict side-effect limits.

#### Answer to Q09: option A

Option A: Expose a pure validated snapshot boundary using existing artifact parsers, with no home preparation, migration, claim or capability output. A pure snapshot boundary is easier to verify against the bulk reader's strict side-effect limits.

User decision: confirmed: A, on 2026-11-09.

### Q10: Evidence that a saved pane id still names the same agent

Which independent observation defines continuity of a saved target? TUIOS pane ids are UUIDs; practical reassignment means a changed host, checkout or TUIOS session. Claude clears create a new agent session, including this tool's own clear; Codex exposes no agent session id in the observed build.

A saved UUID missing from discovery, or listed without an agent, is absent
and skips. A different live agent host is a known conflict and fails.

#### BBQ for Q10

A room number is not proof that the same person still occupies it. In this picture: the room number is the pane id, the occupant is the agent instance, and the check-in record is log/session identity evidence.

#### Options for Q10

- Option A: Record an observed agent/session incarnation or start/log identity when available and validate it with current independently attributable evidence; report unknown identity without substituting a pane.
  - Pro: Distinguishes stable pane location from actual agent continuity.
  - Con: TUIOS or a host may not expose enough evidence, causing an unresolved-target skip.
- Option B: Require current pane content to identify the exact saved pause/assignment as continuity evidence, in addition to live pane and host matching.
  - Pro: Can work without a dedicated agent incarnation identifier.
  - Con: Cleared or truncated content may remove the proof, and quoted old context must be excluded.
- Option C: Use the live pane UUID, host, checkout and TUIOS session as target identity, with an agent session id as supporting evidence. Report a changed agent session id alone, then revalidate all current protections. Known host/checkout/session conflicts fail classification; unavailable identity is an unresolved-target skip.
  - Pro: Survives routine clears and supports Codex without an agent session id, without choosing another pane.
  - Con: Treats a same-host restart in the same pane as the same target. UUID uniqueness across restored TUIOS sessions must be verified before enabling that profile.

#### Recommended option for Q10

Option C: The writer initially recommended A; the reviewer proposed C because A cannot survive ordinary clears or current Codex evidence. The writer adopts C while retaining the confirmed classification failure for known conflicting identities, rather than the reviewer's suggested skip for reassignment. No routing or input-protection requirement is waived.

#### Answer to Q10: option C

Option C: Validate the live pane UUID, host, checkout and TUIOS session. An agent session id is supporting evidence; a changed id alone is reported and revalidated. Known reassignment fails classification, unavailable identity skips, and restored-session UUID behavior must be validated.

User decision: confirmed: C, on 2026-11-09.

User qualification: Make sure `tuitp` keeps working and can resume all
eligible sessions. The integration completion and coverage conditions above
record this requirement. This delivery preserves the installed launcher's
prompt and receipt grammars, validated by fixtures. Resuming all eligible
sessions through the shared interface remains the deferred senv completion
condition under requirement Q05=A. Neither condition relaxes saved-target
validation. Runtime compatibility remains to be demonstrated.

### Q11: Revalidation between prompt consumption and role claim

A marked requestor can write its receipt before the review claim. How should the receiving workflow handle the prompt or selected exchange changing between those actions?

The existing `claim_selected` transaction rejects a changed round or occurrence under its transition lock. Q13's shared validator additionally rechecks digest, routing and receiving pane immediately before the claim; it does not replace that lock.

#### BBQ for Q11

A collection receipt does not permit picking a different parcel if the shelf changes. In this picture: the receipt is prompt consumption, the shelf is live exchange state, and collection is the exact role claim.

#### Options for Q11

- Option A: Revalidate marker bindings immediately before each protected mutation; stop a changed selection without claiming another exchange and retain truthful completed consumption evidence.
  - Pro: Preserves the exact launch scope and records what actually happened.
  - Con: A consumed pause can remain without restored ownership and need explicit diagnosis.
- Option B: Validate all bindings immediately before consumption and treat the already selected claim transaction as the only later check.
  - Pro: Keeps fewer receiving-workflow checks outside the claim transaction.
  - Con: The transaction must also receive enough digest and routing context to reject a replaced prompt, which it currently lacks.

#### Recommended option for Q11

Option A: It applies the target binding across both receiving actions while keeping normal protocol locking responsible for the claim.

#### Answer to Q11: option A

Option A: Revalidate marker bindings immediately before each protected mutation; stop a changed selection without claiming another exchange and retain truthful completed consumption evidence. It applies the target binding across both receiving actions while keeping normal protocol locking responsible for the claim.

User decision: confirmed: A, on 2026-11-09.

### Q12: Receiver completion evidence at the observation deadline

After accepted delivery, a single agent, resumed requestor or activated reviewer may still be processing when its 120-second observation ends. How should the report distinguish that from a proved marker/confirmation failure or unconfirmed delivery? The same rules apply to every accepted receiver; reviewer acceptance alone never proves completion.

#### BBQ for Q12

A courier can acknowledge departure before reaching the destination. In this picture: departure is accepted resume input, arrival is completed resume evidence, and the tracking deadline is the observation bound.

#### Options for Q12

- Option A: Report accepted/in progress with completion unconfirmed when acceptance is proved and no explicit failure is observed; fail observed marker/confirmation errors and all unconfirmed deliveries.
  - Pro: Keeps acceptance, processing and completed recovery distinct without waiting indefinitely.
  - Con: A failure arising after the observation deadline cannot be included in that invocation's result.
- Option B: Require a structured receiving-workflow success or failure result within the observation budget and fail a missing result.
  - Pro: Gives every successful invocation positive receiver completion evidence.
  - Con: Treats slow processing as failure even when delivery was accepted and no automation failure is observed.

#### Recommended option for Q12

Option A: It preserves bounded observation without claiming completion that has not been proved; the reported limitation remains visible.

#### Answer to Q12: option A

Option A: Report accepted/in progress with completion unconfirmed when acceptance is proved and no explicit failure is observed; fail observed marker/confirmation errors and all unconfirmed deliveries. It preserves bounded observation without claiming completion that has not been proved; the reported limitation remains visible.

User decision: confirmed: A, on 2026-11-09.

### Q13: Receiving-side marker validation surface

Both receiving workflows must decode the marker, independently prove their pane and full typed input, and recheck bindings before receipt or claim. The human-only `resume_paused` refuses agent callers and cannot be their validation command. Where should these deterministic checks run?

#### BBQ for Q13

A courier checks a parcel seal with the depot scanner instead of by eye. In this picture: the seal is the marker, the scanner is a shared validator, the parcel destination is the resolved assignment, and checking by eye is instruction-only validation.

#### Options for Q13

- Option A: Add a separate read-only, agent-callable validator launcher shared by `resume-session` and `review-resume`. It strictly parses the marker, recomputes canonical bindings, reads independent pane/full-input evidence and a pure exchange snapshot, and returns typed non-secret JSON without writes or capabilities.
  - Pro: Gives both hosts and workflows one testable contract; Q11's rechecks use the same surface before each protected mutation.
  - Con: Adds a public launcher whose validation-only boundary must stay separate from the human-only bulk command.
- Option B: Validate through instructions only, asking the receiving agent to decode the marker and compare evidence.
  - Pro: Adds no executable surface.
  - Con: Strict parsing and binding comparison depend on model reasoning and cannot be covered by deterministic fake-TUIOS tests.

#### Recommended option for Q13

Option A: The reviewer identified the missing receiving validation surface, and the writer agrees. Shared deterministic checks make strict consent and mutation revalidation testable without authorizing agent calls to the bulk launcher.

#### Answer to Q13: option A

Option A: Add a separate read-only, agent-callable validator for both receiving workflows. It returns validated scope and evidence or an explicit failure, performs no receipt or claim itself, and keeps the bulk command human-only.

User decision: confirmed: A, on 2026-11-09.

### Q14: Codex complete-input proof channel

Q02 requires proof of the complete marked command. `capture-pane --unwrap`
joins only rows wrapped by the pane; a host's own layout breaks remain.
Observed Codex panes report no conversation id. How should the Codex receiver
and bulk observer prove the complete typed command?

The metadata check confirms session identity, checkout, timestamp and
`cli_version` fields. It does not validate a complete-input profile. Every
option must prove the latest typed user input, exclude notifications and
quoted older commands, and reject unavailable or ambiguous evidence. No
option permits live input experiments during this design review.

#### BBQ for Q14

A depot can read a long address from a folded label or look the parcel up in
its ledger by tracking number. In this picture: the label is the Codex screen,
the ledger is the session file, and the tracking number is the unique launch
id. The ledger still needs evidence tying that parcel to the intended desk.

#### Options for Q14

- Option A: Reconstruct the complete command from the screen with a tested Codex layout profile covering prompt prefix, indentation and break rules. Use `--unwrap` only for pane-level wraps.
  - Pro: Evidence comes directly from the target pane without reading host conversation files.
  - Con: Rendering changes can break reconstruction, and breaks at spaces remain ambiguous unless the profile proves exact preservation.
- Option B: Find exactly one Codex session file whose latest typed user message equals this delivery's complete marked command, in the same checkout and recorded after delivery. Tie it to the target pane through the displayed command prefix containing that command's unique launch id, followed by `Working`.
  - Pro: Preserves complete input without screen reconstruction or required hook installation. The same file can confirm `cli_version` after delivery.
  - Con: Adds session-file location, format and user-input classification to the profile. The pane tie depends on the fresh unique launch id rather than a pane-reported conversation id; ambiguous matches fail. Files hold whole conversations, so read only defined fields in memory and never expose their contents. Version evidence after delivery cannot satisfy Q06's pre-delivery gate.
- Option C: Require validated TUIOS Codex hooks to report the pane's conversation id, then read that exact session file for complete typed-input proof.
  - Pro: Gives a direct pane-to-session association and can supply `cli_version` before delivery from an existing session.
  - Con: Requires machine setup absent here, and hook attribution under the shared app-server must be proved independently of inherited pane variables. Session-file parsing remains necessary.

#### Recommended option for Q14

Option B: The round 2 reviewer proposed B, and the writer adopts it as the
proposed channel after checking metadata and capture limits. It preserves
exact complete-input proof without mandatory hook setup. Q06's independent
pre-delivery version evidence remains required, and an unsubmitted command
still needs exact input-box reconstruction for the single recovery Enter.
This recommendation does not establish a validated host profile. The user's
decision is recorded below.

#### Answer to Q14: option B

Option B: Prove the full Codex command from one uniquely matching session
file's latest typed user input, tied to the intended pane by the fresh launch
id in its displayed command prefix followed by `Working`. Require matching
checkout and post-delivery time; fail missing or ambiguous proof. Keep Q06's
pre-delivery version gate and the separate exact input-box recovery gate.

User decision: confirmed: B, on 2026-11-09.

### Q15: Codex receiving-pane proof at later protected writes

Q13 makes the receiving validator prove the current pane and input before each
protected write or claim. Q14 ties a Codex session file to its pane through the
displayed command prefix holding the launch id, followed by `Working`. That
screen evidence lasts only while the submitted command is still on screen,
while the session file's latest typed user message lasts until new input
arrives. What must later validator calls in the same receiving turn prove?

#### BBQ for Q15

A depot checks a courier at the gate, then checks the same parcel number at
each later door. In this picture: the gate check is the first validation with
the displayed prefix, the parcel number is the matched session file and launch
id, and the later doors are the receipt and claim writes.

#### Options for Q15

- Option A: The first validation proves the full Q14 tie and returns the matched session identity and launch id as non-secret evidence. The receiver passes them to later calls. Each later call requires the same unique session file, its latest typed user message still exactly equal to the marked command, the same checkout, and the same live pane UUID, host and TUIOS session. It also recomputes the bindings and the exchange snapshot. Any change, new typed input or ambiguity stops before the write.
  - Pro: The pane tie is proved once from fresh evidence, and every later check uses evidence that lasts through the turn.
  - Con: Later calls depend on values the receiver supplies from its own context. A wrong or missing value has to fail closed, and tests must cover it.
- Option B: Every call re-proves the displayed prefix and `Working`, accepting attributable scrollback that holds this launch id under a tested profile rule.
  - Pro: Each call stands alone on screen evidence.
  - Con: It depends on scrollback depth and layout, needs an exception to the rule that older scrollback grants nothing, and a long turn can still lose the line.
- Option C: Only the first validation proves pane and input. Later calls recheck digest, routing and exchange bindings only.
  - Pro: Simplest validator contract.
  - Con: It drops the pane and input proof at the claim, the write that Q11 protects most, and leaves Codex weaker than Claude, whose transcript lasts.

#### Recommended option for Q15

Option A: The round 4 reviewer proposed A, and the writer agrees. It keeps
Q13's pane and input proof at every protected write using evidence that lasts
through the turn, without screen re-reading or hooks. The initial pane tie
still comes from Q14's fresh launch-id prefix. The carried values hold no
capability or conversation content.

#### Answer to Q15: option A

Option A, confirmed by the user: retain the initially proved session identity
and launch id as non-secret evidence for later validator calls. Re-prove the
same unique file, unchanged latest complete typed command, checkout, live pane
UUID, host and TUIOS session, and current bindings and exchange snapshot
before each protected write. Missing or wrong carried values, changed evidence,
new typed input or ambiguity stop before the write.

Rationale: retain evidence that lasts through the receiving turn while
preserving Q11's revalidation and Q13's pane and input proof. The first pane
tie still requires Q14's fresh displayed launch-id prefix followed by
`Working`; this decision does not relax Q06's pre-input version gate.

User decision: confirmed: A, on 2026-11-10.

### Q16: Proof that a reviewer is already waiting

Requirement Q22=A leaves a reviewer already serving or waiting on the exact
exchange untouched, and design Q04=B runs that check first. A reviewer in
`wait-any-request` waits for any request and leaves no durable protocol record.
In Claude it shows an idle pane with a background watcher. What positive
evidence proves that a reviewer pane is already waiting, and what does the
tool do when that proof is unavailable?

#### BBQ for Q16

A dispatcher must not call a driver already parked at the depot waiting for
loads. In this picture: the parked driver is a reviewer in a global wait, the
depot is the artifact home, and the call is the marked reviewer resume.

#### Options for Q16

- Option A: Prove waiting from that pane's host complete-input channel. The latest typed input must be a reviewer `review-resume` in this checkout, with no later typed input. The host's waiting evidence must also hold: for Claude, a background watcher started after that typed input and still running in the same session, including one restarted after an answer; for Codex, an active turn, which requirement Q02's busy skip already protects. When the proof holds, leave the reviewer alone. When it is incomplete, send no input and report the reviewer as pending, with the reason.
  - Pro: Respects Q22 without a new artifact, and an uncertain reviewer never receives input.
  - Con: Ambiguous evidence, for example after the watcher stopped or other input arrived, leaves the reviewer pending until a person resumes it. The Claude profile must define which transcript fields show a running background task.
- Option B: Deliver the marked reviewer resume whenever exact-exchange protocol evidence shows no current reviewer claim, and rely on the receiving workflow to reuse an existing watcher.
  - Pro: Activates the reviewer in more cases.
  - Con: It types into an already waiting reviewer, which Q22 forbids, and relies on model behavior to avoid a second watcher.
- Option C: Have `wait-any-request` keep a non-secret waiter record in the artifact home while it runs.
  - Pro: Gives protocol evidence for the leave-alone check.
  - Con: It breaks the rule that the watcher keeps no durable waiter record, and a hard kill leaves a stale record that can block activation.

#### Recommended option for Q16

Option A: The round 4 reviewer proposed A, and the writer agrees. It follows
Q22 and the existing rule that uncertain evidence never permits input, adds
no durable state, and reports pending cases to the person.

#### Answer to Q16: option A

Option A, confirmed by the user: prove waiting from the pane's complete-input
channel and current host waiting evidence. The latest typed input must be
reviewer `review-resume` in this checkout, with no later typed input. For
Claude, require a background watcher started after that input and still
running in the same session, including one restarted after an answer. For
Codex, an active turn is already protected by the busy-pane skip. Leave a
proved waiting reviewer alone. Incomplete evidence permits no input; report
the reviewer as pending with the reason.

Rationale: preserve requirement Q22's leave-alone rule and design Q04's check
order without adding durable waiter state or risking a duplicate watcher.
The Claude profile must validate which transcript fields prove a currently
running background task; this decision does not claim that validation exists.

User decision: confirmed: A, on 2026-11-10.

### Q17: Reviewer activation when no wait is running

Requirement Q22=A leaves a reviewer already serving or waiting untouched and
otherwise sends its marked reviewer resume. Confirmed Q16=A has two outcomes:
a proved wait leaves the reviewer alone, and incomplete proof sends no input
and reports the reviewer pending. A reviewer that is not waiting never passes
Q16's proof, so without a third outcome the tool would never activate a
reviewer, including a fresh conversation and the swapped pair in the
acceptance examples. What evidence shows that no wait is running, so that the
reviewer receives the marked resume?

A reviewer waits only through its host's own mechanism: a Claude background
watcher, or a Codex attached wait inside an active turn. An active turn is
already skipped as busy under requirement Q02=A.

#### BBQ for Q17

A dispatcher may call a driver whose bay is empty, but not one who might be
parked there. In this picture: the parked driver is a waiting reviewer, the
empty bay is proof that no wait is running, and the call is the marked
reviewer resume.

#### Options for Q17

- Option A: Treat a wait as excluded when current evidence shows that the host's wait mechanism is absent. For Claude, the transcript tied to the pane's session id shows no background task still running in that session, under a validated profile. For Codex, a fresh supported capture shows an idle pane with empty input and no active turn. Then deliver the marked reviewer resume after takeover proof, the normal eligibility checks and the later-continuation rules, which never resend an uncertain prior reviewer delivery. A case that is neither Q16's proved wait nor this exclusion is incomplete evidence: send no input and report the reviewer pending with the reason.
  - Pro: Activates a reviewer that is not waiting on both hosts, as requirement Q22=A and Q01=D require, while any possible wait still prevents input.
  - Con: Q16 option A's con lists a stopped watcher as a pending case; under this option an idle Claude pane whose profile proves no running task is activated instead. The Claude profile must prove that no background task is running, including after a host restart.
- Option B: Require the option A exclusion and, in addition, proof from the pane's complete-input channel that no reviewer entry command was typed in its current conversation.
  - Pro: Keeps Q16 option A's pending examples pending: a stopped watcher and input after a reviewer resume.
  - Con: Before a marked delivery, Q14 ties no Codex session file to a pane, so the tool would never activate a Codex reviewer. A Claude reviewer would be activated only in a fresh or cleared conversation.
- Option C: Never deliver after a failed waiting proof. Report the reviewer pending and leave its resume to the person.
  - Pro: The tool never types into a reviewer pane.
  - Con: Contradicts requirement Q22=A, which sends the reviewer resume otherwise, and Q01=D's counterpart activation. The user would have to reopen those requirement decisions.

#### Recommended option for Q17

Option A: The round 6 reviewer proposes A, and the writer agrees. A reviewer
can wait only through its host's own mechanism, so proof that the mechanism
is absent excludes a wait whatever the typed history. This activates a
reviewer that is not waiting, as requirement Q22=A requires, and Q16's
no-input rule still covers every uncertain case. This recommendation is not
a user decision.

#### Answer to Q17: option A

Option A, confirmed by the user: deliver the marked reviewer resume only
when current evidence excludes a wait: for Claude, no background task still
running in the pane's session under a validated profile; for Codex, a fresh
supported idle, empty-input capture with no active turn.
Takeover proof, the normal eligibility checks and the later-continuation
rules still apply; an uncertain prior reviewer delivery is diagnosed, not
resent. Otherwise follow Q16: leave a proved waiting reviewer alone, and
report every other case pending, with no input.

Rationale: proof that the host's waiting mechanism is absent permits the
reviewer activation required by requirement Q22=A and Q01=D while preserving
Q16's no-input rule for uncertainty. This changes Q16 option A's
stopped-watcher example: an idle Claude pane whose validated session profile
proves no background task remains running can be activated, including after
a host restart. Missing or ambiguous evidence still reports the reviewer
pending without input. The host profiles and their absence evidence still
require validation; this decision does not claim that proof already exists.

User decision: confirmed: A, on 2026-11-10. The user selected
"A: Prove no wait (Recommended)" after the Q17 explanation.
