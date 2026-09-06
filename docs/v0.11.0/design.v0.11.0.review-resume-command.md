# Design v0.11.0 -- Resume interrupted reviews from their durable LLM role

This design implements the behavior specified by
`feature-request.v0.11.0.review-resume-command.md`. It is a cross-cutting
revision of the review exchange: runtime artifacts gain a configurable home,
role ownership gains an LLM-nature trace, status gains a bounded migration
preflight, and an LLM-only resume skill continues the correct requestor or
reviewer workflow.

## Context for v0.11.0 review resumption

The durable exchange already records enough identity and state to diagnose an
interrupted review, but its runtime evidence is spread across project-root
files and it records only protocol roles, not the LLM host that acted in each
role. Existing exact-identity wait operations also cannot express a reviewer
waiting before any concrete request exists.

Resumption therefore cannot be a thin alias for one existing exchange command.
It must first normalize artifact placement, resolve and verify role identity,
and then dispatch to one of two deliberately different continuations:

- a reviewer is a persistent review-request consumer and either answers a
  concrete request or waits for any future specification or code request;
- a requestor owns one task workflow and either waits for its exact answer,
  performs its exact exchange action, or asks `pw skill` for the next task.

## Scope for v0.11.0 review resumption

### In scope for v0.11.0 review resumption

- one versioned repository declaration for the runtime artifact home;
- a shared artifact locator used by all review producers and consumers;
- a fast placement check and an all-or-none legacy migration;
- bounded migration from ordinary review-status collection;
- durable Claude, Codex, Gemini, or `unknown` evidence per protocol role;
- legacy identity inspection and current-role backfill;
- an LLM-only resume skill with thin host adapters;
- exact continuation for specification and code-review requestors and
  reviewers;
- identity-free, open-ended reviewer waiting for the next request;
- lease-independent human-invoked pickup with displaced-session rejection;
- schema, renderer, instruction, documentation, and regression-test updates
  required by these cross-cutting changes.

### Outside this design

- moving versioned `docs/.../review.*.md` transcripts away from their reviewed
  documents;
- reopening completed requirement, design, plan, validation, or umbrella
  status documents from earlier review-mode topics;
- a batch, shell, `rvw_resume`, or other non-LLM resume command;
- automatic ordering or processing of several simultaneously available
  requests;
- changing the authority of automated rounds or the human convergence gate;
- replacing a conflicting recorded LLM nature;
- a repository-wide identity rewrite unrelated to the selected occurrence.

## Confirmed technical facts for v0.11.0 review resumption

- `tools/review_exchange_paths.py` currently derives request, answer,
  coordination, tombstone, and transition-lock paths directly below the caller
  project root.
- Exchange activation currently submits all transient paths to one
  `git check-ignore -z --stdin` check and rejects uncovered paths.
- `tools/review_status.py` currently discovers root-level
  `a.review-active.*` coordination records and the status contract is described
  as strictly read-only.
- The typed status model currently has schema version 1 and distinguishes
  trustworthy, untrustworthy, and operational-failure outcomes.
- Request and answer envelopes and coordination records use strict schemas and
  do not currently carry LLM-nature evidence.
- Exact request and answer waits require a complete exchange identity and a
  bounded timeout.
- The existing host evidence recognizes Claude through `CLAUDECODE` and Codex
  through `CODEX_THREAD_ID`; falling back to Claude when neither is present is
  not reliable enough for identity evidence.
- Claude, Codex, and Gemini integrations are Markdown adapters over canonical
  shared instructions. Provider files must remain thin direct pointers.
- Current reviewer instructions stop at convergence and therefore do not yet
  implement the persistent-consumer behavior settled by the feature request.

## Target architecture for v0.11.0 review resumption

The feature is organized around five shared services and one orchestration
layer:

1. `ReviewArtifactConfiguration` loads and validates the versioned artifact-home
   declaration.
2. `ReviewArtifactLocator` maps every recognized runtime artifact identity to
   that home.
3. `ReviewArtifactMigration` checks placement, creates a safe home, and performs
   recoverable all-or-none migration.
4. `LlmNatureDetector` and `RoleNatureEvidence` detect, persist, reconcile, and
   backfill role-specific host identity.
5. Review status discovers through the locator and projects migration and role
   nature into schema version 2.
6. The canonical resume skill applies those services, resolves a role, and
   delegates to requestor or reviewer continuation.

