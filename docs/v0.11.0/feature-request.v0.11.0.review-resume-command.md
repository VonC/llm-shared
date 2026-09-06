# Resume interrupted reviews from their durable LLM role

## CDC revision that introduces review resumption

The earlier review-mode CDC defines durable specification and implementation
exchanges, requestor and reviewer roles, restart-safe coordination evidence,
and a read-only review-status command. It does not provide one LLM-native entry
point that can recover the current role and continue its work after an
interruption.

The revised CDC assigns the final `review-resume-command` umbrella item a
cross-cutting update. Runtime review artifacts move below a configurable
repository-local directory, exchanges trace the LLM nature acting in each
role, review status can migrate legacy evidence before observing it, and a
resume skill continues as requestor or reviewer from durable state.

## User story for review resumption

As a Claude, Codex, or Gemini session returning to a repository, I want one
resume skill to locate or migrate review evidence, determine which role I am
continuing, validate or complete that role's LLM trace, and immediately wait or
act according to the protocol, so I do not have to reconstruct an interrupted
exchange or manually choose its next workflow command.

## Current behavior in v0.11.0

- Protocol-owned runtime review artifacts are written directly below
  `PRJ_DIR`; there is no shared configurable artifact-home resolver with a
  `<PRJ_DIR>/.reviews` default.
- Existing review artifacts can remain at the repository root, and there is no
  fast migration preflight that distinguishes an already-correct layout from a
  safe migration or a blocking collision.
- Review status is strictly observational and cannot move legacy artifacts
  before collecting status.
- Exchanges record protocol roles but do not consistently record whether
  Claude, Codex, or Gemini acted as requestor or reviewer.
- Legacy artifacts without LLM nature and newer identity-bearing artifacts do
  not share one compatibility and backfill policy.
- There is no LLM-only resume skill that can select a role, wait, reclaim, act,
  or hand a requestor back to `pw skill`.

## Gap to close for configurable review evidence

1. Resolve every protocol-owned runtime review artifact through one
   configurable repository-local directory whose default is
   `<PRJ_DIR>/.reviews`.
2. Provide a migration tool that moves every recognized legacy review artifact
   stored directly in `PRJ_DIR` into the resolved directory.
3. Cover request, answer, coordination, lease, lock, tombstone, consumption,
   and every other artifact recognized by the shared exchange protocol.
4. Preserve durable identity during migration and refuse a collision, damaged
   layout, or ambiguous destination instead of overwriting evidence.
5. Update the shared exchange, requestor, reviewer, status, documentation, and
   test behavior delivered by completed umbrella items without reopening their
   completed documents or status rows.

Only protocol-owned runtime artifacts move into the artifact home. Versioned
`docs/.../review.*.md` transcripts remain beside their reviewed documents. One
dedicated versioned repository declaration carries the artifact-home setting;
session environment variables and resume or status arguments cannot override
it. The declaration's exact file name and syntax are left to design. A declared
path must resolve inside the repository and must not name an existing tracked
directory.

Creating an artifact home also creates a home-local `.gitignore` before any
runtime artifact is written or moved. That generated ignore file is itself
untracked under its own rule. An existing home without effective ignore
coverage is a blocking layout and is not repaired silently during preflight.

## Required migration preflight

A fast `migration_check` tool must report one of these settled outcomes before
resume or migration-capable status collection continues:

- all recognized traces and artifacts are already under the configured or
  default artifact home;
- recognized legacy root artifacts require migration;
- a collision, damaged layout, or ambiguity prevents a safe migration
  decision.

The check must not perform the full review-status projection merely to decide
artifact placement.

The check inspects only the recognized legacy project-root location, the
default `.reviews` home, and the configured home. Migration validates the
complete move before changing any path and then moves every artifact or none;
one collision blocks the whole move and leaves the source layout intact.

Every resume invocation must run `migration_check` before it reads status or
selects a role. When migration is required, resume runs the migration tool and
repeats the check. A failed second check or blocking diagnostic stops the
resume attempt.

Review status, including the repository command `rvw_status` and its local
`rwst` alias, must be able to run the same check and migration. This bounded
preflight mutation is the only exception to the prior strictly read-only status
contract. Once the check passes, normal discovery, projection, and rendering
remain read-only. Status reports whether migration was unnecessary, completed,
or blocked.

Ordinary review status performs a safe required migration automatically. Its
typed result advances the schema version and carries a migration record for the
unnecessary and completed cases. A blocked layout returns the existing
operational-failure outcome with a migration diagnostic because no trustworthy
status projection can follow.

## Required LLM nature trace

