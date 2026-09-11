# Design v0.11.0 -- Review Exchange Core

Reference feature request: [feature-request.v0.11.0.review-exchange-core.md](feature-request.v0.11.0.review-exchange-core.md)

---

## Context for v0.11.0 review exchange core

The review-mode workflow needs a shared, role-neutral protocol through which a writer and an independent reviewer exchange feedback. This design defines the identity, artifact store, state transitions, transcript contract, wait policy, and escalation boundary used by later specification-review and implementation-code-review requirements.

## Scope for v0.11.0 review exchange core

The v0.11.0 outcomes are:

1. One canonical requestor capability can derive and manage review artifacts for both review families.
2. Request and answer publication follows a deterministic, fail-closed state machine.
3. Every review round produces an append-only, role-and-round-labeled transcript entry.
4. Bounded waits, stagnation, disagreement, interruption, and inconsistent state have observable outcomes.
5. LLM-specific wrappers can reference one canonical instruction without embedding the exchange protocol repeatedly.
6. Intermediate change-request rounds remain automated, while convergence requires a durable human confirmation before the owning workflow continues.

Everything else is supporting design context for those outcomes or explicitly deferred.

### In scope for v0.11.0 review exchange core

- Review-mode configuration from the root `a.review-mode` marker.
- Review identity validation and artifact-path derivation.
- One active exchange per reviewed document, with concurrency across different documents.
- Root request, root answer, sibling transcript, and active-round coordination state.
- Safe request and answer transitions, exact-file waiting, and transcript append.
- Timed-out, abandoned, no-progress, disagreement, inconsistent-state, and human-recovery outcomes.
- Convergence-only `awaiting-human-confirmation`, role-neutral confirmation outcomes, and mandatory summary identity.
- The canonical review-requestor instruction, its own wrapper, shared templates, and shared utility interface.

### Deferred from v0.11.0 review exchange core to later umbrella items

- Integration into `review-ask-questions` and `consolidate-then-review-ask-questions`.
- The `spec-reviewer` role and its specification-specific request and answer wording.
- Integration into `implement-step` and its `a.commit` continuation decisions.
- The `code-reviewer` role, code repair behavior, and `implementation-check` usage.
- User-facing Diataxis documentation for the complete review-mode workflows.

---

## Confirmed technical facts for v0.11.0 review exchange core

**The canonical project-root discovery for general tools is `tools._models.find_project_root`**: it is exported as `tools.find_project_root` and used by `prompt_workflow`, `open_questions_md`, and other repository tools. `tools.coverage_gap_functions_shared.find_project_root` is a separate coverage-tool helper and is not the review core's dependency. The review core can operate on the calling project rather than assume that llm-shared itself is the project root.

**The `pw` launcher self-locates**: `bin/prompt_workflow.bat` derives `LLM_SHARED_DIR` from its own path and invokes the llm-shared virtual-environment Python by absolute path. A review wrapper can follow the same launcher contract without environment activation.

**Documentation layout discovery already supports the required locations**: `tools.prompt_workflow_docs.docs_dirs_for_version` recognizes `docs/`, `docs/vX.Y/`, `docs/vX.Y.Z/`, and `docs/vX.Y/vX.Y.Z/`. `resolve_document` fails closed when more than one exact document matches.

**Transient coordination files are ignored here**: the repository `.gitignore` contains `a.*`, matching the required project-root request, answer, and coordination files.

**Canonical adapters are intentionally thin**: entries under `.agents/llm-shared/instructions/` contain one reference to the corresponding canonical instruction under `instructions/`.

**No review-exchange core exists yet**: the current `tools`, `instructions`, `templates`, `bin`, and tests contain no `review-mode`, `review-requested`, or `review-answer` handling.

---

## Current behavior for v0.11.0 review exchange core

Writer workflows reach a human-review stop. No shared service owns review identity, transient artifacts, transcript history, waiting, or recovery.

```txt
writer skill
  -> existing human-review stop
  -> no canonical request artifact
  -> no reviewer handoff state
  -> no bounded automated continuation
```

## Target behavior for v0.11.0 review exchange core

