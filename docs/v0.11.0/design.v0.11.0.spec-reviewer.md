# Design v0.11.0 -- Specification Review Responder

Reference feature request:
[feature-request.v0.11.0.spec-reviewer.md](feature-request.v0.11.0.spec-reviewer.md)

---

## Context for v0.11.0 specification review responses

The review exchange core and specification requestor already publish validated
question-review requests and retain writer authority across repeated rounds.
This design adds the complementary independent reviewer role. It divides live
`pw` routing between writer and reviewer states, defines a pure paired answer
surface, and uses the existing exchange lifecycle for waiting, publication,
transcript append, recovery, and escalation.

## Scope for v0.11.0 specification review responses

The v0.11.0 outcomes are:

1. A pending specification request routes to one dedicated `spec-reviewer`
   role, while writer-owned states continue to route to
   `spec-review-requestor`.
2. The reviewer validates one exact request and assesses the full current
   specification without taking document-edit or consolidation authority.
3. One pure renderer produces matching answer-artifact and transcript-summary
   content for either supported reviewer disposition.
4. Shared answer publication removes the consumed request and appends reviewer
   feedback exactly once through the core's recoverable transition.
5. Timeout, marker suspension, lease reclaim, human recovery, and retained
   assessment behavior preserve evidence without publishing stale identity.
6. Routing and review operations keep a constant exact-path candidate set and
   never read transcript history.

Everything else is supporting design context for those outcomes or explicitly
deferred.

### In scope for v0.11.0 specification review responses

- The canonical specification reviewer role and thin host adapters.
- Ordinary and explicitly forced `pw` routing for the reviewer role.
- Exact pending-request wait and identity validation.
- Full-document question assessment and human-guidance handling.
- Paired reviewer answer rendering and publication through the shared command.
- Requestor-side cold-route reclaim, reviewer-side in-session lease reclaim,
  and stopped-round assessment retention.
- Requestor answer-wait use of the configured full review timeout.
- Focused tests for routing, rendering, publication, recovery, authority, and
  bounded IO.

### Deferred from v0.11.0 specification review responses to later umbrella items

- Writer-side code review requests and implementation-step integration.
- The independent implementation code reviewer.
- Final explanation, tutorial, how-to, and reference documentation for all
  review-mode roles.
- Reviewer editing or consolidation of the reviewed specification.
- Queueing or load balancing across several simultaneous pending requests.

---

## Confirmed technical facts for v0.11.0 specification review responses

These facts were confirmed from the current codebase before writing this
design.

**The shared core already reserves reviewer operations**:
`review_exchange_cli.py` exposes `wait-request` and `publish-answer`, and
`ReviewExchangeCore.publish_answer` validates a reviewer envelope before the
store makes the answer visible, appends one reviewer transcript entry, and
consumes the request through a recoverable transition.

**Specification identity mapping is already canonical**: the exchange accepts
`feature-request`, `issue`, `design-specification`, and `plan`; a source
`design` document maps to `design-specification`, while the other three tokens
remain unchanged. Artifact paths derive from one exact document, optional
umbrella, version, and slug.

**Current live routing is requestor-only**:
`prompt_workflow_skill.next_command` asks
`prompt_workflow_review.live_specification_document` for one live document and
always renders `spec-review-requestor`. The route observer already rejects
several live candidates and avoids transcript reads, but it does not expose the
observed state to role selection.

**Forced specification routing is also requestor-only**:
`prompt_workflow_skill.forced_command` recognizes
`spec-review-requestor`, and `forced_specification_document` returns one live
document or one exact question-bearing document. There is no corresponding
`spec-reviewer` branch constrained to a pending request.

**The marker is a global operation gate**: `ReviewConfiguration.load` returns
`enabled=False` when `a.review-mode` is absent. Routing then returns no review
document, and launcher operations return the established disabled result. The
marker optionally supplies one positive `wait_timeout_seconds` value and
defaults to 1,800 seconds.

**Caller wait overrides currently supersede the marker**:
`ReviewExchangeCore.wait_for_exact` uses an explicit positive timeout when one
is passed and otherwise uses `configuration.wait_timeout_seconds`. The
specification requestor therefore gets the policy-sized wait by omitting a
shorter override.