All exchange commands, waiters, status readers, skills, and tests consume these
shared services. No caller reimplements path construction, artifact
classification, host detection, or role reconciliation.

## Versioned artifact-home declaration

The repository-root file `.review-artifacts.ini` is the sole durable setting
carrier. It is optional; its absence means the default home `.reviews`.

```ini
[review-artifacts]
home = .reviews
```

The parser accepts exactly one `[review-artifacts]` section and one `home`
property. The value is a non-empty repository-relative path. Resolution uses
the physical caller repository root, normalizes `.` and separators, resolves
links before boundary validation, and rejects:

- absolute, drive-relative, UNC, or environment-expanded values;
- a normalized path equal to or outside the repository root;
- the repository root itself;
- a path that names an existing tracked directory;
- an unreadable declaration, duplicate section or property, or unsupported
  property.

The declaration itself remains at the root and is intended to be versioned.
Environment variables, status arguments, resume arguments, and ignored
per-clone markers cannot replace its value. The resolved absolute path is an
internal value; machine output uses the repository-relative form so evidence is
portable between clones.

## Artifact registry and path resolution

`ReviewArtifactLocator` owns an explicit registry of protocol artifact kinds.
The registry covers request, answer, active coordination, lease and wait state,
transition lock, retained manifest, consumed tombstone, question-management
state, review guidance, review-mode runtime state, and any other runtime file
that a review workflow creates. Adding a new protocol artifact requires adding
its kind and name parser to this registry.

The registry is deliberately not a broad `a.*` or recursive glob. Migration
must never capture unrelated user files merely because their names resemble
temporary evidence. Each registered kind defines:

- its accepted legacy root name;
- its artifact-home name;
- whether it carries a full durable exchange identity;
- which role, if any, authored it;
- whether it can contain role-nature evidence;
- its collision and integrity checks.

All runtime artifact derivation goes through the locator. Transcripts continue
to derive from the reviewed document and remain in `docs`. The versioned
`.review-artifacts.ini` declaration is configuration, not a migrated runtime
artifact.

## Artifact-home ignore coverage

Before the home receives its first runtime artifact, creation writes a
home-local `.gitignore` containing a catch-all rule:

```gitignore
*
```

The rule covers the ignore file itself and every runtime descendant. Creation
then asks Git to verify effective ignore coverage for the ignore file and every
prospective artifact path. A newly created empty home is removed if writing or
validation fails.

An existing home is not silently repaired. Missing, malformed, or ineffective
coverage is a blocked layout with a diagnostic that names the home and failed
path. This preserves the existing activation invariant: artifacts are accepted
because Git ignores them, not because the new home receives an exception.

## Migration check and transactional migration

### Fast placement check

`migration_check` is a shared read-only operation. It loads the declaration,
then inspects only:

- recognized legacy artifacts directly below `PRJ_DIR`;
- the default `PRJ_DIR/.reviews` location;
- the configured home when it differs from the default.

It parses names and the minimum identity metadata needed to detect duplicate,
damaged, or ambiguous evidence. It does not build the full review-status model.
Its typed result is one of:

- `ready`: all recognized runtime artifacts are in the resolved home;
- `migration-required`: one or more recognized artifacts are in a legacy or
  superseded inspected location and the complete move is safe;
- `blocked`: configuration, ignore coverage, integrity, collision, or location
  ambiguity prevents a safe move.

The result includes the resolved home, inspected locations, source-to-target
map, and diagnostics. `ready` also distinguishes a pre-existing home from a
home that has not yet needed creation.

### All-or-none migration

Migration accepts only a fresh `migration-required` result. Under a
repository-scoped migration lock it repeats validation, creates and validates
the home when absent, and writes a migration journal inside that ignored home.
The journal records the complete source-to-target map, source fingerprints,
and phase before the first move.

Each move is an atomic same-volume rename where supported and is recorded in
the journal. Any ordinary failure triggers reverse-order rollback and restores
the original root layout. A later invocation that finds an incomplete journal
recovers before returning a placement result: it rolls back an uncommitted
migration or finishes cleanup after a committed one. The commit phase is
recorded only after every target exists with the expected fingerprint. Source
cleanup and journal removal follow that commit.

Thus callers observe either the complete source layout or the complete target
layout. A collision is detected before movement, never overwritten, and one
collision blocks the whole operation. The same durable artifact identity in two
inspected locations with different bytes is an ambiguity and also blocks the
whole migration. The migration preserves bytes and file timestamps where the
platform permits; it does not rewrite legacy identity.

