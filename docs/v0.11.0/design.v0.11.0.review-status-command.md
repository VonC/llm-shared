# Design v0.11.0 -- Review status command

Reference feature request:
[feature-request.v0.11.0.review-status-command.md](feature-request.v0.11.0.review-status-command.md)

---

## Context for v0.11.0 review status

Review exchanges already persist their identity, ownership, round, lease, and
artifact locations. The missing piece is one family-neutral, read-only view
that discovers those records from the caller's repository and explains who
must continue, which umbrella owns the work, and what protocol action follows.

## Scope for v0.11.0 review status

The v0.11.0 outcomes are:

1. Discover every nonterminal specification and code-review exchange in the
   caller's repository.
2. Render the same trustworthy facts for humans and machine consumers.
3. Preserve damaged-exchange evidence without changing any review or Git state.

### In scope for v0.11.0 review status

- a public `review-status-command` skill exposed by the installed llm-shared
  plugin as `$llm-shared:review-status-command`;
- one canonical skill instruction and thin provider adapters that delegate
  status collection to `rvw_status`;
- a repository-root `rvw_status` entry point that preserves caller context;
- a shared read-only status service with human and JSON renderers;
- canonical identity, role, umbrella, lease, artifact, and next-action fields;
- independent results for healthy and damaged exchanges; and
- stable success, untrustworthy-result, and operational-failure outcomes.

### Deferred from v0.11.0 review status

- selecting one exchange when several are active;
- renewing, reclaiming, repairing, cancelling, or completing an exchange;
- executing the reported next action; and
- the `rvw_resume` continuation command.

---

## Confirmed technical facts for v0.11.0 review status

**Exact state classification already exists**: `ReviewExchangeObserver` reads
one bound exchange without mutation, validates its live artifacts, evaluates
lease currency, and delegates to the pure `classify_snapshot` state table.

**Canonical paths already exist**: `derive_artifact_paths` returns the request,
answer, coordination, tombstone, transcript, and transition-lock paths from a
validated `ReviewContext`; transient filenames can also be parsed into an
`ExchangeIdentity`.

**Coordination records carry the required authority**: a strict
`CoordinationRecord` contains the exact context and family policy, `owner`,
`expected_next_actor`, round, lease timestamp, confirmation fields, and
incomplete-transition evidence.

**Lease expiry uses project configuration**: the observer compares
`lease_renewed_at` plus `ReviewConfiguration.wait_timeout_seconds` with an
injected wall clock.

**Caller-root precedent is available**: `commit-plan-check` discovers upward
from `Path.cwd()` unless `--root` is supplied, and its root launcher preserves
the caller's working directory while self-locating the shared Python runtime.

---

## Current behavior for v0.11.0 review status

The existing exchange command observes one identity supplied by its caller:

```txt
exact document and policy
  -> derive one artifact set
  -> observe and classify one exchange
  -> render one operation result
```

A returning caller must therefore remember enough identity to invoke that
single-exchange path. There is no repository-wide discovery result, no explicit
continuing-agent view, and no shared cardinality or trustworthiness outcome.

## Target behavior for v0.11.0 review status

```txt
caller working directory or explicit root
  -> validated Git repository root
  -> canonical coordination-record discovery
  -> strict record and filename validation per entry
  -> existing observer classification for valid identities
  -> normalized status records
  -> one human report or one versioned JSON result
```

Discovery never takes a review family, document, slug, step, round, occurrence,
role, or artifact path. It reads only protocol-owned coordination candidates at
the resolved repository root. Each candidate becomes either a validated
exchange status or a damaged-entry diagnostic; one bad candidate does not
discard healthy results.

---

## Repository and discovery boundary for v0.11.0 review status

### Caller repository resolution

The default root is discovered upward from the caller's current working
directory. An explicit `--root` selects a repository for controlled callers and
tests. Both the root launcher and direct shared entry point pass the same
resolved root into the status service; the launcher self-locates its runtime
without changing directories.

A missing Git root, unreadable root, or invalid explicit root is an operational
failure. It produces no guessed repository and no partial exchange result.

### Coordination-record discovery

Discovery enumerates only canonical active coordination filenames at the root.
For each candidate it:

1. parses the filename identity;
2. strictly parses the coordination record;
3. verifies that filename identity, record context, and derived canonical paths
   agree; and
4. invokes the existing observer with the record's exact context and policy.

The document and umbrella values come from durable exchange context. A legacy
record missing umbrella identity is repair-required; document metadata may be
shown as a hint but never promoted into authoritative identity.

`idle` observations are excluded from the active list. Every other
`ArtifactState` value is included verbatim, including
`owning-action-pending`, abandoned, interrupted, repair-pending, escalated, and
inconsistent states.