**The requestor already establishes the paired-renderer pattern**:
`spec_review_request` accepts exact ignored assessment inputs and returns a
complete request plus a substantive transcript summary without mutating
exchange artifacts. The reviewer can mirror that boundary with its own answer
input and renderer.

**Shared instructions already separate role authority**:
`review-requestor.md` reserves `wait-request` and `publish-answer` for a
specialized reviewer adapter. `spec-review-requestor.md` retains specification
edits, intermediate answer consumption, convergence presentation, durable
human confirmation, consolidation, and final exchange completion.

---

## Current behavior for v0.11.0 specification review responses

The writer can publish a correct request, but `pw` routes every live state back
to that same writer role. An independent reviewer has no canonical instruction,
rendering surface, or routed command.

```txt
question workflow
  -> spec-review-requestor
  -> publish request
  -> request-pending
  -> pw skill
  -> spec-review-requestor again
  -> wait-answer
  -> no specialized reviewer route
```

A reviewer can call the shared core manually, but no specialized boundary
defines full-document assessment, disposition criteria, paired content,
human-guidance response, or retained-assessment recovery.

## Target behavior for v0.11.0 specification review responses

The live route becomes state-aware. The reviewer owns only pending-request
assessment and answer publication; the requestor owns every writer action and
all convergence continuation.

```txt
spec-review-requestor publishes request
  -> request-pending
  -> pw skill selects spec-reviewer
  -> reviewer waits for and validates exact request
  -> reviewer reads full current specification
  -> reviewer renders answer + transcript summary
  -> shared publish-answer transition
     -> answer visible
     -> reviewer summary appended once
     -> request consumed
  -> answer-pending or convergence-gate
  -> pw skill selects spec-review-requestor
```

When a cold routing decision observes an intact abandoned request, role
selection returns it to the requestor for reclaim. Reclaim restores
`request-pending`, after which the ordinary route returns to `spec-reviewer`.
When a reviewer already holding the round expires its lease during assessment,
that same reviewer may reclaim in-session and continue toward publication.
When the exchange is escalated, only human resolution can create a fresh round;
the reviewer revalidates any retained assessment before republication.

---

## State-aware routing design for v0.11.0 specification responses

### One live route with one owning role

The review observer continues to derive the same fixed candidate contexts and
to reject more than one live route. Its selected route is one immutable value
containing both the exact document context and observed artifact state. Role
selection is then a pure mapping over that coherent observation, without a
second classification read:

| Observed state | Routed role | Reason |
| --- | --- | --- |
| `request-pending` | `spec-reviewer` | A published request awaits independent assessment. |
| `abandoned-request` | `spec-review-requestor` | On a cold route, the writer-side coordinator reclaims the stale request before reviewer routing resumes. |
| `round-in-progress` | `spec-review-requestor` | The writer still owns request rendering or continuation. |
| `answer-pending` | `spec-review-requestor` | The writer assesses and consumes reviewer feedback. |
| `convergence-gate` | `spec-review-requestor` | Only the writer presents the human decision. |
| `owning-action-pending` | `spec-review-requestor` | The writer completes authorized consolidation. |
| `abandoned-answer` or `abandoned-mid-round` | `spec-review-requestor` | Recovery resumes the persisted writer action. |
| `escalated` or repair-required state | `spec-review-requestor` | Human recovery and protocol repair remain outside reviewer authority. |
| `idle` or `disabled` | No live route | Ordinary document routing or marker behavior applies. |

This mapping changes only the selected role. Candidate discovery, multiple-live
diagnostics, host prefix rendering, topic selection, and transcript avoidance
remain shared.

### Explicit specification reviewer route

An explicit `pw skill spec-reviewer` route accepts only one exact live
specification exchange whose state is `request-pending`. It does not start a
new exchange from an open-question document: activation remains the writer's
responsibility. An exact `abandoned-request` routes to the requestor reclaim
path before the reviewer can be selected again.

When there is no sole pending request, the explicit route returns no command or
the same exact-candidate diagnostic used by ordinary routing. It never chooses
the oldest request, prompts inside the router, or falls back to a nearby
question-bearing document.

### Marker suspension across role routing

Both ordinary and explicit reviewer routes load the same review configuration
before observing candidates. With no marker, they return no review command even
when coordination evidence exists. Restoring the marker makes that existing
state visible again; it does not create a new round or mutate retained
artifacts.