Resume always performs check, safe migration when required, and a second check
before status or role selection. Review status performs the same bounded
preflight automatically. A blocked result or a non-`ready` second result is an
operational failure and no exchange continuation follows.

## LLM-nature detection and durable evidence

### Detection contract

`LlmNatureDetector` returns `claude`, `codex`, `gemini`, or `unknown`, together
with a non-secret evidence source. Detection uses a trusted host hint supplied
by the installed provider entry point first, then known host-owned environment
signals. Contradictory known signals produce `unknown` with a conflict
diagnostic; absence of evidence also produces `unknown`. It never defaults to a
specific LLM.

The trusted hint is part of skill invocation context, not a user-selectable
resume argument and not durable repository configuration. Canonical logic
validates it against the supported enum. Claude and Codex retain their known
host signals, and the Gemini adapter supplies the `gemini` hint; environment
support can be extended when Gemini exposes a stable host-owned signal without
changing artifact schemas.

Only the enum value is persisted. Environment-variable names, values, session
IDs, and other host evidence are never written to review artifacts.

### Role-nature representation

New strict schemas carry a role map:

```json
{
  "role_natures": {
    "requestor": "codex",
    "reviewer": null
  }
}
```

A string is the nature detected when that role acted. `null` means the role has
not yet produced attributable evidence in that exchange occurrence. The
explicit value `unknown` means the role acted but reliable host detection was
unavailable. Absence of `role_natures` identifies a legacy schema.

Each request, answer, coordination transition, retained or consumed state, and
transcript entry preserves the two-role snapshot known at creation. The first
request records the requestor and leaves an unobserved reviewer as `null`; the
reviewer's claim and answer add the reviewer value; later requestor transitions
preserve both. Status reconciles all snapshots and reports both the effective
value and the contributing artifact paths.

Role authorship comes from artifact kind and durable transition semantics, not
from a mutable prose label. New writes cannot silently change an already known
non-`unknown` nature for a role.

## Legacy role evidence and backfill

After migration and role selection, resume enumerates every artifact in the
selected exchange occurrence that the registry attributes to the selected
role. It partitions them into missing, matching, and conflicting nature sets.
Counterpart-role artifacts are readable, but missing counterpart nature is
ignored and never backfilled by the current role.

For a known current nature:

1. the complete set is scanned before any mutation;
2. any conflicting non-missing value stops the attempt and presents all
   conflicts together;
3. `Stop` changes nothing;
4. attempt-scoped `Override` preserves every conflicting value, fills only
   missing selected-role values, and permits continuation;
5. with no conflict, all missing selected-role values are filled atomically
   before continuation.

For an `unknown` current nature, resume performs the same role selection but
does not backfill missing values. It also cannot prove that an existing known
selected-role value conflicts, so that value is preserved and continuation does
not require the discrepancy override. The explicit role or human role choice is
the authority for this attempt.

Mutable JSON artifacts receive the new field through a validated atomic
rewrite. Immutable transcript history is not edited in place; one append-only
identity-completion entry records the affected role, occurrence, current
nature, and artifact paths. Its heading is
`### LLM nature completion for <role> (exchange <occurrence>)`. The role and
occurrence qualifiers keep every completion heading unique within a transcript,
and the entry identifier makes a repeated completion attempt idempotent.
Request and answer content files that are part of the current runtime occurrence
are atomically rewritten only when their parsed schema supports a lossless
legacy upgrade. Failure of any prospective rewrite prevents all backfill;
temporary replacements are validated before a commit phase and rolled back on
failure.

## Status model and migration-aware reporting

Review status schema advances from version 1 to version 2. Its top-level result
adds:

```json
{
  "migration": {
    "state": "unnecessary | completed",
    "artifact_home": ".reviews",
    "moved_count": 0
  }
}
```

`unnecessary` means the preflight began ready. `completed` means status safely
migrated evidence and the required second check returned ready. A blocked check,
migration failure, or failed second check returns the existing
`operational-failure` outcome with typed migration diagnostics instead of a
normal schema-2 exchange list.

Each exchange projection adds `requestor_llm_nature` and
`reviewer_llm_nature`. A value can be one supported enum, `unrecorded` for
legacy or not-yet-observed evidence, or `conflicting` with an accompanying
evidence list. Human rendering labels both roles explicitly. Machine consumers
read typed fields and never infer identity from report prose.

