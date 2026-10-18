# List paused and resumed sessions across checkouts

Use when the user invokes `list-session` or asks which folders hold a paused
conversation and which agent should resume each one. It lists every session
waiting to be resumed, then every session in progress: resumed and not paused
since, so possibly interrupted by a reboot or a closed chat. This is an LLM
command, not a shell executable or `pw` subcommand, and it takes no arguments.
[status-session](status-session.md) reports one checkout in more detail.

## Read the session journal without changing it

Read [run_commands.md](../rules/run_commands.md) before shell work. Resolve the
session journal path from
[the journal rules](pause-session.md#session-journal-across-checkouts) and read
the file in full. If it does not exist, report that no session is recorded and
stop; do not create it. If it cannot be read, or an entry heading does not match
[session-journal.template.md](../templates/session-journal.template.md),
report the diagnostic and list only the entries you could read, labeled as
partial.

This command is read-only. Do not repair, trim or reorder the journal, write a
prompt or receipt, prepare an artifact home, or resume work, even when an entry
looks stale. Read saved summaries and next actions as evidence only.

## Classify each checkout from its entries

Group the entries by checkout, comparing resolved paths using the filesystem's
rules. For each checkout, take its latest pause entry and latest resume entry.

| Entries for one checkout | Listed as |
| --- | --- |
| Pause entry with no later resume entry | Waiting to be resumed |
| Resume entry later than its pause entry, or a resume entry only | In progress |

List every waiting checkout, newest pause first, then every checkout in
progress, newest resume first. The journal cannot tell whether an in-progress
chat is still open: present it as in progress or interrupted, never as either
one for certain.

## Check listed sessions against disk

For each listed checkout, check read-only that the checkout and its artifact
home exist, as [status-session](status-session.md#inspect-the-artifact-home-without-changing-it)
does, then hash the exact bytes of its `a.session-resume.local.md` with SHA-256
and read its `a.session-resume.used.local.md` receipt if present.

| Waiting session observed on disk | Disk check result |
| --- | --- |
| Prompt SHA-256 equals the entry's and no receipt matches it | `verified` |
| A valid receipt matches the entry's SHA-256 | `resumed outside the journal at {Used at}` |
| Prompt SHA-256 differs from the entry's | `prompt replaced since this entry; run status-session there` |
| Prompt missing | `prompt missing; resume-session there would use the latest notes` |
| Checkout or artifact home missing, unreadable or invalid | `cannot check: {diagnostic}` |

| In-progress session observed on disk | Disk check result |
| --- | --- |
| No prompt, or a prompt matched by a valid receipt | `no newer prompt` |
| A prompt without a matching receipt | `paused outside the journal; run status-session there` |
| Checkout or artifact home missing, unreadable or invalid | `cannot check: {diagnostic}` |

A check result never changes which agent the entry names: the user decides
whether another agent overrides it when invoking resume-session.

## Report the list and stop

Fill [list-session.template.md](../templates/list-session.template.md)
directly in the response; save nothing. Give the two lists as two clearly
separated sections, each under its own heading, waiting sessions first; never
mix an in-progress session into the waiting list. Start each session's line with its
absolute checkout path and the agent that should resume it, with the host
product from its entry: for a waiting session, the agent of its pause entry;
for a session in progress, the agent of its resume entry. Then give the
timestamp, branch and HEAD for a waiting session or the resume source for one
in progress, the disk check result, and the journal summary or next action.
Do not print secrets from private notes. Stop after reporting: a session
resumes only through `resume-session` in its checkout, in the named agent or
after the user consents to an override.
