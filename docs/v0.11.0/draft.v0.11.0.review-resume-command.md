# Resume interrupted reviews

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Interrupted review recovery need

Review exchanges can outlive a shell, terminal, VPN connection, computer
session, or prompt context. A human needs one skill that resumes the exact
durable exchange without reconstructing its family, reviewed document, actor,
round, occurrence, artifacts, or next action from memory.

The recovery entry point must build on the typed review-status result. After
the migration preflight passes, status discovery remains read-only; resumption
is the explicit human-authorized orchestration action that waits for work or
renews or reclaims the selected exchange and continues the correct role in the
current LLM session.

## Configurable review-artifact home and migration

Every protocol-owned runtime review artifact must live below one configurable
repository-local review-artifact directory. The default is
`<PRJ_DIR>/.reviews`; callers and skills must use the configured path through
one shared resolver rather than assume that artifacts live directly below
`PRJ_DIR`.

The effort must provide a migration tool that finds existing review artifacts
stored directly in `PRJ_DIR` and moves them into the configured directory, or
the default directory when no override exists. Migration must cover the
request, answer, coordination, lease, lock, tombstone, consumption, and other
protocol-owned review files recognized by the shared exchange implementation.
It must preserve their durable identity and refuse an ambiguous or destructive
collision rather than overwrite evidence.

A fast `migration_check` tool must determine whether every recognized review
trace and artifact is already under the configured or default directory,
whether legacy root artifacts require migration, or whether a collision or
damaged layout blocks a safe decision. It must avoid performing the full
status projection merely to answer that location question.

Every resume invocation must call `migration_check` before it reads status or
selects a role. When the check finds recognized traces or artifacts outside the
configured or default directory, resume must invoke the migration tool and
then repeat the check before continuing. A blocked or still-incomplete check
stops resume with its evidence.

Review status, including `rwst`, must use the same check and be able to invoke
the same migration. This bounded preflight migration is an explicit exception
to the earlier strictly read-only status contract; after artifacts are in the
resolved directory, ordinary status discovery and rendering remain read-only.
Status output must report whether no migration was needed, migration ran, or a
migration problem prevented a trustworthy result.

This path change affects the shared exchange, requestor, reviewer, status, and
documentation behavior delivered by earlier umbrella items. This topic owns
the shared-code update and the corresponding updates to every affected test;
the already completed topic documents and their status rows remain unchanged.

## LLM identity in every exchange

An LLM session must be able to determine whether it is running as Claude,
Codex, or Gemini, using host environment evidence where available. The shared
identity resolver must record an explicit unknown or unavailable result when
the host cannot be detected instead of silently choosing one.

Every exchange must durably trace the LLM identity acting as requestor and the
LLM identity acting as reviewer. Each later request, answer, coordination
transition, status projection, and continuation must preserve that trace.
Review status, including the `rwst` entry point, must report the specific LLM
known for each role as part of both its human-readable and machine-readable
result.

Existing artifacts may lack this identity because they predate the trace. That
absence is a legacy state the resume skill handles explicitly. Migration moves
the evidence but must not invent an LLM identity for old traces.

## Legacy and traced artifact compatibility

The shared readers must process both legacy artifacts with no recorded LLM
nature and newer artifacts that carry one. Before applying identity rules, the
reader determines which protocol role authored the artifact from its artifact
kind and durable exchange identity.

Before continuing as a resolved role, the resume instruction must inspect all
artifacts in the selected exchange that durable protocol identity attributes
to that role. It must classify every one as missing LLM nature, matching the
current LLM, or recording a different LLM.

If none records a different LLM, update every artifact attributed to the
current role whose nature is missing so it records the detected current LLM.
This is one role-wide legacy backfill, not an opportunistic update of whichever
artifact happened to be read first. Artifacts whose nature already matches are
left unchanged.

If even one current-role artifact records a different LLM nature, stop before
performing any missing-nature backfill. Show every conflicting artifact path,
the common role, each recorded nature, and the current nature, then ask the
human to choose:

- `Override` -- continue as the current LLM for that role and complete the
  missing-nature backfill, while preserving every conflicting recorded nature
  as evidence;
