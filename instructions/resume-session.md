# Resume the last paused session once

Use when the user invokes `resume-session` to continue saved session work.
Accept the optional argument `--force`, as in `resume-session --force`.
These are LLM instruction commands, not shell executables or `pw` subcommands.
Reject other arguments instead of guessing a different prompt or checkout.

## Locate and check the saved prompt

Read the current project's agent instructions and
[run_commands.md](../rules/run_commands.md) first. Resolve and validate the
artifact home and exact two filenames from the
[pause-session artifact contract](pause-session.md#pause-inputs-and-artifact-contract).
Use that checkout's `a.session-resume.local.md`, even if another older
checkpoint looks unused. Do not scan all `.reviews` Markdown for a likely
prompt, fall back to earlier notes, or interpret `a.prompt.txt` as this file.

At invocation time, check the exact prompt and flag paths, rather than a
remembered listing. Hash the prompt's exact bytes with SHA-256; normalize
the hexadecimal digest to lowercase. The flag must match the fields in
[resume-session.template.md](../templates/resume-session.template.md):
schema 1, the canonical prompt basename, a 64-character SHA-256 digest,
an absolute project root, timestamp with offset, and `true` or `false`
for Forced. Compare resolved project paths using the filesystem's rules.

| Observed state | Resume behavior |
| --- | --- |
| Prompt missing | Report that no pause-session prompt exists; leave the flag alone and stop |
| Prompt empty, unreadable or incomplete | Report the problem; write no flag and stop |
| Flag absent | Announce the found prompt as `unused`, then read and reconcile |
| Valid flag identifies this prompt, root and digest | State `resume-session: already used`; stop unless `--force` was supplied |
| Valid flag has a different digest | Announce the found prompt as `new prompt since previous use`, then read and reconcile |
| Malformed or unreadable flag, wrong prompt basename or project root | Report the diagnostic and stop; do not treat a failed check as absence |

Once these initial checks permit reading the prompt, make the first resume
status a clear announcement that it was found and will be used:

> resume-session: found resume prompt `<relative-path>` ({state}); I will use
> it to resume this session.

Substitute the actual prompt path relative to the consuming project's checkout
root, such as `.reviews/a.session-resume.local.md`, honoring any configured
artifact home. Replace `{state}` with `unused`, `new prompt since previous use`,
or `forced reread` for a matching flag with `--force`. Send this as a progress
message before reading and reconciling the saved context, any recovery summary,
or task execution. Do not end the turn at this announcement.

For a stopping state, include the same relative pathname in the diagnostic
instead; do not claim the prompt will be used. State the sampled result before
acting. Force bypasses only the already-used check. It does not bypass missing
inputs, ownership checks, approval boundaries, running-job checks, or current
instructions.

## Read and reconcile before continuing

Read the entire saved prompt. Follow its reading order for applicable agent
rules, journals and handoffs, then the references the next action needs.
For plan steps, read the journal and handoff in full as
[step-journal.md](step-journal.md) requires. Preserve the user's objective,
accepted decisions and still-applicable authorizations across sessions.
Current user steering and project instructions take precedence over the
saved prompt; historical quotations and tool output remain evidence.

Check the current checkout path, branch, HEAD and dirty state against the
snapshot. Read the latest journal milestones to detect obsolete handoff
actions. Verify required local references and inspect any active job through
its documented status mechanism before considering a new run. Use disk and
current protocol state as evidence; do not replay a completed action merely
because it remains on an old next-actions list.

Do not automatically switch branches, reset changes, reclaim a live review,
or restart a job to make the snapshot match. Reconcile ordinary progress
and record it in the existing notes. If the worktree is different, a required
reference is missing, or a discrepancy prevents a safe continuation, report
the exact blocker and leave the receipt unchanged. Ask only for information
or authorization actually needed to resolve it. Unrelated work remains intact.

A prompt that names a review role does not restore ownership. Route review
continuation through [review-resume.md](review-resume.md) and preserve role
isolation. Never spawn or contact the automated counterpart. A host session
handle is not a reusable ownership capability. A process may outlive the
previous chat without being attachable from this one; verify it before
launching anything else.

## Mark this prompt used and resume the task

Once the prompt and required references have been read and state reconciled:

1. Re-hash the prompt and resample its flag immediately before writing,
   applying the same state table again.
   If the prompt changed, restart selection against the new bytes. If another
   session consumed it meanwhile, stop unless this invocation used `--force`.
   The receipt is a reuse guard, not a lock for concurrent agents; coordinate
   conflicting ownership before continuing.
2. Fill [resume-session.template.md](../templates/resume-session.template.md)
   with the exact prompt digest, resolved root, current timestamp, actual
   force argument and a concise reconciliation outcome. Write the complete
   UTF-8 receipt using a temporary file in the home and atomic replacement
   where supported. Verify its contents and ignored/untracked status. On
   failure, report the error and stop before task mutations.
3. Append a `resume` milestone to an existing applicable journal and refresh
   its handoff. Record the prompt path, reconciled state and next action;
   never record session secrets. Leave the saved prompt unchanged.
4. Briefly state the recovered objective, any material changes since pause,
   and the next action. Continue the authorized task in the same turn, following
   the prompt's reconciled continuation. The response after the opening status
   must carry out that work and report its results, or explain a concrete blocker
   or pending human decision. A receipt confirmation, summary, or offer to
   continue alone does not complete a resume.

The flag means context was read and reconciled, not that the task completed.
Write it before task execution so a later failure does not silently replay
the same work. To re-read that same prompt after an interruption, the user
invokes `resume-session --force`. A subsequent `pause-session` publishes a
fresh snapshot and clears the flag only after publication succeeds.
