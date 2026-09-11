# Implementation code-review requestor instruction

Use this instruction when an implementation writer delegates review of one
completed plan step. The writer retains ownership of the staged work,
implementation evidence, repair assessment, `a.commit`, and any human-authorized
commit action. The reviewer never commits.

Read and follow `instructions/review-requestor.md` in full before running any
exchange command. That shared instruction owns durable coordination. This
specialized instruction supplies code-review policy, authored content, staged
repair assessment, and the owning continuation only.

## Exact policy for implementation code-review operations

Pass this unchanged policy to every shared exchange operation:

```text
--family code
--convergence-signal commit-ready
--another-round-label "Rework and review again"
--continue-owning-workflow-label "Commit"
```

Also pass `--document <exact-implementation-plan>` and
`--implementation-step <exact-step>`, plus `--umbrella <exact-umbrella-draft>`
when the effort declares one. The plan filename supplies the version and slug;
the family always uses the fixed `code` type token.

Never create, overwrite, rename, or delete a protocol artifact by hand. Run all
coordination through
`& "<LLM_SHARED_DIR>\bin\review_exchange.bat"` and use the exact paths it
returns.

## Immutable request evidence

Before every fresh request publication, let
`& "<LLM_SHARED_DIR>\bin\code_review_request.bat"` call
`capture_index_tree` at its publication boundary. The helper records the Git
tree object of the index in `request_index_tree`; do not substitute a worktree
digest or compose a separate Git command.

The renderer calls `resolve_code_review_validation` with the mandatory project
default and additive checks. Pass every exact plan-step addition through a
repeatable `--plan-validation-command` and every stricter current-request
addition through a repeatable `--request-validation-command`. An addition may
share a command with another source, but it cannot remove the `ghog day` project default.
The resulting `resolved_validation_set` retains each command's project, plan,
or request sources in deterministic order.

Render both fields from that one typed value under the authored
`## Code review evidence` heading. Keep this fenced JSON object distinct from
the shared envelope's `## JSON`; never edit either rendering independently.
Only then pass the complete paired artifacts to `publish-request`.

## Ordered round sequence for implementation code review

1. Run `status` with the exact plan, step, optional umbrella, and fixed policy.
2. Run `activate` before the first mutation. If the state is `idle`, run `start`
   once and never restart a live identity.
3. Prepare separate ignored root UTF-8 assessment, implementation report,
   change summary, writer response, and optional guidance files. Run
   `& "<LLM_SHARED_DIR>\bin\code_review_request.bat"` with every applicable additive validation
   command and two distinct ignored output paths.
4. Pass the complete request and substantive summary to `publish-request`.
5. Do not start, spawn, delegate, invoke, or message a reviewer. Run
   `wait-answer` immediately in this same requestor session using the complete
   marker timeout. Read only the exact `paths.answer` file returned for this
   identity.
6. For an intermediate answer, assess accepted repairs, make writer-owned
   corrections, and call `consume-answer` with truthful `reviewed-work-changed`
   evidence plus `disagreement` only for explicit disagreement.
7. When automation remains active, call `continue`, render the replacement
   round, publish it, and wait again.
8. At convergence, retain the answer, apply polishing-only covered wording,
   present the human gate, and call `confirm` only with the human's exact label.
9. After durable Commit authorization, run the canonical owning continuation.
   It executes the reviewed root `a.commit` first. If it stages residual paths,
   run the authorized residual `group-commits-msg` continuation and its second
   batch. The owning action succeeds only after every batch succeeds and the
   final working tree is clean; only then call `complete`.

Never read the versioned transcript as working context. After a wait or status
reports an answer, read only the exact `paths.answer` file.

The shared role-session isolation rule is fail-closed. A requestor never runs
`pw skill code-reviewer`, invokes the reviewer skill or prompt, uses an agent
or subagent tool to create the counterpart, or asks another model to review.
Publishing the request is the whole handoff; waiting is the whole requestor
continuation.

Reject this requestor task if an automated reviewer or a parent agent acting as
reviewer spawned, delegated, started, invoked, or messaged it. The reviewer
publishes an answer and waits; it never creates the requestor continuation.

## State handling for the code-review requestor

| Observed state | Specialized action |
| --- | --- |
| `disabled` | Preserve the ordinary human commit gate and create no exchange. |
| `idle` | Activate, start round 1, render, and publish. |
| `round-in-progress` | Resume the persisted requestor work. |
| `request-pending` | Keep the request and wait for the exact answer. |
| `answer-pending` | Read only `paths.answer`, then assess staged repairs. |
| `abandoned-request` | Call `reclaim`, then wait with unchanged evidence. |
| `abandoned-answer` | Call `reclaim`, then assess the retained answer. |
| `abandoned-mid-round` | Call `reclaim` and resume normally, unless the human explicitly decides to close it through forced completion. |
| `convergence-gate` | Re-present evidence, recommendation, and both choices. |
| `owning-action-pending` | Resume the authorized commit without asking again. |
| `escalated` | Stop for shared human resolution; never reclaim it. |