After migration succeeds or is unnecessary, status discovery and projection
are read-only and enumerate coordination records only through the configured
home. The canonical status instruction and published skill description state
this bounded mutation exception.

## Resume skill orchestration

Resume is implemented as one canonical LLM skill and canonical instruction.
Claude, Codex, and Gemini adapters contain only the provider-required direct
pointer to that canonical content plus the trusted provider hint mechanism
allowed by the adapter format. No adapter copies workflow rules.

Invocation accepts an optional protocol role, `requestor` or `reviewer`; it does
not accept an artifact-home override or exchange identity guess. The canonical
sequence is:

1. resolve the caller repository;
2. detect the current LLM nature;
3. run migration check, migrate if required, and require a ready recheck;
4. collect typed status and locate resumable evidence;
5. resolve or confirm the protocol role;
6. inspect and, when allowed, backfill selected-role identity;
7. acquire a fresh ownership capability for a concrete exchange when one
   exists;
8. dispatch immediately to the role-specific continuation.

Malformed, repair-required, escalated, artifact-inconsistent, or ambiguous
status stops before dispatch and shows the typed evidence. The only normal
ambiguities delegated to the human are role selection, known role conflict,
and selection among several simultaneously available requests.

## Role resolution

Role resolution reconciles all role-nature evidence in the selected occurrence:

- one role matches the known current LLM: select it without confirmation;
- neither role has nature and no argument exists: ask `requestor` or `reviewer`;
- an explicit role with no trace supplies the choice without confirmation;
- both roles match and no argument exists: ask which role to continue;
- an explicit role conflicts with known trace: show the mismatch and require
  one confirmation for this attempt;
- an explicit role matches: select it, while still running the full artifact
  identity scan;
- current nature is `unknown`: use an explicit role or ask for one, without
  writing `unknown` into missing legacy identity.

Once this gate and any selected-role evidence gate pass, resume does not ask for
a second go-ahead before waiting or acting.

## Lease-independent pickup and displaced sessions

Every ordinary or resumed session acquires an ownership capability when it
claims its next actor-owned transition. `start`, `reclaim`, an exact wait that
wakes for its actor, and a global reviewer wait that selects a request perform a
locked compare-and-swap, increment a monotonic `ownership_generation`, and issue
a fresh random ownership token. Coordination stores only the token digest. The
secret is returned only to the claiming LLM session's machine result and is
never printed in human reports or recoverable from coordination.

Every mutating exchange command presents the generation and secret held by its
session. Under the transition lock, the core re-reads coordination, checks the
generation, and compares a digest of the presented secret with the stored
digest. A command never reads its token from coordination. Successful handoff
to a different expected actor requires that actor to claim a new capability;
the previous capability is invalidated by the new generation.

A human's direct resume invocation is an explicit recovery action, so it may
perform that claim even while the previous owner's lease is fresh. A displaced
session that rereads coordination learns the current generation but cannot
present its secret. Its next renewal, publication, consumption, or state
transition fails with a typed `ownership-superseded` result showing the durable
exchange identity and current generation. It cannot refresh its old lease or
overwrite resumed work.

Read-only polling does not require a capability, but a wake must claim or
validate one before acting. An ordinary session without the capability returned
by its claim, or with an invalid capability, cannot mutate and receives a typed
ownership failure. Repeating resume with the capability for an unchanged owned
generation is idempotent; a distinct later direct resume is another authorized
pickup and advances the generation.

A session holding no capability for a live exchange acquires one through a
direct resume pickup, which is authorized to claim while the previous lease is
fresh. Two ordinary situations reach that state: a later session that arrives
at the durable convergence gate without having run the wait that claims, and a
session whose secret is no longer available to it mid-round. `reclaim` does not
cover either, since it applies to a round abandoned through lease expiry.
Neither situation requires waiting for the lease to lapse.

## Reviewer continuation

Reviewer continuation is request-consumer-only:

- If exactly one valid request is available, resume claims or reclaims that
  request's complete identity and generation, runs the matching specification
  or code reviewer workflow, and publishes its exact answer.
- If no request is available, resume enters a global reviewer wait that watches
  only recognized request artifacts in the configured home.