The specialized writer and reviewer roles supply feedback content and owning-workflow decisions. The core owns only the exchange protocol.

```txt
writer adapter
  -> canonical review-requestor instruction
  -> derive validated exchange identity and paths
  -> publish request and transcript entry
  -> wait for exact answer

reviewer adapter
  -> wait for exact request
  -> produce specialized feedback
  -> consume request, publish answer, append transcript

requestor
  -> classify answer as changes requested or convergence recommended
  -> apply intermediate changes and start another automated round
  -> at convergence, retain answer and await explicit human confirmation
  -> continue owning workflow or start another round from confirmed choice
```

---

## Identity and configuration design for v0.11.0 review exchange core

### Canonical exchange identity

The core represents every exchange with one validated identity record.

| Field | Specification family | Implementation-code family |
| --- | --- | --- |
| Review family | `specification` | `code` |
| Document type token | `feature-request`, `issue`, `design-specification`, or `plan` | Fixed `code` token |
| Version | `vX.Y.Z` from the reviewed document | `vX.Y.Z` from the reviewed plan |
| Slug | Reviewed document topic | Reviewed plan topic |
| Document path | Exact resolved source document | Exact resolved plan |

Every exchange context also carries an optional umbrella path. When present, it must resolve to an existing umbrella draft; when absent, human-readable summaries render `Umbrella draft: none`. Code-review context additionally carries the implementation-step identifier. These context fields are validated but do not change the artifact identity key.

The document path is resolved first and remains authoritative. The core derives the transcript beside that path and the transient artifacts at the discovered project root. Slugs must satisfy the existing lowercase letter, digit, hyphen, and underscore rule.

For document resolution, the `design-specification` protocol type token maps to the repository's `design.vX.Y.Z.<slug>.md` source-document prefix, while every review artifact retains the full `design-specification` token.

Only one active identity may target a given resolved document path. Different paths can proceed concurrently. A second exchange for the same document fails before it overwrites or consumes any artifact.

### Review-mode marker contract

An absent `a.review-mode` means review mode is disabled. An empty marker enables review mode with the documented default wait limit of 1,800 seconds.

The marker accepts one optional line:

```text
wait_timeout_seconds=<positive integer>
```

Unknown keys, duplicate keys, non-integer values, and non-positive values are invalid configuration. Invalid configuration stops review-mode activation with a diagnostic and leaves existing artifacts unchanged.

### Derived path contract

| Purpose | Derived location |
| --- | --- |
| Specification transcript | `<document-parent>/review.<type>.vX.Y.Z.<slug>.md` |
| Specification request | `<project-root>/a.review-requested.<type>.vX.Y.Z.<slug>.md` |
| Specification answer | `<project-root>/a.review-answer.<type>.vX.Y.Z.<slug>.md` |
| Code transcript | `<plan-parent>/review.code.vX.Y.Z.<slug>.md` |
| Code request | `<project-root>/a.review-requested.code.vX.Y.Z.<slug>.md` |
| Code answer | `<project-root>/a.review-answer.code.vX.Y.Z.<slug>.md` |
| Durable coordination record | `<project-root>/a.review-active.<family>.<type-token>.vX.Y.Z.<slug>.md` |
| Consumed-request tombstone | `<project-root>/a.review-consumed.<family>.<type-token>.vX.Y.Z.<slug>.md` |
| Human recovery archive | `<project-root>/a.review-archive.<family>.<type-token>.vX.Y.Z.<slug>.<YYYYMMDD-HHMMSS>.<artifact-kind>.md` |

Every derived transient coordination path uses the `a.review-` prefix. Review-mode activation requires a Git repository and verifies through Git's effective ignore resolution that every derived transient path is ignored. Activation fails with a diagnostic outside a Git repository or when any derived transient path is not ignored. This accepts any effective ignore rule, not only a literal `a.*` entry.

For the code family, the family and fixed type token intentionally repeat, for example `a.review-active.code.code.v0.11.0.review-exchange-core.md`. Archive `<artifact-kind>` is exactly `request`, `answer`, `consumed`, or `coordination`. The consumed-request tombstone has one stable name per identity and therefore has no timestamp.

