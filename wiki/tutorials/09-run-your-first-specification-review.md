# Run your first specification review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use two agent sessions in the same repository. The requestor agent owns the
specification and the reviewer agent assesses it from an independent context.
Changing skills inside one agent session does not create that separation.

📝 This tutorial reviews the fictional route-warning requirement under the
`docs/v1.4.0/draft.v1.4.0.trail-safety.md` umbrella. Its reviewed specification
is `docs/v1.4.0/feature-request.v1.4.0.route-warnings.md`. You will publish two
rounds and stop at the human choice without editing protocol artifacts.

If your next task is implementation evidence rather than a specification, use
[the implementation-code tutorial](10-run-your-first-implementation-code-review.md)
at the point where the two families diverge.

## 1. Activate independent review mode

Prepare the configured artifact home (`.reviews` by default) with a local
`.gitignore` containing `*`, then create an empty `a.review-mode` inside it.
An empty marker selects the default bounded requestor wait. Keep the fictional umbrella and
reviewed specification as repository-relative paths when you address the agent.

Open two agent sessions in this repository and label them **Requestor** and
**Reviewer**. Leave both sessions open until the exchange reaches its human
gate. You open the two sessions independently; never ask either agent to spawn,
invoke, delegate to, or message its counterpart.

## 2. Publish specification round 1

### Requestor agent session — publish the first request

Ask the requestor to review the existing requirement questions:

```text
$llm-shared:review-ask-questions on docs/v1.4.0/feature-request.v1.4.0.route-warnings.md under docs/v1.4.0/draft.v1.4.0.trail-safety.md
```

The normal `pw` handoff detects the marker, routes to the specification
requestor, and publishes round 1. The request identity names the umbrella,
reviewed specification, and round. The requestor then enters one bounded wait
for the reviewer answer.

From a repository shell, inspect the durable state without resuming it:

```powershell
& "<LLM_SHARED_DIR>\rvw_status.bat"
```

The report names the `.reviews` artifact home, migration result, recorded
requestor and reviewer LLM natures, `request-pending` state, reviewer owner, and
the exact next action. On an older repository, this first status call may move
recognized runtime artifacts transactionally before reporting them.

Do not infer the answer filename. Keep the requestor session waiting while the
reviewer works; the final launcher result will return the authoritative
`paths.answer` value.

## 3. Ask the independent reviewer for changes

### Reviewer agent session — answer specification round 1

In the separate reviewer session, ask:

```text
$llm-shared:spec-reviewer
```

This instruction comes from you, not from the waiting requestor. A reviewer
must reject a task that an automated requestor or requestor parent session
initiated, even when round 1 is validly pending.

The reviewer follows the sole pending specification request, reads its returned
request path, and publishes a `changes-requested` answer. For this example,
imagine it finds that the route-warning requirement never says what happens
when a trail has no severity value.

The reviewer does not edit the specification or choose for the human. Its
published answer becomes durable exchange evidence. Because the disposition is
`changes-requested`, the reviewer immediately enters the quiet global
`wait-any-request` in the same session. Leave it running; do not invoke the
reviewer skill again for round 2.

## 4. Apply the answer and publish round 2

### Requestor agent session — process the returned answer

Return to the requestor agent session. Its bounded wait now ends with final JSON
whose `paths.answer` member identifies the exact answer to read. The requestor
accepts the missing-severity finding, updates the reviewed specification, and
records the change in its writer response.

The requestor consumes that intermediate answer, continues the same exchange,
and publishes round 2. The round number changes; the umbrella and reviewed
specification identity do not. That publication releases the reviewer session
that is already waiting.

### Reviewer agent session — assess specification round 2

Without another command from you, the active reviewer reads the returned round
2 request, finds the questions and answers complete, and publishes a
convergence recommendation and leaves the human gate alone. The reviewer
returns to `wait-any-request` under the configured home, ready for a replacement
round or a new review. The requestor's exit `3` is the expected human stop and
grants no consolidation authority.

## 5. Make the human choice

### Requestor agent session — present the specification gate

Return to the requestor agent session. It presents the reviewer recommendation,
its own assessment, and exactly these choices:

- `Consolidate`
- `Revise and review again`

Only your `Consolidate` choice authorizes the owning workflow to fold the
settled answers into the specification. The recommendation alone does not
authorize consolidation. Choose `Revise and review again` when another
independent round is needed. After authorization, the owning workflow first
commits the answered specification alone, then performs the fold and completes
the exchange.

## What you learned

One specification exchange keeps the umbrella, reviewed specification, and
round visible; alternates automatically through requestor and reviewer waits;
returns exact paths for each counterpart artifact; and stops at a human-owned
consolidation gate.

This page describes the observable journey. The canonical
[specification-requestor instruction](../../instructions/spec-review-requestor.md)
and [specification-reviewer instruction](../../instructions/spec-reviewer.md)
remain authoritative for agent policy.

Next: [run an implementation code review](10-run-your-first-implementation-code-review.md)
or revisit [why independent review separates authority](../explanation/independent-review-mode-and-human-authority.md).