## Normalized exchange result for v0.11.0 review status

### Stable machine record

The JSON document has a schema version, repository root, overall outcome,
active count, error flag, and an ordered `exchanges` array. Each exchange entry
contains:

- canonical family, type, version, slug, reviewed document, umbrella or null,
  implementation step or null, round, and occurrence;
- exact state and diagnostic;
- continuing role, role specialization, and owner;
- lease timestamp, configured timeout, and derived freshness;
- canonical artifact paths with applicability and observed presence; and
- stable next-action identity plus its human rendering.

Entries use a deterministic identity order so unchanged repository evidence
produces stable output.

### Continuing-agent mapping

For ordinary agent turns, the broad continuing role comes directly from
`expected_next_actor`, and family plus role supplies the specialization.
`owner` remains a separate field.

Two states intentionally record a human next actor. At `convergence-gate`, the
continuing agent is `requestor`, the owner remains `reviewer`, and the
next-action identity says that human confirmation is required. At `escalated`,
the continuing role is the agent named by the artifact shape and the next action
is human escalation resolution. A human next actor in any other state is
inconsistent. Genuine corruption reports role `unknown`; a healthy
owner/next-actor difference does not.

### Lease freshness

The raw `lease_renewed_at` value remains authoritative. The derived lease block
also reports the expiry timestamp, evaluation timestamp, configured timeout,
and one of `current`, `expired`, `not-held`, or `missing`. `not-held` means the
protocol deliberately cleared the lease at `convergence-gate` or `escalated`;
`missing` is a defect in a state that should carry lease evidence. Consumers can
derive elapsed or overdue duration from the fixed timestamps. Status does not
renew or reclaim the lease.

### Artifact completeness

Each of the six paths comes from `derive_artifact_paths`, never from locally
reconstructed names. Every path record carries an applicability value and an
observed presence boolean. Expected-but-missing and unexpected-but-present
shapes remain visible and feed the exchange diagnostic.

### Next-action identity

One closed action vocabulary describes protocol intent independently of display
text. Its values distinguish waiting for the counterpart, requestor or reviewer
work, human confirmation, authorized owning work, reclaim, repair, escalation
resolution, and no safe action. The human command or description is rendered
from that identity and the exact exchange context, so the two forms cannot
drift.

## Skill entry point for v0.11.0 review status

The installed llm-shared plugin exposes the public skill name
`$llm-shared:review-status-command`. Its canonical instruction invokes the
repository-root `rvw_status` launcher from the caller repository and reports
the typed command outcome. Provider-specific files contain only discovery
metadata and a direct reference to that canonical instruction.

The skill does not duplicate discovery, classification, rendering, or
exit-code policy in Markdown. It remains read-only and does not resume, renew,
reclaim, repair, cancel, complete, stage, or commit an exchange.

## Human report and command outcome for v0.11.0 review status

### Human-readable report

The human renderer starts with the repository and overall outcome, then prints
one labelled block per exchange. `Role`, `Specialization`, `Owner`, and
`Umbrella` are separate visible fields. Umbrella uses the exact
repository-relative path or the literal `none`. Damaged entries retain their
candidate path and diagnostic even when their full identity cannot be trusted.

### Trustworthiness and process status

- Status `0` means the query is trustworthy, whether it found zero, one, or
  several well-formed active exchanges.
- Status `3` means the command completed but at least one candidate is
  unreadable, malformed, inconsistent, or repair-required. Trustworthy partial
  entries remain in both output forms.
- Status `2` means invocation, root resolution, or another operational boundary
  prevented a trustworthy query.

The human and JSON renderers consume the same normalized result, and process
status is derived from its overall outcome rather than from renderer text.

## File-based IO cost clarification for v0.11.0 review status

- Enumerate the reserved active-coordination prefix once at the resolved root;
  never scan the documentation tree or inspect unrelated repository files.
- Load `ReviewConfiguration` once and share it across every per-candidate
  `ReviewExchangeObserver`.
- For each candidate, read the coordination bytes before observation, inspect
  only the six fixed artifact paths, then read the coordination bytes once more
  for the required changed-during-read fingerprint check.
- Normalize, order, and render the collected records in memory; neither renderer
  performs another filesystem read.

The scan is linear in active coordination candidates with a constant artifact
set per candidate. It enters no transition lock and performs no protocol or Git
write.

## Read-only trust boundary for v0.11.0 review status

The status path opens artifacts for reading and performs bounded Git root
queries only. It never enters the exchange transition lock and never calls
store publication, lease, recovery, confirmation, completion, marker, index, or
ref mutation operations. Repeated calls over unchanged files and the same wall
clock freshness bucket return the same normalized identity and action data.