The durable coordination record is a coordination primitive, not a fifth review-content artifact. It starts with an H1 identity title followed by a first `## JSON` section. That section's fenced JSON block records:

- `status`: `active`, `awaiting-human-confirmation`, or `escalated`, with an escalation reason when applicable.
- Lease owner, expected next actor (`requestor`, `reviewer`, or `human`), round number, and lease-renewed local timestamp with numeric UTC offset.
- Previous-round progress as `reviewed_work_changed` and `convergence_recommended`, plus the current no-progress streak.
- Whether the dedicated clarification round has already run.
- Any incomplete-transition kind and stable transcript-entry identifier.
- Optional umbrella path, exact reviewed-document path, and implementation step when applicable.
- Confirmed display label, role-neutral outcome, confirmation timestamp, and optional human guidance when a convergence choice has been recorded.

The lease TTL equals the effective wait limit. Only state-changing core operations renew it; waiting polls never renew it. No separate heartbeat runs while an LLM is authoring feedback. `awaiting-human-confirmation` suspends lease expiry, and `escalated` carries no active lease.

Short operating-system locks protect only individual read, validate, and write transitions for one identity. They are never held while waiting for another LLM process or across the complete exchange.

---

## Artifact and state design for v0.11.0 review exchange core

### Review-content envelope

Request and answer templates produce UTF-8 Markdown that starts with one H1 title. The first section is `## JSON`, and its fenced JSON metadata identifies the exchange identity, optional umbrella path, exact reviewed-document path, implementation step when applicable, role, round number, and creation time. Answer metadata also declares `changes-requested` or `convergence-recommended` through the convergence signal registered by the specialized family. Exactly that first JSON section is parsed; later fenced blocks belong to role-authored content. Specialized requirements own the H2 feedback sections and conclusions after the metadata section.

Every request's human-readable summary repeats the umbrella or `none`, exact specification or plan, implementation step when applicable, and round. The core validates those values against the JSON envelope and coordination context before publication and fails closed on mismatch.

Fixed template conclusions and file-handling instructions are coordination boilerplate. Role-authored analysis, decisions, recommendations, and response summaries are substantive content copied to the transcript.

### Observable exchange states

| Request | Answer | Tombstone | Coordination | Lease | State | Core outcome |
| --- | --- | --- | --- | --- | --- | --- |
| Absent | Absent | Absent | Absent | Absent | Idle | A new round may start. |
| Absent | Absent | Absent | `active` | Current | Round in progress | The current actor may publish a request or complete post-answer work. |
| Present | Absent | Absent | `active` | Current | Request pending | The expected reviewer may consume the exact request. |
| Absent | Absent | Present | `active` with incomplete marker | Current | Answer publication in progress | The transition may publish or repair the prepared answer. |
| Absent | Present | Present | `active` with incomplete marker | Current | Transcript repair pending | Only this identity is blocked until its transcript append succeeds idempotently. |
| Absent | Present | Absent | `active` | Current | Answer pending | The expected requestor may consume the exact answer. |
| Absent | Present | Absent | `awaiting-human-confirmation` with no confirmed outcome | Suspended | Convergence gate | Retain the answer and re-present the human choices across sessions. |
| Absent | Present | Absent | `awaiting-human-confirmation` with confirmed `continue-owning-workflow` | Suspended | Owning action pending | Retain the answer and re-report the confirmed authorization idempotently without asking the human again. |
| Any | Any | Any | `escalated` with reason | None | Escalated, awaiting human resolution | Preserve everything, append no duplicate escalation, and wait for human resolution. |
| Absent | Absent | Absent | `active` | Expired or absent | Abandoned mid-round | Preserve coordination state; the expected actor may reclaim by lease renewal, or a human may explicitly force completion with a durable close decision. |
| Absent | Absent | Present | `active` or missing | Expired or absent | Interrupted answer publication | Preserve the tombstone and escalate for human recovery. |
| Absent | Present | Present | `active` with incomplete marker | Expired or absent | Interrupted transcript append | Preserve both artifacts and repair the exact identity before continuation. |
| Present | Absent | Absent | `active` or missing | Expired or absent | Abandoned request | Preserve state; with active coordination the expected actor may reclaim by lease renewal, otherwise append escalation and require human resolution. |
| Absent | Present | Absent | `active` or missing | Expired or absent | Abandoned answer | Preserve state; with active coordination the expected actor may reclaim by lease renewal, otherwise append escalation and require human resolution. |
| Present | Present | Any | Any non-escalated value | Any | Inconsistent | Fail closed and escalate without deleting evidence. |

