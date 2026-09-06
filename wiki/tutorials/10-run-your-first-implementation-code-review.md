# Run your first implementation code review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use two agent sessions in the same repository. The requestor agent owns the
implementation step and staged subject; the reviewer agent assesses immutable
evidence from an independent context. Changing skills in one session is not an
independent review.

🧪 This tutorial uses the second stage of the fictional route-warning effort.
Its umbrella is `docs/v1.4.0/draft.v1.4.0.trail-safety.md`, its implementation
plan is `docs/v1.4.0/plan.v1.4.0.route-warnings.md`, and the implementation step
is Step 2. The tutorial is independently runnable from that settled plan.

If you need to review the requirement, design, or plan first, use
[the specification tutorial](09-run-your-first-specification-review.md) at the
point where the review families diverge.

## 1. Activate independent review mode

At the repository root, create an empty `a.review-mode` file. Open two agent
sessions in the same repository and label them **Requestor** and **Reviewer**.
Keep repository context paths relative to the Git root. You open both sessions
independently; neither agent may create, invoke, delegate to, or message its
counterpart.

Start with a settled plan whose Step 2 is not implemented and a clean index.

## 2. Implement and publish code-review round 1

### Requestor agent session — run the implementation chain

Ask the requestor to run the plan step:

```text
$llm-shared:implement-step on docs/v1.4.0/plan.v1.4.0.route-warnings.md step 2
```

The ordinary chain implements the step, runs its checks, records the
implementation assessment, and prepares `a.commit`. Because the marker is
present, `pw` routes to the code-review requestor instead of stopping at the
ordinary commit-message gate.

Before publishing round 1, the request renderer captures the staged
`request_index_tree` and the ordered `resolved_validation_set`. Those immutable
values bind the reviewer to one implementation plan, implementation step,
round, staged subject, and set of commands. The requestor then enters one
bounded wait.

## 3. Ask the independent reviewer for changes

### Reviewer agent session — answer code-review round 1

In the separate reviewer session, ask:

```text
$llm-shared:code-reviewer
```

This instruction comes from you, not from the waiting requestor. A reviewer
must reject requestor-initiated or requestor-parent delegation even when the
published request and staged evidence are otherwise valid.

The reviewer compares the live index with `request_index_tree`, executes the
resolved validation commands, and runs `validation-state compare` after the
checks. For this example, imagine it finds that one route-warning boundary lacks
an acceptance assertion and publishes `changes-requested`.

The reviewer may leave an attributable repair staged, but it does not commit.
It reports each repaired path so the requestor can accept or reverse the change.
After publishing `changes-requested`, it immediately enters the next bounded
`wait-request` in the same session. Leave that reviewer session running.

## 4. Accept the repair and publish round 2

### Requestor agent session — process the returned code answer

Return to the requestor agent session. The bounded wait ends with final JSON;
follow its `paths.answer` member rather than reconstructing a filename. The
requestor checks the staged repair against the implementation step, updates the
implementation report if needed, and confirms that `a.commit` still matches the
staged paths and group order.

The requestor consumes the intermediate answer and publishes round 2 with a new
`request_index_tree` for the accepted subject. The implementation plan,
implementation step, umbrella, and commit boundary remain explicit. Publishing
the replacement request releases the reviewer session that is already waiting.

### Reviewer agent session — assess code-review round 2

Without another command from you, the active reviewer reads the returned round
2 request and repeats the index and validation-state comparisons. When every
readiness result passes and this round makes no substantive repair, it publishes
a commit-ready recommendation and leaves the exact exchange at its human gate.
The reviewer remains available for a future request under the artifact home,
but the cross-exchange monitor has not shipped; do not replace it with polling.
Exit `3` means no commit has run.

## 5. Make the human choice

### Requestor agent session — present the commit gate

Return to the requestor agent session. It presents the immutable evidence,
validation result, staged repair assessment, `a.commit`, and exactly these
choices:

- `Commit`
- `Rework and review again`

Only your `Commit` choice authorizes the owning workflow to validate and execute
the reviewed commit plan. The reviewer recommendation does not cross the commit
boundary. Choose `Rework and review again` when code or evidence needs another
round.

After `Commit`, the requestor runs the prepared root `a.commit` first. If that
batch leaves any non-ignored path, the same authorization stages the complete
remainder and invokes `group-commits-msg` without another human menu. The
requestor executes that residual plan and completes the exchange only after
`git status --porcelain` is empty. A failed batch or dirty final status keeps
the authorization pending for safe replay.

## What you learned

Code review binds one implementation step to immutable staged evidence,
alternates intermediate rounds through reciprocal active waits, returns exact
counterpart paths, and leaves the final commit decision with the human. That
single decision covers the reviewed batch and any bounded residual cleanup,
but never permits a dirty tree to advance.

This page describes observable behavior. The canonical
[code-review requestor instruction](../../instructions/code-review-requestor.md)
and [code-reviewer instruction](../../instructions/code-reviewer.md) remain
authoritative for agent policy.

Previous: [run a specification review](09-run-your-first-specification-review.md).
For the authority model, read
[why independent review separates authority](../explanation/independent-review-mode-and-human-authority.md).
