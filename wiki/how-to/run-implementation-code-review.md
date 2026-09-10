# Run an implementation code review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use this guide after selecting one implementation-plan step. The requestor owns
the staged subject and `a.commit`; the independent reviewer assesses immutable
evidence and may leave attributable repairs staged; the human owns commit.

Start the two role sessions independently. A requestor must not create, invoke,
delegate to, or message a reviewer, and a reviewer must not do those things to
a requestor. Each role rejects a task initiated by its automated counterpart.

Do not reconstruct protocol filenames or edit protocol artifacts. Read the one
final JSON result and use its `paths` member.

## Start an implementation code review

1. Activate the repository with [the opt-in guide](enable-independent-review-mode.md).
2. In the requestor agent session, start the ordinary implementation chain:

   ```text
   $llm-shared:implement-step on docs/v1.4.0/plan.v1.4.0.route-warnings.md step 2
   ```

3. Let the chain implement, validate, and group the step. After `a.commit` is
   prepared, `pw` routes to the code-review requestor and publishes immutable
   index and validation evidence.
4. In a separate reviewer agent session, run:

   ```text
   $llm-shared:code-reviewer
   ```

5. Leave the reviewer session active. After publishing `changes-requested`, it
   immediately waits for the replacement request; do not invoke the reviewer
   skill again for later intermediate rounds.
6. Return to the requestor after its bounded wait. Follow `paths.answer`, assess
   staged repairs, update writer-owned records, and publish a replacement round
   when the answer requests changes. That publication releases the waiting
   reviewer into its next assessment.

Stop when the requestor presents `Commit` and `Rework and review again`. Exit
`3` and a commit-ready recommendation do not authorize a commit. Convergence
leaves the exchange at its human gate. Keep the reviewer session in the quiet
`wait-any-request` under the configured home; a replacement round or a new
specification or code request will wake it.

After the human chooses `Commit`, the requestor executes the prepared root
`a.commit` through `pw code-review-commit`. If residual changes remain, that
continuation stages all of them and preserves durable authorization. Run
`group-commits-msg` for the staged remainder without another menu, then run
`pw code-review-commit --residual`. Do not complete the exchange, run
`pw skill`, or begin another step until `git status --porcelain` is empty.

## Resume an implementation code review

1. Open the same repository in the requestor agent session.
2. Optionally run `& "<LLM_SHARED_DIR>\rvw_status.bat"` to inspect every
   active exchange without resuming one.
3. Run `$llm-shared:code-review-requestor on <plan-path> step <n>` with the exact
   repository-relative plan and step.
4. Follow the final JSON `state`, `round`, and `paths`. A persisted
   `owning-action-pending` state means the human already authorized the commit;
   do not ask again.
5. Keep `a.commit` aligned with the staged paths after accepted repairs. Never
   commit through private Git commands.
6. At `owning-action-pending`, resume `pw code-review-commit`. A residual phase
   reuses the existing human authorization and must finish with a clean tree.
7. Stop on escalation, inconsistent evidence, or interrupted transition and use
   [the recovery guide](recover-an-independent-review.md).

The canonical [code-review requestor](../../instructions/code-review-requestor.md)
and [code reviewer](../../instructions/code-reviewer.md) instructions remain
authoritative for agent policy.

For the final result contract, see
[read review results and continue](read-independent-review-results-and-continue.md).