The shared host detector must determine whether the current session is Claude,
Codex, or Gemini from host evidence when possible. When detection is not
possible, it records an explicit unknown or unavailable result rather than
choosing a host silently.

Every new exchange must durably trace the LLM nature acting as requestor and
the LLM nature acting as reviewer. Requests, answers, coordination
transitions, status projections, and continuation instructions preserve those
role-specific identities. Human-readable and machine-readable review status
both report them.

Migration moves old evidence but does not invent an LLM nature. Legacy
identity completion belongs to the role-aware artifact policy below.

## Legacy and identity-bearing artifact policy

Readers must accept both legacy artifacts without LLM nature and newer
artifacts that record it. Artifact kind and durable exchange identity determine
which protocol role authored each artifact.

Before continuing a resolved role, resume scans every artifact in the selected
exchange attributed to that role. It classifies each artifact as:

- missing LLM nature;
- matching the detected current LLM;
- recording a different LLM nature.

When none records a different nature, resume updates all missing-nature
artifacts attributed to the current role so they record the detected current
LLM. The update covers every missing-nature artifact attributed to that role in
the selected exchange occurrence, not only the first legacy artifact the
workflow happens to read. Already matching artifacts remain unchanged.

When any current-role artifact records a different nature, resume stops before
performing any missing-nature backfill and shows every conflicting artifact
path, the role, each recorded nature, and the current nature. It presents only:

- `Override` -- continue as the current LLM for the role and complete the
  missing-nature backfill while preserving every conflicting recorded value as
  evidence;
- `Stop` -- make no identity change and end the resume attempt.

Override never rewrites an existing conflicting LLM nature.

Override authority lasts only for the current resume attempt. A later resume
re-evaluates the preserved discrepancy and requires a new decision when it is
still present.

Artifacts authored by the counterpart role remain readable. When their LLM
nature is missing, the reader ignores that missing field and leaves the
artifact unchanged. A counterpart artifact carrying a different nature is
expected and does not block the current role.

## Resume skill and role selection

Resume is a public LLM skill with a shared implementation and host-specific
adapters. It must not add a CMD, batch, or repository-root `rvw_resume`
command, because continuation requires an active LLM session.

The skill supports specification requestor, specification reviewer,
implementation code-review requestor, and implementation code reviewer roles.
It resolves the role as follows:

1. Detect the current LLM nature and compare it with the durable requestor and
   reviewer traces.
2. When the trace identifies the current LLM as one role, select that role
   without asking the human to choose.
3. When legacy trace evidence contains no LLM nature and no role argument was
   passed, ask whether the session resumes as `requestor` or `reviewer`.
4. Accept an explicit `requestor` or `reviewer` argument without that role
   question when no LLM nature exists.
5. When the forced role conflicts with a known LLM-role trace, show the
   mismatch and require explicit confirmation before applying the override.
6. A matching role argument does not bypass the role-wide artifact identity
   scan or its `Override` or `Stop` decision.

When both role traces identify the detected current LLM and no role argument
was passed, resume asks whether to continue as requestor or reviewer. When host
detection returns unknown or unavailable, resume can continue after role
selection but does not backfill that weak value into legacy artifacts; missing
natures remain available for a later known LLM to complete.

Once the role and artifact identity gates are resolved, resume continues
without another confirmation.

## Reviewer continuation behavior

A resumed reviewer has exactly two protocol outcomes:

- When a review request exists, renew or reclaim its exact identity, round,
  occurrence, and lease as needed, assess it, and publish the matching answer.
- When nothing is available to review, including when no exchange or
  implementation step has started and no live request artifact exists, enter a
  global reviewer wait for any new specification- or code-review request
  artifact in the configured review directory. The future document, family,
  slug, step, round, and occurrence do not need to be known before the wait
  starts. An idle exchange, an exchange that has concluded, and a live exchange
  whose next action belongs to the requestor or to the human convergence gate
  are all valid wait entry points, and none may be rejected merely because the
  existing exchange-specific `wait-request` operation has no concrete identity
  to target. The wait wakes on the next request artifact whether it belongs to
  the same exchange resuming at a later round or occurrence, or to an exchange
  that did not exist when the wait started.

A reviewer resume never runs `pw skill`, starts writer work, or advances a
requestor workflow. Its open-ended wait wakes only for review-request
artifacts, not unrelated review files.

The global reviewer wait remains active until a request arrives or the human
cancels it; exchange timeout rules begin only after a concrete request exists.
If several requests are observed together, resume lists them and asks the human
to select one instead of inventing an ordering or processing a queue.

