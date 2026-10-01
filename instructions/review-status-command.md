# Report active review status

Use this instruction when a user asks where an interrupted specification or
code review stands, who acts next, or which umbrella owns it. This workflow is
migration-aware: it may perform one bounded safe migration preflight, after
which ordinary status discovery, projection, and rendering remain read-only.

## Codex status-check isolation

When Codex delegates a user-requested status check, start a fresh status-only
helper with `fork_turns="none"`. Never pass the active conversation context:
no conversation history, summary, previous review assessment, inferred active
document, or session ownership capability. Pass only the absolute repository
root, the resolved canonical instruction and launcher paths, and the request
to report the command's current status. Do not create a requestor or reviewer
agent for this check.

Use this self-contained helper task, substituting only the resolved paths:

```text
Report review status for <absolute-project-root>. Read and follow
<LLM_SHARED_DIR>/instructions/review-status-command.md, then run
<LLM_SHARED_DIR>/rvw_status.bat once from that repository root. Return the
exit code and status output. You are a status observer only. Do not delegate,
start a watcher, claim ownership, resume a review, or act as either review role.
```

This delegation rule applies to the parent, not recursively to its helper.
If fresh-context delegation is unavailable, run the launcher directly using
the same path-only inputs and report its output; do not use a helper that
inherits the conversation. Base the report on the command result alone.

During a Codex attached reviewer wait, the parent retains the existing watcher
handle and its session-only capability, then continues that same wait after
reporting status. A user-requested status check is one operation, never a
periodic substitute for `wait-any-request`. Claude's status execution and
background completion behavior are unchanged.

## Run the status command

Read [`../rules/run_commands.md`](../rules/run_commands.md) before invoking the
launcher. Resolve `<LLM_SHARED_DIR>` as the repository or installed plugin root
that contains this canonical instruction, then run the launcher by full path
from the caller's project root:

```powershell
& "<LLM_SHARED_DIR>\rvw_status.bat"
```

Use the caller's working directory as the repository by default. Pass
`--root <project-root>` only when the user names another repository or the
caller root cannot represent the requested target. Keep the default human
format unless the user requests structured data; then pass `--format json`.

## Interpret and report the result

- Status `0` means the complete result is trustworthy, including a result with
  zero or multiple active exchanges.
- Status `3` means the command returned useful evidence but at least one review
  candidate is untrustworthy. Report the retained evidence and diagnostics.
- Status `2` means an operational boundary prevented a trustworthy query.
  Report the typed migration diagnostic and do not infer review state.

Report the command's migration state and artifact home, then each exchange's
requestor and reviewer LLM nature, role, specialization, owner, umbrella,
state, reviewed document, implementation step when present, round, artifacts,
and next action without reconstructing them from prompt memory. When a role
nature is `conflicting`, include its evidence paths.

Do not reproduce migration, exchange discovery, or state classification in
this instruction. Outside the command's safe required migration, do not renew,
reclaim, repair, resume, cancel, complete, stage, or commit anything. A
separate review continuation workflow owns those actions.