Treat inconsistent, interrupted, and repair-required outcomes exactly as the
shared requestor directs. An intact expired active round uses `reclaim`; an
escalated exchange never does.

## New-session ownership pickup

A new agent session cannot recover the previous session's plaintext ownership
token. A bare user `resume` authorizes the canonical resume gates and automatic
`claim` with the unchanged exact code review context before the first mutation.
At `convergence-gate` and
`owning-action-pending`, pickup advances the ownership generation for the
requestor even though the convergence choice itself belongs to the human.

Keep the returned `ownership_generation` and `ownership_token` only in the
current process or session. Supply them as `--ownership-generation` and
`--ownership-token` to `confirm` and every later fenced mutation. Never write
the plaintext token into an artifact, environment file, transcript, or status
message.

Pickup is not a reset: it advances the generation monotonically and fences the
old session. It is also distinct from `reclaim`, which renews an intact expired
lease without replacing a missing session capability. Do not resolve, archive,
or restart an otherwise valid exchange merely because the agent session
changed.

For a convergence handoff, the human can state: `Commit selected. This is a new
session; force requestor ownership pickup, record Commit, then continue the
authorized commit process.` The requestor must run `pickup` before `confirm`.

## Authored inputs for implementation review rounds

The assessment states whether the exact step is fully implemented and names the
test, static-check, coverage, architecture, performance, and feature-integrity
evidence. The implementation report explains what changed. The change summary
lists the current staged paths and `a.commit` groups. The writer response records
accepted earlier feedback and any disagreement. Human guidance stays separate.

The paired renderer receives the exact plan, step, round, optional umbrella,
separate ignored authored inputs, and separate ignored request-content and
transcript-summary outputs. Do not author those outputs independently.

## Staged repair and commit-plan assessment

Assess every answer against this four-part scope evidence, in this order:

1. the exact plan step;
2. the repaired-path inventory from the answer;
3. the staged diff, complete only because the reviewer must
   leave each repair staged and name every repaired path in its answer; and
4. the relevant `implementation-check` result.

The writer owns final acceptance of reviewer edits. If the requestor reverses a
repair, the replacement request records that reversal as explicit disagreement.
Never hide a reversal behind a generic changed-work signal.

Assess `a.commit` after every repair. Amend it only when
membership, grouping, order, scope, or subject accuracy no longer matches the
staged work. A wording repair that leaves commit boundaries and subjects
accurate needs no amendment.

## Intermediate answers and repair classification

Intermediate changes-requested answers do not enter a human gate. Apply or
assess repairs, report `reviewed-work-changed` truthfully, add `disagreement`
only for explicit disagreement, call `consume-answer`, then `continue` and
publish the replacement round.

A repair is substantive when it changes code, tests, acceptance behavior, or
commit grouping. A substantive changes-requested answer requires a replacement
round. Wording, formatting, and equivalent metadata changes are polishing-only
when proposed commit boundaries remain unchanged.

Do not call `consume-answer` for a commit-ready recommendation. Convergence
answers remain evidence at the human gate.

## Commit-ready convergence and human authority

Present the exact umbrella or `none`, plan, step, round, reviewer recommendation,
repaired paths, staged evidence, `a.commit`, and writer assessment. Show
`Rework and review again` and `Commit`.

When substantive repairs accompany commit readiness, retain the legitimate
gate and recommend `Rework and review again`. The requestor cannot start a new
round directly from convergence. Polishing-only repairs may accompany a
same-round commit-ready recommendation.

The reviewer recommendation never authorizes a commit. For `Rework and review
again`, pass that label to `confirm`, preserve any guidance separately, and
publish the replacement round. For `Commit`, require
`owning_action_authorized: true` before the owning action. At
`owning-action-pending`, do not ask the human again; resume the already
authorized action.

## Authorized commit replay for implementation review

After durable authorization, invoke the canonical commit continuation that
validates and executes the reviewed root `a.commit`. Do not construct private
Git commit commands and do not present the commit choice again.

The first `pw code-review-commit` pass executes that prepared plan. If it
reports residual changes, it has staged the complete remainder with
repository-wide `git add -A` while retaining authorization. Follow the
authorized code-review continuation in `group-commits-msg.md`: replace the root
`a.commit` with groups for every residual staged path, format it, skip its human
menu, and run `pw code-review-commit --residual`.

The residual pass executes the replacement plan and requires
`git status --porcelain` to return no entries. If the action succeeds, call
`complete`. If either batch fails or the final tree is non-clean, retain the
authorization and report the failure so a later session can repair and replay
the owning action. Never proceed to `pw skill` or another implementation step
until this clean-tree postcondition succeeds.

For a bare user `resume`, follow [the canonical resume instruction](review-resume.md)
through migration, role and identity gates, and automatic `claim` before
continuing this exact exchange. Keep its capability in session and pass the
paired ownership flags to every fenced operation. After exchange release, run
and follow `pw skill` immediately.
