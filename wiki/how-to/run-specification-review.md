# Run a specification review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use this guide when a requirement, design, or plan already exists and an
independent agent should assess its questions. The requestor owns document
changes; the reviewer owns the answer; the human owns the final choice.

Start the two role sessions independently. A requestor must not create, invoke,
delegate to, or message a reviewer, and a reviewer must not do those things to
a requestor. Each role rejects a task initiated by its automated counterpart.

Do not reconstruct protocol filenames or edit protocol artifacts. Follow the
final JSON `paths` member returned by the active skill.

## Start a specification review

1. Activate the repository with [the opt-in guide](enable-independent-review-mode.md).
2. In the requestor agent session, run the normal question workflow on a
   repository-relative document path:

   ```text
   $llm-shared:review-ask-questions on docs/v1.4.0/design.v1.4.0.route-warnings.md
   ```

3. Let `pw` route the finished question pass to the specification requestor.
   It publishes round 1 and enters one bounded wait.
4. In a separate reviewer agent session, run:

   ```text
   $llm-shared:spec-reviewer
   ```

5. Leave the reviewer session active. After each `changes-requested` answer it
   immediately waits for the replacement request; do not invoke the reviewer
   skill again for later intermediate rounds.
6. Return to the requestor after its wait ends. Read only the exact answer at
   `paths.answer`, apply accepted changes, and let the requestor publish another
   round when needed. That publication releases the already-waiting reviewer,
   which assesses the next round automatically.

Stop when the requestor presents `Consolidate` and
`Revise and review again`. A convergence recommendation and exit `3` do not
authorize consolidation. Convergence ends the exact-exchange reviewer wait at
the human gate. Keep the reviewer available for any future request under the
configured artifact home. The cross-exchange monitor has not shipped, so do not
poll or claim that another exchange will wake it automatically.

## Resume a specification review

1. Open the repository in the requestor agent session.
2. Optionally run `& "<LLM_SHARED_DIR>\rvw_status.bat"` to inspect every
   active exchange without resuming one.
3. Run `$llm-shared:spec-review-requestor`. The durable state selects the
   persisted round and owner.
4. Follow the final JSON `state`, `round`, and `paths`; do not infer which
   artifact should exist beside another one.
5. If the result says `request-pending`, keep the request and let the reviewer
   answer. If it says `answer-pending`, assess that returned answer. If it says
   `convergence-gate`, present the human choices without consuming the answer.
6. Stop on escalation, inconsistent evidence, or interrupted transition and use
   [the recovery guide](recover-an-independent-review.md).

The canonical [specification requestor](../../instructions/spec-review-requestor.md)
and [specification reviewer](../../instructions/spec-reviewer.md) instructions
remain authoritative for agent policy.

For result fields and authorized continuation, see
[read review results and continue](read-independent-review-results-and-continue.md).