Any artifact shape not listed in the table is inconsistent, fails closed, and escalates with all evidence preserved. An incomplete-transition marker overlays any listed row and blocks that exchange identity until its idempotent transcript repair succeeds, so no underlying row permits consumption past a pending append. Lease validity is computed from the persisted renewal timestamp plus the effective wait limit. An active wait that reaches its own monotonic deadline records a timed-out outcome in the waiting flow. A later operation that discovers an expired active lease detects abandonment. Before any escalation is recorded, the returning expected actor may reclaim an intact abandoned round through the reclaim operation, which renews the lease in place and changes no artifact or transcript content; once escalation is durable, only human resolution starts a fresh round. The expected-next-actor field identifies whose inaction ended the round. A retained convergence answer is never abandoned while coordination status is `awaiting-human-confirmation`.

### Safe publication transitions

All new request and answer content is completed in a same-directory temporary file before it becomes visible under its final name. Publication replaces the final path only after the complete UTF-8 content is ready.

The state transitions are:

1. Start round: take the short identity lock, validate that no matching state conflicts with the new round, and create active coordination with the requestor owner, reviewer as expected next actor, round number, progress state, clarification state, and renewed lease.
2. Publish request: under the short lock, set the request-transcript incomplete marker before the first mutation, remove a stale matching answer, publish the complete request, append the requestor transcript entry idempotently, clear the marker, and renew the lease.
3. Publish answer: under the short lock, verify the exact request identity, prepare the answer completely, and set the answer-transcript incomplete marker before the first mutation. Atomically rename the matching request to the consumed-request tombstone, publish the answer, append the reviewer transcript entry idempotently, remove the tombstone, clear the marker, and persist the answer disposition. For `changes-requested`, set the requestor as expected next actor and renew the lease. For `convergence-recommended`, retain the answer, set status to `awaiting-human-confirmation`, set the expected next actor to human, and suspend lease expiry.
4. Read and act on answer: take a short lock to read and verify the exact answer, then release it. Apply or assess the feedback outside any lock. For an intermediate answer, take a new short lock, delete the consumed answer, persist the round's progress flags, and renew the lease before continuing. A crash before deletion leaves the answer safely pending for re-consumption. A convergence answer is retained for the human gate.
5. Continue automated round: publish a new request with the requestor response summary, increment the round, set the reviewer as expected next actor, and renew the lease. Two consecutive `reviewed_work_changed: false` change-request rounds trigger no-progress escalation; convergence exits the automated loop instead. Persist whether the dedicated clarification round has already run.
6. Record escalation: under the short lock, set the escalation-transcript incomplete marker before changing status, set status to `escalated` with its reason, append the escalation entry idempotently, clear the marker, and stop renewing the lease. Observing an already-escalated exchange appends nothing new.
7. Record human confirmation or resolution: under the short lock, set the human-transcript incomplete marker before persisting the human choice or resolution, append its transcript entry idempotently, then clear the marker. Confirmation handling follows the convergence transitions below; escalation resolution follows the fresh-round recovery flow.
8. Complete exchange: remove the coordination record only after the human-authorized owning action succeeds and no incomplete transition remains. As a separate recovery, a human may force completion only for an artifact-free `abandoned-mid-round`; the core marks and appends that close decision idempotently before removing coordination, without asserting convergence or authorizing new owning work.
9. Reclaim abandoned round: under the short lock, verify the round is abandoned or still live with active coordination and no incomplete marker, then renew the lease in place and change nothing else. Escalated, confirming, interrupted, and inconsistent exchanges cannot be reclaimed.