- If several requests are available or arrive in one observation, it lists
  their family, document, step, round, occurrence, requestor nature, and age and
  asks the human to choose one.

`GlobalReviewRequestDiscovery` owns notification hints, bounded polling, and
authoritative candidate rescans without claiming. `GlobalReviewerWait` selects
one discovered candidate and invokes the locked claim compare-and-swap. When
several reviewer waits race for one request, the first successful claim owns it.
Every `already-claimed` loser discards no evidence and returns to discovery.
Recorded reviewer nature does not reserve an unclaimed request; it is identity
evidence and a later discrepancy gate, not a scheduling lock.

The global wait is identity-free and has no exchange timeout before a request
exists. It uses the existing file-observation abstraction with a low-cost
directory change notification where supported and bounded polling fallback.
Each wake rescans and validates the complete candidate set, so events may be
coalesced without losing requests. It remains active until a request is selected
or the human cancels.

`wait-any-request` is one quiet foreground blocking command. It writes no idle
progress to standard output or standard error and returns one final machine
result after a request is selected and claimed, ambiguity is found, or the human
cancels. A graceful host or console interruption is caught as cancellation and
returns exactly one final machine result rather than raw interrupt output. The
result contains `operation`, `outcome`, `identity`, `candidates`, and
`diagnostic`; `found` adds the session-only generation/token capability from
its locked claim, while other outcomes contain no capability. `found` exits 0;
`ambiguous` and `cancelled` exit 3; invalid input and operational failures exit
2. A hard process kill may prevent a final result and grants neither a claim nor
subsequent authority. A Codex or Claude session can await that command without
model-side polling; the protocol does not promise that a file watcher can create
a new model turn after its host ends the command.

Idle, concluded, requestor-owned, and human-convergence-gate exchanges are all
valid entry states. A matching later round or occurrence and an entirely new
specification or code exchange wake the same wait. Unrelated artifacts do not.
After an intermediate answer, the reviewer returns to the global wait instead
of requiring an exact replacement-request wait. After convergence, it likewise
waits globally; it never performs the human or requestor action.

Reviewer resume never runs `pw skill`, writes a requirement or design,
implements code, publishes a request as requestor, or advances a requestor
workflow.

## Requestor continuation

Requestor continuation stays bound to the selected exchange until that exchange
hands control back to its owning workflow:

- `answer-pending` or an equivalent response-wait state starts or restarts the
  exact answer wait;
- a requestor-owned state claims or reclaims the complete exchange identity,
  consumes the answer, applies requested changes, publishes the next round, or
  presents the durable human convergence gate as directed by the existing
  requestor skill;
- when no review remains for the current task, it runs `pw skill` and
  immediately follows the returned writer, implementation, review-requestor,
  or other workflow handoff.

Requestor resume never waits for an arbitrary future request. If its current
workflow later needs a new review, it initiates that new exchange through the
normal requestor skill with the new exact identity.

## Failure and idempotency boundaries

- Configuration and placement failures stop before status collection.
- Migration and identity backfill validate their complete change sets before
  mutation and recover incomplete journaled work before retry.
- Ambiguous exchange identity is never resolved from filename ordering.
- Several requests require human selection; they are not treated as corrupt.
- A conflicting current-role nature requires `Override` or `Stop`; missing
  counterpart nature does not.
- `unknown` detection is supported but is not used to fill legacy evidence.
- A missing, stale, or invalid ownership capability cannot mutate an exchange,
  whether the actor entered through an ordinary workflow or direct resume.
- Repeating check, migration after completion, backfill after completion, wait,
  or resume against unchanged state has no additional durable effect.
- The convergence gate and all existing requestor/reviewer authority checks
  remain in force after pickup.

## File-based IO cost clarification for v0.11.0 review resumption

- Configuration is loaded once per workflow invocation and the resolved locator
  is reused by every producer and consumer in that invocation.
- Placement preflight performs three non-recursive directory reads and parses
  only registered candidates; migration fingerprints each source a bounded
  number of times under one journaled transaction.
- Status performs no projection before placement is ready and performs one
  ordinary read-only projection afterward.
- Role reconciliation is linear in artifacts for one selected occurrence.
- Directory notifications only mark the global wait dirty; a bounded rescan is
  the source of truth, so event callbacks perform constant work.
- Ownership claims and mutations read and write one coordination record under
  the transition lock.

## Acceptance cases for v0.11.0 review resumption