The global wait is one foreground script operation, not an LLM polling loop. It
uses non-mutating discovery for notification hints, bounded fallback polling,
and authoritative candidate rescans; only the selected reviewer path claims a
request. It writes no idle progress to the LLM and returns one final machine
result when it finds or claims a request, reaches ambiguity, or is cancelled.
A graceful host or console interruption is cancellation. The final result has
`operation`, `outcome`, `identity`, `candidates`, and `diagnostic`; `found`
also carries the session-only ownership capability. The command exits 0 for
`found`, 3 for `ambiguous` or `cancelled`, and 2 for invalid input or an
operational failure. It creates no persistent waiter record or cancellation
artifact.

## Requestor continuation behavior

A resumed requestor follows the durable workflow state:

- When a review is in progress and its response has not arrived, start or
  restart the wait for the matching review-answer artifact.
- When the requestor owns the next review action, renew or reclaim the exact
  identity, round, occurrence, and lease as needed; consume an answer, apply
  requested work, publish a later request, or continue to the human convergence
  gate.
- When no review is in progress and no further request remains for the current
  task, run `pw skill` and immediately follow the command it returns.

The `pw skill` result may continue writing, implementation, a later task that
will publish its own review request, or any other workflow selected from the
repository's durable state. No second go-ahead is requested after role and
identity resolution.

## Recovery safety and protocol boundaries

- Direct human invocation of resume authorizes lease-independent pickup even
  when the recorded lease has not expired and without waiting for
  `wait_timeout_seconds`.
- Waiting, renewal, reclaim, and action preserve the exact exchange identity,
  family, reviewed document, umbrella, step when applicable, round,
  occurrence, artifacts, expected actor, and next action.
- Malformed, repair-required, escalated, artifact-inconsistent, or ambiguous
  multiple-exchange states stop with typed review-status evidence rather than
  a guessed continuation.
- Ordinary automated rounds, reviewer recommendations, and the durable
  `awaiting-human-confirmation` convergence gate retain their existing
  authority rules.
- Repeating resume against the same durable state is idempotent.
- Design must specify how a session displaced by lease-independent pickup is
  rejected on its next transition. This deferred point does not change the
  requirement-level pickup authority.

## File-based IO cost clarification for review resumption

- Artifact-home resolution reads one small versioned declaration per workflow
  invocation and must not load every review artifact to derive one path.
- `migration_check` inspects only the project root, default home, and configured
  home without recursive repository discovery or full status projection.
- Status performs at most one bounded migration preflight before its ordinary
  read-only projection.
- Selected-role identity completion scans only one exchange occurrence, and the
  global reviewer wait treats file notifications as hints with bounded polling
  rather than repeatedly projecting all review state.

## Acceptance criteria for review resumption

1. With no configuration, every new runtime review artifact is placed below
   `<PRJ_DIR>/.reviews`.
2. With a configured artifact home, every producer, consumer, waiter, status
   reader, migration tool, and resume path uses that same resolved directory.
3. `migration_check` quickly distinguishes ready, migration-required, and
   blocked layouts without collecting the full status model.
4. Resume always runs the migration check first, migrates recognized misplaced
   evidence when safe, repeats the check, and refuses to continue on an unsafe
   or incomplete result.
5. Review status and `rvw_status` can perform and report the same bounded
   migration; after the preflight they remain observational.
6. New exchanges trace Claude, Codex, Gemini, or an explicit unknown result for
   both requestor and reviewer roles, and status exposes those values in human
   and machine output.
7. A selected role with only matching or missing identities backfills every
   missing-nature artifact attributed to that role before continuing.
8. A single conflicting identity prevents partial backfill and presents the
   complete conflict set with `Override` and `Stop` choices.
9. Override preserves conflicting values, fills only missing current-role
   identities, and continues; Stop leaves all identity evidence unchanged.
10. A counterpart-role artifact without LLM nature remains readable and
    unchanged.
11. Missing trace nature with no role argument prompts for requestor or
    reviewer; an explicit role supplies that choice, subject to known-trace
    conflict confirmation.
12. A reviewer with a request reclaims and answers it; a reviewer without one
    waits globally for any future specification- or code-review request
    artifact without requiring its identity. That wait is entered before any
    exchange or implementation step starts, after the reviewer's own exchange
    has concluded, while the exchange's next action belongs to the requestor,
    and while the reviewer is parked at a convergence gate; in the last two
    cases it wakes on the replacement request when the requestor publishes it
    or when the human chooses another round.
13. A requestor waits for an in-progress answer, performs owned review work, or
    runs and follows `pw skill` when no review remains.