- `Stop` -- make no identity change and end the resume attempt.

The override authorizes the discrepant role continuation; it never silently
rewrites a conflicting recorded LLM nature.

When the artifact was authored by the other role, a missing LLM nature is not
an error. Read the artifact, leave it unchanged, and ignore only that missing
identity field. A different recorded nature on the other role's artifact is
also expected and does not block reading it.

This role-bounded backfill is distinct from artifact migration. Migration
moves evidence without inventing identity; the resume workflow may add the
detected nature only to missing-nature artifacts that durable role evidence
attributes to the current LLM role.

## Settled scope

This effort regroups a public LLM resume skill, the shared implementation it
invokes, configurable artifact-path resolution and migration, LLM host
detection and durable participant traces, the status-to-role routing needed to
resume either side of specification and code review, and self-contained
host-specific continuation instructions for the current session.

Resume is intentionally a skill-only entry point. The effort must not add a
CMD, batch, or repository-root `rvw_resume` command because role continuation
only makes sense inside an active LLM session.

The implementation covers these continuing roles:

- specification review requestor;
- specification reviewer;
- implementation code-review requestor;
- implementation code reviewer.

## Resume role resolution and override

By default, the resume skill detects the current LLM kind and compares it with
the durable requestor and reviewer traces. When the trace identifies the
current LLM as one role, resume continues that role without asking the human to
choose between requestor and reviewer.

When the existing trace does not include the LLM nature and the caller passed
no role argument, the skill must ask whether the current session resumes as
requestor or reviewer. It must not guess from the exchange's next action or
from which artifact currently exists.

After that role is selected, the legacy-artifact rules apply: missing nature on
all artifacts authored by the selected role is backfilled together after the
role-wide discrepancy scan, while missing nature on artifacts authored by the
counterpart is ignored.

A trace that includes LLM nature but does not match the current LLM is not
treated as missing. When it belongs to the role being resumed, stop and ask the
human to choose `Override` or `Stop`; a matching role argument alone does not
make the recorded LLM mismatch safe.

The skill accepts a role argument that forces `requestor` or `reviewer`. When
that argument conflicts with the role recorded for the current LLM in the
exchange trace, the skill must show the mismatch and require explicit human
confirmation before it applies the override. When legacy evidence contains no
LLM nature, the explicit argument supplies the role without a separate role
question because there is no recorded LLM-role mapping to contradict it. Role
override confirmation does not suppress the separate role-wide artifact scan
or its `Override` or `Stop` decision.

After the role is resolved and the role-wide identity scan either passes or
receives `Override`, resume must proceed without another confirmation. The only
identity gates are a forced role argument that conflicts with a known role
trace and the `Override` or `Stop` decision for conflicting current-role
artifact natures.

## Role-specific waiting, reclaiming, and acting

Resume means continuing the role's complete protocol behavior, not merely
printing a command or reporting status:

### Reviewer continuation

- When a review request exists for the reviewer, renew or reclaim its exact
  round and occurrence, assess it, and publish the matching answer.
- When there is nothing more to review, including when no exchange or
  implementation step has started and no live request artifact exists, enter a
  global reviewer wait for any new specification- or code-review request
  artifact in the configured review directory. The reviewer does not need to
  know the future document, family, slug, step, round, or occurrence before it
  begins that wait. An idle exchange, an exchange that has concluded, and a
  live exchange whose next action belongs to the requestor or to the human
  convergence gate are therefore all valid wait entry points, and none may be
  rejected merely because `wait-request` has no concrete exchange identity yet.
  The wait wakes on the next request artifact whether it belongs to the same
  exchange resuming at a later round or occurrence, or to an exchange that did
  not exist when the wait started.
- A reviewer resume either waits or answers. It never runs `pw skill`, starts
  writer work, or advances a requestor workflow.

### Requestor continuation

- When a review is in progress and its response has not arrived, start or
  restart the wait for the matching review-answer artifact (even when the action
  is abandoned or not reclaimed: trust the reviewer will do the necessary work,
  like a reclaim: you just start the wait for a response).
- When the requestor owns the next review action, renew or reclaim the exact
  round and occurrence, consume the answer when present, apply requested work,
  publish another request when required, or continue to the human convergence
  gate.