Renaming the matching request path to the tombstone satisfies the delete-before-answer rule because the matching request path disappears before the answer becomes visible. The tombstone preserves the exact consumed evidence until answer publication and transcript append are durable.

If request publication stops before the request file becomes visible, the requestor repairs the marked round by re-running publication with the same round and stable transcript-entry identity; create-or-overwrite publication and the idempotent append make regeneration of its own request safe. The answer envelope's `convergence-recommended` declaration is authoritative when publication succeeded but coordination disposition persistence did not, so answer consumption retains that answer and restores the convergence gate instead of treating it as an intermediate answer.

Every transition that appends to the transcript sets its identity-scoped incomplete marker before its first mutation and clears it only after the idempotent append succeeds. An operation validates the identity encoded in an existing transient artifact before reading, replacing, or deleting it. A mismatch never falls back to the nearest file name. An incomplete-transition marker blocks only its exchange identity; exchanges for other reviewed documents continue normally.

---

## Transcript design for v0.11.0 review exchange core

### Transcript initialization

The core initializes a missing transcript from the template selected by review family and version. An existing transcript is preserved. Initialization records the reviewed document reference and exchange identity but contains no fabricated review round.

### Append-only review entries

Each appended entry has this logical shape. Code-review request and answer
identifiers include the implementation step before the round, so different
steps in one plan never count as restarted exchanges. When the same document
and step start a new exchange, request and answer headings append
`(exchange <n>)` and their stable entry identifiers append `-exchange-<n>` so
round numbering can restart without colliding with earlier history.

```md
## Round <n> by <requestor-or-reviewer> - Step <identifier when applicable>

- Recorded: <local ISO-8601 timestamp with numeric UTC offset, such as 2026-08-03T14:30:05+02:00>
- Exchange: <family>/<type-token>/vX.Y.Z/<slug>
- Umbrella: <validated path or none>
- Reviewed document: <exact specification or plan path>
- Implementation step: <identifier when applicable>
- Outcome: <request, answer, escalation, human-confirmation, human-completion, human-reclaim, or human-resolution>

<complete substantive role-authored content>
```

The core serializes appends under the identity's short operating-system lock. Agents pass the new entry to the core and do not read historical transcript content. Each entry has a stable identity and is appended idempotently, so repair cannot duplicate a completed round. This preserves the transcript's documentation-only purpose while making round order, no-progress evidence, and escalation history human-verifiable. A requestor-only legacy repair may replace the final entry while its request is still pending when an older renderer produced a repeated exchange identity; the durable request remains unchanged, the existing incomplete-transition marker makes replacement crash-repairable, and no earlier entry is rewritten.

For implementation-code review, the implementation step is appended to every
round heading. This keeps headings unique when one transcript records rounds
for multiple implementation steps and preserves the `MD024` duplicate-heading
check.

---

## Waiting, termination, and recovery design for v0.11.0 review exchange core

### Exact and bounded waiting

Waiting polls only the fully derived counterpart path and validates its embedded identity before reporting success. The active process uses a monotonic clock for its deadline. It reports `active` while the effective deadline remains and `timed-out` once the configured duration expires with the counterpart absent.

Only state-changing core operations renew the coordination lease for the full effective wait limit and record the renewal in local system time as ISO-8601 with a numeric UTC offset. Waiting polls do not renew. No heartbeat is required while an LLM is authoring. A later operation reports `abandoned` when it finds matching transient state with expired active coordination; already-escalated and awaiting-confirmation states are excluded. The returning expected actor may renew such an expired lease in place through the reclaim operation while the round's evidence remains intact and no escalation has been recorded.

The wait operation exposes short progress intervals to the host so an agent can remain communicative during a long review. It never replaces a bounded wait with an indefinite shell or terminal prompt.

### Progress and disagreement policy

The specialized requestor reports whether a completed change-request round substantively changed the reviewed work. The core persists that flag and the current no-progress streak. Two consecutive unchanged change-request rounds cause a no-progress escalation. A convergence recommendation exits the automated loop at the confirmation gate and does not participate in no-progress counting.