14. Once role and identity gates pass, resume acts or waits without another
    confirmation.
15. All affected tests from the shared exchange, requestor, reviewer,
    review-status, adapter, waiting, and documentation topics are updated for
    the artifact-home and LLM-nature rules. The canonical review-status
    instruction and published skill description are updated to replace their
    strictly read-only wording with the bounded migration exception.
16. Creation of an artifact home establishes effective Git ignore coverage
    before any artifact moves into it, and migration preflight blocks a home
    whose required coverage is absent.
17. One versioned repository declaration carries the artifact-home setting;
    invalid locations outside the repository and existing tracked directories
    are rejected.
18. The typed status result distinguishes migration that was unnecessary from
    migration that completed, advances its schema version, and reports a
    blocked migration as an operational failure with a diagnostic.
19. The foreground global wait is silent while idle; graceful host or console
    cancellation returns exactly one typed result with the stated fields and
    exit mapping, without an ownership capability or persistent waiter state.

## Scope boundaries and dependencies

This effort depends on `review-exchange-core`, `review-status-command`,
`spec-review-requestor`, `spec-reviewer`, `code-review-requestor`,
`code-reviewer`, and `review-mode-docs`.

The implementation updates their shared code and affected tests through this
topic. It does not reopen their completed requirement, design, plan, validation
documents, or umbrella statuses. It does not create a shell resume command,
weaken the convergence-only human authority gate, overwrite conflicting LLM
identity evidence, or treat counterpart missing identity as damage.

This effort supersedes two rules the umbrella draft states for earlier items:
runtime protocol artifacts no longer stay directly at the project root under
the `a.*` ignore rule, and the resume entry point is an LLM skill rather than
the repository-root `rvw_resume` command the umbrella originally regrouped for
this item, because continuation requires an active LLM session. The umbrella
draft is updated with both revisions; no completed requirement, design, plan,
validation document, or completed umbrella row is reopened.

## Requirement clarifications

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Move runtime protocol artifacts only; keep versioned transcripts beside reviewed documents. | Gap to close for configurable review evidence | Moving transcripts too; configuring runtime and transcript homes separately. |
| Q02 | Check only `PRJ_DIR`, default `.reviews`, and the configured home. | Required migration preflight | Root-only inspection; recursive repository scans. |
| Q03 | Use one durable repository setting with no session override. | Gap to close for configurable review evidence | Environment overrides; per-command path arguments. |
| Q04 | Let ordinary `rvw_status` perform and report safe migration automatically. | Required migration preflight | Explicit migration mode; status that only reports a migration command. |
| Q05 | Validate first, then migrate every artifact or none. | Required migration preflight | Partial moves; retaining duplicate source and destination artifacts. |
| Q06 | Ask for a role when both role traces match the current LLM. | Resume skill and role selection | Selecting the next actor; requiring a new invocation with an argument. |
| Q07 | Continue by selected role when LLM nature is unknown, without backfilling `unknown`. | Resume skill and role selection | Durable unknown backfill; refusing unsupported hosts. |
| Q08 | Backfill current-role artifacts only in the selected exchange occurrence. | Legacy and identity-bearing artifact policy | All occurrences for one document; repository-wide backfill. |
| Q09 | Apply an identity discrepancy override only to the current resume attempt. | Legacy and identity-bearing artifact policy | Persistent occurrence authority; replacing conflicting evidence. |
| Q10 | Keep a global reviewer wait active from idle, concluded, requestor-owned, and convergence-gate states until a same-exchange or new-exchange request arrives or the human cancels. | Reviewer continuation behavior | Exchange timeout before a request exists; idle-only entry; one-shot polling. |
| Q11 | List concurrent requests and ask the human to select one. | Reviewer continuation behavior | Oldest-first selection; automatic queue processing. |
| Q12 | Create an untracked home-local `.gitignore` before first use; block an existing uncovered home. | Gap to close for configurable review evidence | Root `.gitignore` rewrites; bypassing effective-ignore validation. |
| Q13 | Carry the home in a dedicated versioned declaration and reject external or tracked-directory targets. | Gap to close for configurable review evidence | Ignored per-clone marker; unrelated project settings file. |
| Q14 | Advance the typed status schema, record successful migration state, and use operational failure when blocked. | Required migration preflight | Failure-only reporting without typed success state; human-readable reporting only. |
| Q15 | Treat a graceful foreground host or console interruption as `cancelled`, with one typed final result and fixed exit mapping. | Token-quiet global reviewer wait | LLM polling loops; streamed progress; durable waiter state in this topic. |