## Reviewer orchestration design for v0.11.0 specification responses

### Exact invocation context and pending-request wait

The canonical reviewer instruction receives one reviewed document path from
`pw`, derives the optional umbrella from the current effort, and registers the
fixed specification policy:

```text
family: specification
convergence signal: consolidation-ready
another-round label: Revise and review again
owning-workflow label: Consolidate
```

That instruction owns waiting, assessment orchestration, recovery, and shared
publication calls. The specialized paired renderer remains pure: it validates
caller-authored inputs and formats both outputs, but never waits, reasons about
the specification, or invokes the exchange core.

It calls the shared status surface before acting. A valid
`request-pending` state proceeds to one bounded `wait-request`; if the request
is already visible, that wait returns immediately. If that reviewer session's
lease expires during assessment, the session may reclaim its intact
`abandoned-request` while its reviewer ownership remains authoritative and then
continue. A cold reviewer route observing the same state instead stops with the
requestor reclaim handoff. Disabled, mismatched, interrupted, escalated, or
repair-required state stops with the shared diagnostic.

The requestor's complementary `wait-answer` invocation omits a shorter
`--timeout-seconds` argument and uses the marker's configured full-review
limit. Progress output remains diagnostic only and does not become another
polling loop.

### Reviewer and human authority boundary

The reviewer may observe status, wait for the exact request, reclaim one intact
reviewer-owned abandoned request, render its response, and publish the answer.
It may not consume an answer, continue a round, confirm convergence, complete
the exchange, or consolidate the specification.

`cancel`, `resolve`, and `archive` remain human-authority actions. The reviewer
reports the stopped state and retains its caller-owned assessment; it never
turns a timeout into permission to start a fresh round itself.

| Action | Reviewer | Requestor | Human |
| --- | --- | --- | --- |
| Wait for exact request | owns | no | no |
| Assess specification | owns | no | no |
| Reclaim expired in-session reviewer lease | owns | no | no |
| Reclaim an abandoned request from a cold route | no | owns | no |
| Publish answer | owns | no | no |
| Edit specification | no | owns | may guide |
| Consume intermediate answer | no | owns | no |
| Confirm convergence | no | presents choice | owns choice |
| Cancel, resolve, or archive | reports only | reports only | owns |
| Consolidate and complete | no | owns after authorization | authorizes |

## Independent assessment design for v0.11.0 specification responses

### Full current document as review source

The reviewer reads the complete current specification and the validated
request, with the request and open-question section as the focus. This is
necessary to find decisions that the writer failed to express as questions.
The versioned transcript is never review input.

Current document content is authoritative. When the request summary describes
older text, the reviewer evaluates the current document and records the drift
as `changes-requested`. It does not reject every concurrent edit and does not
review obsolete request text in preference to current source.

### Question and answer assessment model

The assessment covers missing, redundant, unclear, or out-of-scope questions;
distinct options and their consequences; recommendation quality; the answer the
reviewer would choose; and concrete replacement wording when evidence supports
it. When evidence cannot support a correction, the answer states that limit
instead of inventing content.

A request whose current document has no open question receives
`changes-requested`, directing the writer to settle or cancel the inconsistent
round. A defect belonging to an earlier document or outside the selected scope
is named precisely and returned to the writer for correction or rerouting.
Repeated unchanged disagreement remains governed by the shared no-progress
limits.

### Human guidance and independent judgment

Replacement requests can contain one literal `Human guidance:` block. The
reviewer addresses it explicitly and keeps its response separate from the
writer's preceding response. Guidance informs the assessment but cannot
override artifact identity, protocol safety, or the selected document boundary.

The reviewer remains independent: it can disagree with the writer's proposed
answers or human preference, but it must state the reason and choose the
disposition that truthfully reflects remaining substantive work.

## Paired answer design for v0.11.0 specification responses

### One typed assessment input and two outputs

The reviewer renderer receives one validated specification context, positive
round number, disposition, and separate ignored UTF-8 inputs for its assessment,
writer instructions, and optional response to human guidance. It returns a
complete answer artifact and a substantive transcript summary from the same
typed source.

The caller selects separate ignored root output paths. Rendering reads every
caller-owned input once, produces both Markdown values in memory, validates
their required identity, and writes the two outputs. It does not read the
transcript or mutate request, answer, coordination, tombstone, or lock files.