An explicit disagreement permits one round labeled `clarification`. If the roles still disagree after that round, the core records an escalation and stops automation.

### Convergence confirmation and durable re-presentation

Each specialized family registers a machine-readable convergence signal and two display labels mapped to the role-neutral outcomes `another-round` and `continue-owning-workflow`. The core never interprets recommendation prose and never lets a reviewer invoke confirmation.

At convergence, the answer is retained, coordination status becomes `awaiting-human-confirmation`, the expected next actor becomes human, and lease expiry is suspended. A later `pw` session re-presents the validated identity-bearing summary, reviewer recommendation, requestor assessment, and registered choices instead of treating the exchange as abandoned.

The host collects an explicit choice and calls the core confirmation operation. No new transient confirmation artifact is created. The core validates the display label against the registered family and current state, then persists the label, generic outcome, confirmation timestamp in local ISO-8601 with numeric offset, and optional human guidance in coordination and transcript.

For `another-round`, the core records the override, resets no-progress counters, includes optional human guidance in the replacement request summary, deletes the retained answer after the transition is durable, changes status to `active`, increments the round, sets the requestor as current owner and reviewer as expected next actor, and starts a fresh automated round. For `continue-owning-workflow`, the core returns explicit authorization to the specialized requestor; after the owning action succeeds, it deletes the retained answer and completes the exchange. Human cancellation changes the exchange to `escalated` and records the cancellation through the escalation-resolution path.

### Human escalation and fresh resumption

An abandoned round whose evidence is intact may first be reclaimed by the returning expected actor through in-place lease renewal; escalation is recorded only when nobody reclaims the round. Timeout, abandonment, no-progress, persistent disagreement, and inconsistent state all preserve matching transient evidence and append an escalation entry. The coordination record retains the escalation and no longer grants an active lease after that record is durable.

A human resolves which evidence is authoritative and moves stopped transient evidence to identity-and-timestamp-named `a.review-archive.*` paths or explicitly clears it. Archive names use compact local `YYYYMMDD-HHMMSS` timestamps because Windows file names cannot contain colons. The transcript records the exact archive names with an unambiguous local timestamp and numeric UTC offset.

The core does not resume the old transition. It starts a new round with a new coordination lease and appends a human-resolution entry containing the resolution summary before the new requestor entry.

---

## File-based IO cost clarification for v0.11.0 review exchange core

The utility accepts the exact reviewed-document path and materializes its derived-path set once, so normal operations use direct file checks rather than documentation-tree or project-root scans. Each wait poll performs constant work against only the expected artifact and coordination record; it never reads the transcript or scans for neighboring review files. Transcript initialization is one existence check; append and repair may seek to a bounded tail to verify the stable entry identifier without loading transcript history, then use append-only writes under the identity lock. Git-ignore activation validates the constant derived transient set in one bounded call. Human recovery is outside the polling path and touches only the fixed artifacts belonging to the selected identity.

---

## Canonical role and adapter boundary for v0.11.0 review exchange core

### Core-owned surfaces

The core owns one canonical review-requestor instruction, its own thin LLM-specific wrapper, shared request-generation templates, and one non-interactive utility interface for identity, lifecycle, transcript, wait, status, and recovery operations.

The wrapper only locates and delegates to the canonical instruction. The instruction tells the LLM when to call protocol operations and what role-authored content to supply; it does not reproduce state-machine rules that belong to the utility contract.

### Later adapter responsibilities

The later `review-ask-questions`, `consolidate-then-review-ask-questions`, and `implement-step` integrations decide when their writer workflow enters review mode and how they perform the human-authorized owning action. The later `spec-reviewer` and `code-reviewer` adapters own evaluation behavior and emit the registered convergence signal. The specification family maps `another-round` and `continue-owning-workflow` to `Revise and review again` and `Consolidate`; the code family maps them to `Rework and review again` and `Commit`. All five consume the same core identity, summary, and lifecycle surfaces.

---

## Design decisions for v0.11.0 review exchange core

