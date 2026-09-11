# Read independent review results and continue

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use this guide after a requestor or reviewer skill returns. Treat its one final
standard-output JSON object as the result; progress diagnostics written during a
wait are not the final result.

Do not reconstruct protocol filenames or edit protocol artifacts. Use the
returned `paths` object even when a neighbouring filename looks predictable.

## Read the returned result

1. Read `operation`, `identity`, `state`, `outcome`, `round`, `paths`, and
   `diagnostic` from the final JSON.
2. Follow only the artifact assigned to the current actor. A requestor follows
   `paths.answer` after an answer result; a reviewer follows `paths.request`
   after a request result.
3. Interpret the process exit separately:

   - Exit `0` means the operation completed and the returned state grants the
     reported next action.
   - Exit `3` is an expected stop such as timeout, abandonment, escalation,
     convergence, or pending authorized work.
   - Exit `2` is invalid input or a fatal error; stop and report the diagnostic.

4. Do not treat `outcome: published` or a convergence disposition as human
   authorization. Read the returned state and the registered choices.

## Continue an authorized action

1. At `convergence-gate`, present the exact family choices. Only the human may
   select `Consolidate` or `Commit` instead of another round.
2. Let the requestor record that choice. Continue only when the result includes
   `owning_action_authorized: true` and state `owning-action-pending`.
3. Resume the owning skill rather than composing a direct launcher sequence:

   - specification: run `$llm-shared:spec-review-requestor` to replay the
     authorized consolidation; its owning workflow commits the answered
     specification alone before changing or stripping it, then groups every
     post-fold change and requires a clean tree before handoff;
   - code: run `$llm-shared:code-review-requestor on <plan-path> step <n>` to
     replay the authorized reviewed commit. If it reports residual changes,
     run `group-commits-msg` for that staged remainder without another menu,
     then run `pw code-review-commit --residual`.

4. Do not ask the human again when durable authorization is already pending.
5. For specification consolidation, verify that the snapshot commit contains
   only the reviewed document and that the index is empty before the fold.
6. For either family, require `git status --porcelain` to be empty after every
   authorized batch. Do not run `pw skill` or another implementation step from
   a dirty tree.
7. The requestor completes the exchange only after the owning action succeeds.
   On failure, leave authorization pending for a later replay.

For an expired or stopped exchange, use
[recover an independent review](recover-an-independent-review.md).
The canonical [shared requestor instruction](../../instructions/review-requestor.md)
remains authoritative for agent policy.
