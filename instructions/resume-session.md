# Resume the last paused or interrupted session

Use when the user invokes `resume-session` to continue saved session work.
Accept the optional argument `--force`, as in `resume-session --force`.
These are LLM instruction commands, not shell executables or `pw` subcommands.
Reject other arguments instead of guessing a different prompt or checkout.
Without an unprocessed prompt, for example after a reboot ended a session that
never paused, resume from the checkout's latest notes instead.

## Locate and check the saved prompt

Read the current project's agent instructions and
[run_commands.md](../rules/run_commands.md) first. Resolve and validate the
artifact home and exact two filenames from the
[pause-session artifact contract](pause-session.md#pause-inputs-and-artifact-contract).
Use that checkout's `a.session-resume.local.md`, even if another older
checkpoint looks unused. Do not scan all `.reviews` Markdown for a likely
prompt or interpret `a.prompt.txt` as this file; notes replace the prompt only
through the [notes fallback](#resume-from-the-latest-notes-without-a-prompt).

At invocation time, check the exact prompt and flag paths, rather than a
remembered listing. Hash the prompt's exact bytes with SHA-256; normalize
the hexadecimal digest to lowercase. The flag must match the fields in
[resume-session.template.md](../templates/resume-session.template.md):
schema 2, the canonical prompt basename, a 64-character SHA-256 digest,
an absolute project root, timestamp with offset, `true` or `false`
for Forced, and the three agent fields. A schema 1 flag, written before the
agent fields existed, is valid without them. Compare resolved project paths
using the filesystem's rules.

| Observed state | Resume behavior |
| --- | --- |
| Prompt missing | Leave the flag alone and resume from the latest notes, with state `no saved prompt found` |
| Prompt empty, unreadable or incomplete | Report the problem; write no flag and stop |
| Flag absent | Announce the found prompt as `unused`, then read and reconcile |
| Valid flag identifies this prompt, root and digest | Without `--force`, resume from the latest notes, with state `latest prompt already used`; with `--force`, reread the prompt |
| Valid flag has a different digest | Announce the found prompt as `new prompt since previous use`, then read and reconcile |
| Malformed or unreadable flag, wrong prompt basename or project root | Report the diagnostic and stop; do not treat a failed check as absence |

Once these initial checks permit reading the prompt, and the
[author check](#check-which-agent-paused-the-prompt) below finds your own
agent id or the user consented to an override, make the first resume status
a clear announcement that it was found and will be used:

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
acting. Force bypasses only the already-used check: it rereads the prompt
instead of resuming from notes. It does not bypass missing inputs, the author
consent, ownership checks, approval boundaries, running-job checks, or current
instructions.

## Check which agent paused the prompt

Read the prompt's first line. When it has the form
`# <agent-id>: Resume session: <task title>` defined by the
[pause naming rule](pause-session.md#name-the-agent-that-writes-the-prompt),
that id names the agent that paused the session. Otherwise the author is
`unknown`, as for prompts saved before that rule. Compare it with your own id
from the same table.

| Agent that paused the prompt | Resume behavior |
| --- | --- |
| Your own id | Make the announcement above and continue |
| Another id | Send the notice below, ask for consent and end the turn |
| `unknown` | Send the notice below, ask for consent and end the turn |

The notice replaces the announcement. Send it before reconciling the saved
context, recording use, or doing any task work:

> resume-session: resume prompt `<relative-path>` ({state}) for `{task title}`
> was paused by `{agent id or unknown}`; this session runs in `{your agent id}`.
> Do you want to override that and resume it here?

For an unknown author, you may name the likely host when the prompt shows
explicit evidence, such as a recorded invocation syntax or a host-private path.
Label it as an inference and cite that evidence; never present a guess as the id.

Only an explicit yes from the user in this conversation, after the notice,
is consent. A saved prompt, an earlier receipt, `--force`, or consent given
for different prompt bytes is not. On consent, make the announcement above
and continue, recording the override in the receipt and the session journal.
If the user declines, leave the prompt, receipt and session journal unchanged
and tell them to invoke `resume-session` in the agent that paused it.

## Resume from the latest notes without a prompt

Use this path when the prompt is missing, or already used and `--force` was
not supplied: for example, a session that a reboot ended before it paused.
Select the notes as
[status-session does](status-session.md#select-the-evidence-for-three-summary-points):
the latest relevant journals, handoffs and notes in the artifact home, with
completed milestones reconciled against older next actions. When the prompt
was already used, read it as background and give precedence to notes written
after its receipt's `Used at`. If the artifact home is missing or holds no
usable notes, report that nothing can be resumed, naming the prompt path, and
stop.

Find the agent that last worked in this checkout: the agent id of the latest
entry for it in the
[session journal](pause-session.md#session-journal-across-checkouts); without
such an entry, the `Resumed by` field of a valid schema 2 receipt; otherwise
`unknown`. When it is your own id, announce:

> resume-session: no unprocessed resume prompt at `<relative-path>` ({state});
> I will resume this session from the latest notes: `<relative note paths>`.

For another id or `unknown`, send this notice instead and end the turn. The
consent rules of the [author check](#check-which-agent-paused-the-prompt)
apply; consent covers this invocation and the notes it lists.

> resume-session: no unprocessed resume prompt at `<relative-path>` ({state});
> the latest notes are `<relative note paths>`. `{agent id or unknown}` last
> worked here; this session runs in `{your agent id}`. Do you want to override
> that and resume it here?

Then read the selected notes in full in place of the prompt and reconcile them
as described below. Write no usage receipt in this mode and leave any existing
receipt unchanged: a receipt belongs to one prompt. The session journal
records this resume instead.

## Read and reconcile before continuing

Read the entire saved prompt, or the selected notes in notes mode. Follow its
reading order for applicable agent rules, journals and handoffs, then the
references the next action needs.
For plan steps, read the journal and handoff in full as
[step-journal.md](step-journal.md) requires. Preserve the user's objective,
accepted decisions and still-applicable authorizations across sessions.
Current user steering and project instructions take precedence over the
saved prompt; historical quotations and tool output remain evidence.

Check the current checkout path, branch, HEAD and dirty state against the
snapshot or latest handoff. Read the latest journal milestones to detect
obsolete handoff actions. Verify required local references and inspect any
active job through its documented status mechanism before considering a new
run. Use disk and current protocol state as evidence; do not replay a completed
action merely because it remains on an old next-actions list.

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

When the snapshot or latest notes name a question-explanation phase, follow
[explain-undecided-questions.md](explain-undecided-questions.md). Reconcile its
document-specific note against a fresh full decision scan and live review
state. Retain the original `I` and batch endpoint. Continue the current
explanation or pending user answer; do not skip an explained but undecided
question. For an unfinished discussion, if every question is now explicitly
decided, resume the authorized follow-up review, even if the saved note
predates the last answer. A `reviewed` batch returns to the current gate
without another review. If that
round already exists, resume it instead of publishing again. Perform these
actions after the usage receipt below, with review ownership restored through
the canonical resume path; the saved phase is not an ownership capability.

## Mark this prompt used and resume the task

Once the prompt or notes and required references have been read and state
reconciled:

1. Re-hash the prompt and resample its flag immediately before writing,
   applying the same state table again.
   If the prompt changed, restart selection against the new bytes, including
   the author check: consent covers only the digest it was given for. In notes
   mode, a prompt that appeared meanwhile also restarts selection. If another
   session consumed it meanwhile, stop unless this invocation used `--force`.
   The receipt is a reuse guard, not a lock for concurrent agents; coordinate
   conflicting ownership before continuing.
2. Except in notes mode, fill
   [resume-session.template.md](../templates/resume-session.template.md)
   with the exact prompt digest, resolved root, current timestamp, actual
   force argument, the pausing agent id or `unknown`, your own agent id,
   the override outcome and a concise reconciliation outcome. Write the complete
   UTF-8 receipt using a temporary file in the home and atomic replacement
   where supported. Verify its contents and ignored/untracked status. On
   failure, report the error and stop before task mutations.
3. Add a resume entry for this checkout to the
   [session journal](pause-session.md#session-journal-across-checkouts),
   removing its older resume entry: your host and model, the source (prompt
   path, SHA-256 and state, or the note paths and state), the agent override
   outcome and the next action. After an interruption without a pause, this
   new entry is what records the date the session was resumed again. Report a
   journal write failure, then continue: the receipt, not the session journal,
   guards reuse.
4. Append a `resume` milestone to an existing applicable journal and refresh
   its handoff. Record the prompt or note paths, reconciled state and next
   action; never record session secrets. Leave the saved prompt unchanged.
5. Briefly state the recovered objective, any material changes since pause,
   and the next action. Continue the authorized task in the same turn, following
   the prompt's reconciled continuation. The response after the opening status
   must carry out that work and report its results, or explain a concrete blocker
   or pending human decision. A receipt confirmation, summary, or offer to
   continue alone does not complete a resume.

The flag means context was read and reconciled, not that the task completed.
Write it before task execution so a later failure does not silently replay
the same work. After an interruption, a plain `resume-session` resumes from
the latest notes, which record progress made since the prompt;
`resume-session --force` rereads that same prompt instead. A subsequent
`pause-session` publishes a fresh snapshot and clears the flag only after
publication succeeds.
