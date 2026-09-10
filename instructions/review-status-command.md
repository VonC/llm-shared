# Report active review status

Use this instruction when a user asks where an interrupted specification or
code review stands, who acts next, or which umbrella owns it. This workflow is
migration-aware: it may perform one bounded safe migration preflight, after
which ordinary status discovery, projection, and rendering remain read-only.

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
