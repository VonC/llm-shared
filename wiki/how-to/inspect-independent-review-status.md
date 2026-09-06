# Inspect independent review status

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Use this guide to find active specification and code exchanges, determine who
acts next, or diagnose a stopped review without resuming or mutating its
lifecycle. Status may perform one bounded safe artifact migration before its
ordinary read-only projection.

## Inspect the current repository

1. Run the public launcher by its installed path from anywhere inside the
   reviewed Git repository:

   ```powershell
   & "<LLM_SHARED_DIR>\rvw_status.bat"
   ```

2. Read the repository header first:

   - `Outcome: trustworthy` means the whole report's evidence is trustworthy.
   - `Migration` says `unnecessary`, `completed`, or `blocked`.
   - `Artifact home` names the configured repository-relative runtime home.
   - `Active exchanges` counts both healthy exchanges and retained damaged
     candidates.

3. For each healthy exchange, follow `State`, `Role`, `Owner`, and `Next action`.
   Treat `Requestor LLM nature` and `Reviewer LLM nature` as artifact evidence,
   not as a reason to launch either role. `unrecorded` is valid legacy absence;
   `conflicting` retains contradictory evidence for diagnosis.

4. Follow the exact artifact paths printed by status. Do not reconstruct a
   request, answer, coordination, transcript, tombstone, or lock name.

The status result is diagnostic only. `human-confirmation` means a valid
reviewer answer already reached the convergence gate; it does not mean a newly
published request has been reviewed. A freshly published request should report
`request-pending`, reviewer ownership, and `reviewer-work`.

## Inspect another repository or emit JSON

Pass an explicit Git root only when the current directory is not inside the
target repository:

```powershell
& "<LLM_SHARED_DIR>\rvw_status.bat" --root C:\work\project
```

Use schema-2 JSON for automation:

```powershell
& "<LLM_SHARED_DIR>\rvw_status.bat" --format json
```

The JSON repository object contains `schema_version`, `repository_root`,
`outcome`, `active_count`, `has_errors`, `migration`, and `exchanges`. Each
healthy exchange includes identity, role specialization, owner, lease,
artifacts, both LLM-nature values and evidence arrays, and the typed next action.

## Handle the process status

- Exit `0`: the complete report is trustworthy, including zero active reviews.
- Exit `3`: useful candidate evidence was retained, but at least one candidate
  is damaged or untrustworthy. Stop before continuation and report its
  diagnostic.
- Exit `2`: arguments, repository discovery, artifact-home validation, or
  migration prevented a trustworthy query. Read standard error and do not infer
  exchange state.

Do not use repeated status calls as a reviewer wait. Exact intermediate rounds
use the protocol's bounded `wait-request` or `wait-answer`; the global
cross-exchange reviewer monitor is planned for Step 5 and has not shipped.

For exact fields and configuration, see the
[independent review mode contract](../reference/independent-review-mode-contract.md).
For stopped exchanges, use
[recover an independent review](recover-an-independent-review.md).