### Answer Markdown and identity

The complete answer starts with one H1 title. Its first section is `## JSON`
with a reviewer envelope containing one supported disposition. A focused
specification-reviewer template layers the role-specific sections on the
generic review-answer envelope and heading contract without copying those
protocol rules. Later top-level authored sections start at H2 and include:

- the exact umbrella or `none`, reviewed specification, and review round;
- the independent assessment and per-question verdicts;
- concrete requested changes or convergence wording;
- an explicit response to human guidance when present; and
- one final reviewer decision.

The human-readable identity fields appear exactly once and match the envelope.
The transcript summary contains the same substantive findings without the
artifact envelope. A shared answer template supplies stable structure, while
the specialized renderer owns specification-specific wording.

### Disposition boundary

`changes-requested` applies whenever an in-scope decision, missing question,
unsupported answer, cross-document correction, disagreement, or more than
wording-only change remains. It gives the writer concrete work or an explicit
statement that the available evidence is insufficient. The typed renderer
input requires a requested-changes section for this disposition.

`convergence-recommended` applies only when every in-scope decision is settled
and no more than wording-only edits remain. It never confirms consolidation.
The requestor applies covered wording, retains the answer, and presents the
human convergence gate. The typed renderer input requires covered-wording and
convergence-rationale sections for this disposition.

## Publication and recovery design for v0.11.0 specification responses

### Shared answer publication transition

The reviewer passes the complete answer and transcript summary to
`publish-answer` with the exact context and registered policy. The core
revalidates the envelope and summary, records the transition marker, removes
the request before answer visibility, appends the transcript entry once, and
clears the marker when publication completes.

An interrupted publication is repaired by replaying the same idempotent shared
operation. The specialized reviewer never deletes the request, writes the
answer, or appends the transcript independently, and never interprets partial
visibility as permission to start another round.

### Retained assessment after stopped-round recovery

If the exchange escalates after assessment but before publication, the
reviewer keeps its assessment, instructions, disposition rationale, and
guidance response in caller-owned ignored files. It reports the exact stopped
state and waits for human `resolve` or `archive`.

Those files include one ignored retained-context manifest containing a SHA-256
digest of the assessed working-tree bytes, the original request identity and
round, and the assessment input paths. The manifest covers uncommitted content
that a Git blob identifier cannot represent.

Human recovery creates a fresh round. The reviewer then reads the fresh
request, revalidates envelope and human-readable identity, rereads the current
specification, and compares both with the retained findings. With no material
drift, it renders the same findings under the fresh round identity. With drift,
it updates the assessment before rendering. It never publishes a cached answer
whose round or content context is stale.

After retained findings are republished, the reviewer removes the single-use
manifest so later work cannot mistake it for a current retained assessment.

## File and trust boundaries for v0.11.0 specification responses

Normal routing derives at most the requirement, design, and plan contexts for
one topic, then checks their fixed artifact sets. It rejects `glob`, `rglob`,
`iterdir`, recursive documentation enumeration, and transcript reads.

The reviewer reads only the exact current specification, validated request,
coordination state, and effectively ignored caller inputs. All caller inputs
and renderer outputs must be project-root `a.*` files, UTF-8 encoded, regular
files, and effectively ignored by Git. The shared command performs protocol
mutation under its transition lock with atomic writes.

No answer content, human guidance, or specification Markdown is treated as a
path or command. Context paths come from validated command arguments and the
canonical identity mapping, not from authored reviewer text.

## File-based IO cost clarification for v0.11.0 specification responses

- Routing observes at most the requirement, design, and plan exchange paths for
  the resolved topic; it performs no directory or transcript scan.
- Review reads the exact request, specification, coordination state, and
  caller-owned inputs a constant number of times.
- The pure renderer creates both outputs in memory; the shared publication
  transition owns atomic answer, request, and transcript mutation.
- Recovery reuses one exact ignored manifest and rereads only the fresh request
  and current specification before retiring that manifest after publication.

