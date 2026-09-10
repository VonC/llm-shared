# Recover an independent review

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use direct launchers only after the ordinary skill route reports an expired or
stopped state. Begin with `status`, read its final JSON, and copy the exact
family, document, optional umbrella, step, and policy context into the chosen
operation.

Do not reconstruct protocol filenames or edit protocol artifacts. Follow the
returned `paths` and stop on exit `2`.

## Continue an active review with resume

1. Open the reviewed repository in the agent session and enter `resume`.
2. Let the skill check migration first. It moves recognized legacy evidence
   only when the complete move is safe, then checks again before selecting a
   role. On a blocked or incomplete migration, follow the diagnostic.
3. If the role or exchange is ambiguous, select the one to continue. A known
   identity conflict presents `Override` or `Stop`: Override keeps conflicting
   values and fills only missing identities; Stop leaves the evidence alone.
4. Once these gates pass, automatic pickup replaces a missing or stale session
   capability without waiting for the previous lease to expire. You do not
   supply a token, generation, or new-session declaration.
5. Let the selected role continue. A reviewer answers the selected request or
   waits globally through `wait-any-request`. A requestor waits for its exact
   answer, processes that answer, or resumes its authorized owning action.
6. At convergence, select the existing human choice, such as `Commit` or
   `Rework and review again`. Resume does not select it for you. If Commit was
   already recorded, the requestor finishes the authorized action without
   another confirmation and follows `pw skill` after exchange release.

See the [canonical resume instruction](../../instructions/review-resume.md)
for the exact support operations. Resume is an LLM skill; there is no
`rvw_resume.bat` launcher.

## Reclaim an expired live exchange

Use ordinary reclaim only for an intact live round whose lease expired while
the expected actor was still working.

1. Run status with the exact context and confirm the final JSON state is
   `abandoned-request`, `abandoned-answer`, or `abandoned-mid-round`.
2. Run:

   ```bat
   bin\review_exchange.bat reclaim <family-and-context-flags>
   ```

3. Read the final JSON `state`, `round`, and `paths`. Reclaim renews the same
   round without changing request, answer, or transcript content.
4. Resume the actor named by the returned state. Reclaim is idempotent while the
   round is live.

Do not use ordinary reclaim for an escalated, inconsistent, or interrupted
exchange. A timeout can lead to an abandoned lease, but it does not grant human
recovery authority by itself.

## Recover a stopped exchange

Stop automation for no-progress, explicit disagreement, inconsistent artifacts,
an interrupted transition, or escalation. Preserve the diagnostic and let the
human identify the authoritative evidence before selecting a command below.

## Human decision required

> **Authority:** only the human may choose a forced resume, forced close,
> resolution, or archive. **Precondition:** inspect the final JSON state and the
> artifact shape named by `paths`, then write the decision to an ignored root
> summary file. **Evidence effect:** every command appends or preserves the
> authored decision as described below; none may be substituted for manual
> artifact editing.

To resume an escalated exchange whose request, answer, and transcript remain
intact, preserving the same round and returning ownership from artifact shape:

```bat
bin\review_exchange.bat reclaim --force --summary-file .reviews/a.human-reclaim.md <family-and-context-flags>
```

To close an intact, artifact-free `abandoned-mid-round` exchange without
manufacturing convergence or owning authorization:

```bat
bin\review_exchange.bat complete --force --summary-file .reviews/a.human-close.md <family-and-context-flags>
```

To clear an escalated, inconsistent, or interrupted exchange and start a fresh
round from the human's authoritative decision:

```bat
bin\review_exchange.bat resolve --summary-file .reviews/a.human-resolution.md <family-and-context-flags>
```

Use `archive --summary-file` instead of `resolve` when stopped evidence must be
preserved under derived archive names. Never resume the interrupted transition
itself.

The canonical [shared requestor instruction](../../instructions/review-requestor.md)
remains authoritative for exact preconditions and agent stopping policy.