- When no review is in progress and no further request remains to be made for
  the current task, run `pw skill` and immediately follow the command it
  returns.
- The `pw skill` continuation may resume writing, implementation, a later task
  that will request its own review, or any other workflow selected from the
  repository's durable state. A requestor resume continues that workflow
  without asking for a second go-ahead.

The wait must observe the configured artifact home and apply the same durable
identity, damage, ambiguity, and termination rules as the existing review
protocol. An open-ended reviewer wait watches specifically for new request
artifacts; it does not wake on unrelated review files.

## Recovery boundary

Interruption recovery is a human-invoked orchestration action over an existing
exchange, not reviewer judgment or requestor authorship. Keeping it separate
prevents either role instruction from guessing identity or reconstructing
protocol context.

The resume skill consumes the typed review-status result rather than scraping
human output or rediscovering protocol state independently. It does not
replace the requestor, reviewer, status, or human-convergence workflows.

## Concrete recovery rules

- Resolve every runtime artifact through the configured review directory,
  whose default is `<PRJ_DIR>/.reviews`.
- Run `migration_check` before resume or status discovery. Migrate recognized
  misplaced traces and artifacts, repeat the check, and stop on a collision or
  damaged layout that prevents a safe move.
- When exactly one intact exchange is resumable, preserve that same identity,
  round, occurrence, artifacts, expected actor, participant traces, and next
  action while waiting, renewing, or reclaiming as required.
- Direct human invocation of the resume skill authorizes lease-independent
  pickup, even when the current lease has not expired and without waiting for
  `wait_timeout_seconds` or escalating.
- Preserve every durable artifact and identity field while resuming.
- Detect Claude, Codex, or Gemini when host evidence is available and compare
  that identity with the role trace before selecting the continuation.
- Process both legacy artifacts with no LLM nature and newer traced artifacts.
  Scan every artifact authored by the current role, then backfill the detected
  nature into all missing-nature artifacts for that role as one operation; do
  not modify counterpart-role artifacts merely because their nature is
  missing.
- If any current-role artifact records a different LLM nature, stop before
  backfill, list every discrepancy, and ask for `Override` or `Stop`. Override
  preserves the conflicting values while allowing the missing-nature backfill
  and continuation; Stop leaves all identity evidence unchanged.
- Ask for the role only when the durable trace lacks LLM nature and no role
  argument was passed. Confirm an explicit role override when it conflicts
  with a known LLM-role trace.
- Install one self-contained host-specific instruction that makes the selected
  role continue its full workflow rather than merely report status.
- For requestors, wait for an in-progress response, perform owned review work,
  or run and follow `pw skill` when no review remains.
- For reviewers, answer an existing request or, even before an exchange or
  implementation step starts, wait globally for any new specification- or
  code-review request artifact without needing its identity in advance.
- Once the role and role-wide identity scan are resolved, continue without
  another confirmation. The only identity gates are a forced role mismatch and
  the `Override` or `Stop` decision for conflicting current-role artifacts.
- Refuse malformed, repair-required, escalated, artifact-inconsistent, or
  ambiguous multiple-exchange states. Report the `rvw_status` evidence instead
  of guessing.
- Repeating the skill against the same durable state must be idempotent.

## Review-mode constraints carried forward

Ordinary review rounds remain automated. A convergence recommendation is
advisory and enters durable `awaiting-human-confirmation`; only the human can
authorize specification consolidation or implementation commit. That state is
distinct from `escalated`, which remains a refusal case for automatic resume.

Every continuation must retain the identity-bearing context recorded by the
exchange. Specification work names the umbrella or `none`, exact reviewed
specification, and round. Code work names the umbrella or `none`, exact plan,
implementation step, and round. Those fields must agree with the durable
machine identity and include the traced LLM for both roles when known.

## Dependencies

This effort depends on `review-exchange-core`, `review-status-command`,
`spec-review-requestor`, `spec-reviewer`, `code-review-requestor`,
`code-reviewer`, and `review-mode-docs`. It changes their shared artifact-path
and participant-identity foundations through this topic without reopening
their completed umbrella rows.