## Design decisions for v0.11.0 specification review responses

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Carry exact context and observed state in one immutable live-route value. | State-aware routing design | Separate state lookup or reclassification would permit inconsistent snapshots and duplicate IO. |
| Q02 | Fail closed from a cold forced reviewer route and direct reclaim to the requestor; preserve in-session reviewer reclaim of its own expired lease. | State-aware routing and reviewer orchestration | Silent role substitution or cold reviewer reclaim would blur entry-path authority. |
| Q03 | Keep orchestration in the reviewer instruction and answer formatting in a pure paired renderer backed by the shared exchange. | Reviewer orchestration and paired answer design | A monolithic executable or renderer-owned publication would duplicate reasoning and protocol state transitions. |
| Q04 | Layer a focused specification-reviewer template on the generic answer contract. | Answer Markdown and identity | Generic-only structure leaves reviewer sections implicit; copying the full contract creates drift. |
| Q05 | Retain a single-use ignored manifest with SHA-256 content and exchange identity, then remove it after republication. | Retained assessment after stopped-round recovery | Reassessment without a digest cannot prove unchanged content; Git blobs omit uncommitted reviewed text. |
| Q06 | Enforce the full configured answer wait in the specialized requestor by omitting its timeout override. | Exact invocation context and pending-request wait | Clamping the shared CLI would remove intentional short waits used by other callers and tests. |
| Q07 | Require a separate ignored guidance-response input whenever the request contains human guidance. | Human guidance and paired answer design | Folding it into assessment hides omission; renderer synthesis crosses the formatting boundary. |
| Q08 | Validate disposition-specific required content in the typed renderer input. | Disposition boundary | Free-form or inferred disposition can publish an authoritative answer without actionable instructions or rationale. |

---

## Acceptance cases for v0.11.0 specification responses

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| One feature-request request is pending | `pw` routes `spec-reviewer` to that exact document. | Pending work belongs to the independent reviewer. |
| One issue request is pending | The reviewer preserves the `issue` artifact token. | Source and artifact types are identical. |
| One design request is pending | The reviewer maps source `design` to `design-specification`. | The core owns the canonical mapping. |
| One plan request is pending | The reviewer preserves the `plan` artifact token. | Specification plan review is distinct from code review. |
| Two specification requests are live for one topic | Routing fails closed and lists both exact identities and paths. | No timestamp or directory order has authority. |
| Live state is `answer-pending` | `pw` routes `spec-review-requestor`. | The writer owns answer handling. |
| A cold route observes `abandoned-request` | The requestor reclaims it, then pending routing reaches the reviewer. | Cold stale-route recovery precedes reviewer work. |
| Marker is absent with a live request | Routing and launchers return disabled without deleting evidence. | The marker is a global gate. |
| Marker is restored | The same retained live state becomes routable again. | Marker restoration does not invent a round. |
| Explicit reviewer route has no pending request | No reviewer command is returned. | The reviewer never activates writer work. |
| Request identity mismatches the document | Review stops before assessment or publication. | Nearby artifacts cannot substitute for exact authority. |
| Current document differs from request wording | Reviewer assesses current text and requests changes for drift. | Current repository content is authoritative. |
| Current document has no open question | Reviewer requests writer settlement or cancellation. | Absence of questions does not prove successful review. |
| Human guidance is present | Answer addresses it explicitly without crossing safety or scope boundaries. | Durable human input must have visible effect. |
| Substantive question gap remains | Answer disposition is `changes-requested`. | Another automated writer round is required. |
| Only wording edits remain | Answer disposition may be `convergence-recommended`. | The requestor still owns the human gate. |
| Answer publication succeeds | Request disappears, answer becomes visible, and transcript gains one reviewer entry. | One shared transition owns all three effects. |
| Answer publication is interrupted | Replaying the same publication repairs it without duplicate transcript content. | Core transitions are idempotent. |
| Reviewer lease expires intact during assessment | The same reviewer reclaims the request and round in-session. | Reclaim renews existing reviewer ownership without changing evidence. |
| Round escalates after assessment | Reviewer retains findings and stops for human recovery. | Timeout invalidates ownership, not reasoning. |
| Human recovery creates a fresh round | Reviewer revalidates request and document before republishing retained findings. | Fresh identity cannot accept a cached stale answer. |
| Requestor waits for answer | It uses the marker's full configured timeout. | A shortened caller wait must not manufacture escalation. |
| Directory scans or transcript reads are attempted | The acceptance test fails. | Runtime work stays independent of document and history count. |