| Question | Accepted design | Arguments | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q01 | Store durable lease metadata in the coordination record and use short operating-system locks only for transitions. | Separate LLM processes need shared ownership state; lease TTL equals the wait limit and only state-changing operations renew it. | Identity and configuration; artifact and state; waiting | Whole-exchange OS lock; artifact-only ownership inference |
| Q02 | Key coordination by the complete readable identity tuple, including document type token. | It matches request and answer identities and keeps recovery state human-diagnosable. | Derived path contract | Canonical-path hash; sibling coordination record |
| Q03 | Rename the request atomically to a consumed-request tombstone before answer publication. | The matching path disappears in the required order while exact evidence survives a crash. | Derived path contract; observable states; publication transitions | Direct deletion; copy request content into the coordination record |
| Q04 | Start machine-readable Markdown with an H1 title, put strict metadata in the first `## JSON` section, and parse exactly that section. | The document remains valid Markdown, standard-library JSON parsing stays unambiguous, and later fences remain role-authored content. | Review-content envelope | Leading fenced block; Markdown bullets; YAML front matter |
| Q05 | Use monotonic time for active deadlines and local ISO-8601 timestamps with numeric offsets for persisted records. | Deadline behavior resists clock corrections while humans read familiar unambiguous local time. | Transcript; waiting; recovery | UTC everywhere; no time-based state |
| Q06 | Preserve published artifacts, mark transcript append incomplete for that identity, and repair idempotently before it advances. | Feedback is not rolled back and audit completeness remains mandatory without blocking unrelated exchanges. | Observable states; transitions; transcript | Warning-only append failure; artifact rollback |
| Q07 | Fail activation outside Git or when any derived transient path is not effectively ignored. | Complete substantive feedback must not become commit-visible through a missing protection rule. | Derived path contract | Warning only; assume ignore coverage |
| Q08 | Archive stopped evidence under timestamped, identity-scoped `a.review-archive.*` paths before a fresh round. | The live namespace becomes clean while exact evidence and the human resolution remain auditable. | Human escalation and recovery | Delete evidence; overwrite active names |
| Q09 | Capture a host-native explicit choice through a core confirmation operation and persist its display label and role-neutral outcome. | The core stays role-neutral, reviewers stay advisory, and confirmation survives process boundaries without another transient artifact. | Convergence confirmation; adapter boundary | Chat-only confirmation; new confirmation file |
| Q10 | Suspend lease expiry only in durable `awaiting-human-confirmation` and re-present the gate across sessions. | Automated rounds remain bounded while normal human review can take as long as needed without becoming abandonment. | Observable states; convergence confirmation; waiting | Continue lease expiry; use a separate human timeout |
| Q11 | Carry an optional validated umbrella path and render `none` when absent. | Every summary can identify its collection context without making an umbrella mandatory or inferring it unreliably. | Canonical identity context; content envelope; transcript | Require an umbrella; infer from branch or document search |

---