1. With no declaration, all new runtime artifacts resolve below `.reviews` and
   transcripts remain beside reviewed documents.
2. A valid `.review-artifacts.ini` redirects every producer, consumer, waiter,
   status reader, migration path, and resume path to the same repository-local
   home.
3. External, root, tracked-directory, malformed, or contradictory home
   declarations fail before artifact access.
4. A new home receives effective local ignore coverage before its first
   artifact; an existing uncovered home blocks without silent repair.
5. The fast check distinguishes ready, migration-required, and blocked layouts
   by inspecting only root, default, and configured locations.
6. A complete legacy set migrates together, one collision moves nothing, and
   interrupted migration recovers to one complete layout.
7. Resume and ordinary status both perform check, migration, and ready recheck;
   status schema 2 reports unnecessary or completed migration and uses
   operational failure for a block.
8. New requestor and reviewer actions record the detected Claude, Codex,
   Gemini, or explicit `unknown` role nature without persisting host secrets.
9. Status renders and serializes both role natures and identifies unrecorded or
   conflicting evidence.
10. A known selected role with matching and missing legacy evidence fills every
    missing selected-role artifact in the occurrence before continuation.
11. One selected-role conflict prevents partial backfill and lists the full
    conflict set; Override preserves conflicts and Stop changes nothing.
12. Missing counterpart identity remains readable and unchanged, while an
    unknown current host can continue after role selection without backfill.
13. Resume infers one matching role, asks when legacy evidence cannot decide,
    and confirms only an explicit mismatch or two-role match.
14. Direct resume displaces a live lease by advancing ownership generation, and
    the old session receives `ownership-superseded` on its next mutation.
15. Ordinary requestor and reviewer sessions acquire a generation and token
    when they claim actor-owned work and can complete normal mutations through
    the same fence used by resumed sessions.
16. A session holding no capability picks up a live exchange through direct
    resume, advances the generation, and completes the mutation its role owns,
    including a human confirmation at the convergence gate.
17. A reviewer answers one available request or waits globally from idle,
    concluded, requestor-owned, and convergence-gate states.
18. The global wait wakes for a same-exchange replacement or any new
    specification or code request, ignores other artifacts, persists until
    request or cancellation, and asks when several requests coexist.
19. Two reviewer waits racing for one request produce one successful claim; a
    loser receives `already-claimed` and resumes its global wait.
20. A requestor waits for its exact answer, performs its owned exchange action,
    or follows `pw skill`; it never waits for arbitrary review requests.
21. After role and evidence gates pass, both continuations wait or act without
    another confirmation.
22. Existing exchange, status, requestor, reviewer, adapter, waiting,
    documentation, and regression suites use the shared locator and updated
    schemas and no longer assume root-level artifacts or a default Claude host.

## Design decisions for v0.11.0 review resumption

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Recognize protocol runtime artifacts through one explicit registry of kinds, names, parsers, authorship, and migration rules. | Artifact registry and path resolution | A broad review filename namespace; content-schema discovery. |
| Q02 | Merge every validated, identity-distinct inspected source into the configured home in one transaction; block collisions, damage, and one identity with different bytes. | Migration check and transactional migration | Blocking every split location; moving root artifacts while leaving a former home. |
| Q03 | Store the best-known two-role nature snapshot in each identity-bearing artifact, using `null` until a role acts. | Role-nature representation | Actor-only records; a separate identity ledger. |
| Q04 | Rewrite eligible mutable runtime evidence and append a transcript completion entry qualified by role and occurrence. | Legacy role evidence and backfill | Rewriting historical transcript entries; excluding transcripts from completion. |
| Q05 | Give every ordinary or resumed actor claim a monotonic generation and session-held secret token while coordination stores only its digest. | Lease-independent pickup and displaced sessions | Generation alone; nonce alone; a pickup-only fence. |
| Q06 | Observe global reviewer requests through directory notifications plus bounded polling, with a complete rescan as the source of truth. | Reviewer continuation | Polling only; native notifications without fallback. |
| Q07 | Let the first locked reviewer claim win one request; return every `already-claimed` loser to global waiting. | Reviewer continuation | Reserving by reviewer nature; stopping all waiters for human selection. |
| Q08 | Treat a graceful foreground host or console interruption as cancellation and return one typed result with the stated fields and exit mapping, without persisting wait state. | Reviewer continuation | LLM polling; streamed progress; durable waiter state. |