Filesystem races are reported as damaged or operational evidence rather than
retried through a mutating recovery path. The later resume feature consumes the
status result and owns every state-changing choice.

---

## Acceptance cases for v0.11.0 review status

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| No coordination records | Status `0`, active count `0`, empty exchange list | No active work is a trustworthy result. |
| One request pending | Reviewer continuing role, requestor owner, exact umbrella, wait-for-reviewer action | `expected_next_actor` controls the next agent while ownership remains separate. |
| Convergence gate | Requestor continuing role, reviewer owner, human-confirmation action, and `not-held` lease | The agent continuation, durable owner, and human authority remain distinct. |
| Owning action pending | Requestor role and authorized-owning-work action | A returning agent must not repeat the human gate. |
| Escalated exchange | Escalated state, artifact-shape continuing role, resolve-escalation action, `not-held` lease, overall status `3` | A valid human-resolution stop is diagnostic, not inconsistent. |
| Wait timeout escalation | Original request retained, artifact-shape reviewer role, resolve-escalation action, `not-held` lease, overall status `3` | An overnight stopped handoff remains identifiable and recoverable. |
| Standalone review | Visible `Umbrella: none` and JSON null | Confirmed absence is explicit in both renderers. |
| Legacy record missing umbrella | Status `3`, repair diagnostic, optional metadata hint | Missing identity is not silently inferred or changed to `none`. |
| Current and old leases | Raw timestamps plus current/expired freshness and age | State gives the kind of interruption; freshness gives its degree. |
| Missing expected answer | Canonical answer path marked missing and exchange diagnostic retained | Diagnosis reports both expected shape and observed evidence. |
| Healthy and damaged records together | Healthy entries plus damaged entry, overall status `3` | One defect does not hide independent exchanges. |
| Launcher called from another repository | That caller repository is reported and matches direct-entry output | Runtime location does not replace caller context. |
| Repeated unchanged query | No review artifact, lease, marker, index, ref, or working-tree change | Status remains strictly read-only. |

## Design decisions for v0.11.0 review status

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Discover every file under the reserved coordination prefix and report malformed near-matches as damaged candidates, so unfinished evidence cannot disappear from an otherwise trustworthy result. | Coordination-record discovery | Canonical-name-only discovery hides malformed records; transcript-led discovery misses pre-transcript exchanges and gives transcripts identity authority. |
| Q02 | Represent entries as a tagged union of validated exchanges and damaged candidates, keeping partial evidence distinct from valid nullable fields. | Stable machine record | One nullable record conflates absence with distrust; separate top-level arrays split one ordered repository result. |
| Q03 | Report one absolute repository root and make document, umbrella, candidate, and artifact paths repository-relative, so results remain portable between checkouts. | Caller repository resolution and Stable machine record | Absolute paths everywhere are machine-specific; paired absolute and relative paths duplicate fields and can drift. |
| Q04 | Resolve agent-valued next actors directly, map `convergence-gate` to requestor, map `escalated` to the artifact-shape agent, and reject human next actors in every other state. | Continuing-agent mapping | Falling back to owner confuses ownership with continuation; reporting unknown hides the supported human-turn states. |
| Q05 | Report fixed renewal, expiry, and evaluation timestamps with the timeout and `current`, `expired`, `not-held`, or `missing`; consumers derive duration when needed. | Lease freshness | A changing duration makes stable evidence time-dependent; a category alone loses reproducible timing evidence. |
| Q06 | Use a closed semantic next-action vocabulary and derive human text from the action plus exchange context, preserving a durable routing fact across launcher-name changes. | Next-action identity | CLI operation names cannot express every role or human action; complete commands make host details part of the schema. |
| Q07 | Use an object keyed by all six canonical artifact kinds, with path, applicability, and presence held together for direct and unambiguous access. | Artifact completeness | A list requires searches and duplicate guards; parallel maps can drift and require joins. |
| Q08 | Sort healthy entries by stable exchange identity and damaged candidates by repository-relative path, producing repeatable output across filesystems. | Stable machine record | Urgency ordering embeds a changing policy; filesystem order varies by host and directory history. |
| Q09 | Return status `0` for trustworthy results, `3` for results containing untrustworthy exchange evidence, and `2` for invocation or operational failure. | Trustworthiness and process status | Per-state exit codes duplicate payload detail; always returning zero lets shell automation miss unsafe results. |
| Q10 | Fingerprint each coordination record before and after observation and report changed-during-read when the fingerprints differ, retaining a strictly read-only consistency check. | Read-only trust boundary | An unchecked pass can mix transition moments; taking the transition lock would mutate protocol state. |