## Acceptance cases for v0.11.0 review exchange core

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| Marker absent | Review mode remains disabled and no artifact changes. | Opt-in behavior must preserve existing workflows. |
| Empty marker | Review mode uses the 1,800-second default. | The feature works without configuration. |
| Valid timeout override | The positive marker value becomes the bounded wait. | Projects can adapt review latency. |
| Invalid marker content | Activation fails without changing artifacts. | Invalid termination behavior must not run silently. |
| Activation outside Git | Activation fails with a diagnostic and creates no review artifacts. | Ignore protection cannot be verified outside Git. |
| Derived transient not ignored | Activation fails before writing any transient content. | Review feedback must not become commit-visible. |
| Two different documents | Both exchanges may hold independent leases and use separate transition locks. | Concurrency is safe across document identities. |
| Second exchange for one document | The second start is rejected before publication. | Current names support one authoritative dialogue per document. |
| Code-family coordination path | The derived path contains the intentional `code.code` family and type-token pair. | Implementers must not collapse two distinct identity fields. |
| Request for one slug while waiting for another | The unrelated request is ignored. | Exact identity prevents cross-review contamination. |
| Invalid request-summary identity | Publication fails before writing the request or transcript. | Human-readable and machine-readable identity must agree. |
| Current lease with no artifacts | The exchange is reported as a valid round in progress. | Work may occur between artifact transitions. |
| Expired lease with no artifacts | The exchange is reported abandoned mid-round and escalates with the expected actor identified. | A crash after consuming an answer remains observable. |
| Answer publication | The request is renamed to the tombstone before the complete answer appears. | The matching request path disappears in the normative order while evidence survives. |
| Process stops after request rename | The tombstone remains, lease expiry exposes interrupted publication, and automation escalates. | The destructive crash window is recoverable. |
| Process stops after answer publication | The answer and tombstone remain with an incomplete marker until idempotent transcript repair succeeds. | Published feedback and missing audit history are both preserved. |
| Process stops after answer consumption | The coordination record alone becomes an abandoned mid-round state after lease expiry. | Consuming an answer cannot erase recovery evidence. |
| Answer applied before deletion | Application occurs outside any lock; a crash leaves the answer pending for safe re-consumption. | Long-running role work must not hold a transition lock. |
| Both request and answer present | Evidence is preserved and automation escalates. | The core must fail closed on contradictory state. |
| Writer or reviewer session interrupted | The durable lease expires and the next core operation reports the expected actor's round as abandoned. | Separate processes require persisted abandonment evidence. |
| Abandoned round reclaimed before escalation | The returning expected actor renews the lease in place and the live round continues with all evidence unchanged. | A slow authoring session must not force a fresh round while its evidence is intact. |
| Counterpart absent past deadline | State is timed out, preserved, and recorded. | Automated waiting is bounded. |
| Waiting poll | The poll does not renew the lease. | A dead expected actor must become abandoned within one effective wait window. |
| Two unchanged change-request rounds | No-progress escalation stops the exchange. | Stagnant automated dialogue must terminate. |
| Convergence recommendation | The automated loop ends at the durable confirmation gate regardless of the prior progress flags. | Convergence is not another change-request round. |
| Disagreement survives clarification | Human escalation replaces further automated debate. | Conflict receives one bounded correction attempt. |
| Transcript append | Entry includes identity, role, round, outcome, and complete substantive content. | Humans can verify dialogue and recovery history. |
| Transcript append failure | Only the affected identity is blocked and its stable entry can be repaired without duplication. | Other documents remain independent while audit integrity is restored. |
| Already-escalated exchange observed | No duplicate escalation is appended and the exchange remains awaiting human resolution. | Escalation must be idempotent. |
| Intermediate change-request answer | The requestor applies it and starts the next round without a human wait. | Human confirmation is convergence-only. |
| Convergence answer | The answer is retained, status becomes `awaiting-human-confirmation`, the expected actor becomes human, and lease expiry is suspended. | The human decides with the complete recommendation still present. |
| Later session finds a convergence gate | The pending identity-bearing summary and registered choices are re-presented. | Confirmation survives process exit without becoming abandonment. |
| Session stops after continuing confirmation | The next session re-reports the persisted `continue-owning-workflow` authorization without asking the human again, and retains the answer until the owning action completes. | A completed human decision is idempotent across an interrupted owning action. |
| Reviewer attempts to continue workflow | The operation is rejected because only a human can confirm the registered choice. | Reviewer recommendations remain advisory. |
| Human chooses another round with guidance | The choice and optional guidance are recorded, no-progress state resets, the retained answer is consumed, and the replacement request summary includes the guidance. | A human override creates a meaningful fresh round. |
| Human chooses the continuing outcome | The owning workflow may perform its confirmed consolidation or commit action, then consume the retained answer. | Continuing work requires explicit authorization. |
| Human cancels at convergence | Cancellation is recorded and the exchange follows the human-resolution path. | An indefinite gate has an explicit human exit. |
| Persisted timestamp | Transcript, lease, escalation, and archive records use local ISO-8601 time with numeric offset. | Human-readable time remains unambiguous across DST changes. |
| Human resolves escalation | Stopped state is cleared or archived and a fresh round records the resolution. | Ambiguous state cannot silently regain authority. |
