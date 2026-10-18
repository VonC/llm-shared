# Pause and resume a working session

Use this workflow to leave a session with enough private context for another
session to continue its work. Run it in the checkout being paused, using an
LLM host that can read and write that checkout.

These are commands to the LLM, not shell executables or `pw` subcommands.

## Invocation model

The user invokes each command in the agent session; the AI then follows its
instruction: it reports or lists the saved state, saves the prompt, or reads,
reconciles and continues the saved work. The AI never pauses or resumes on its
own initiative, and only the user can consent to resuming a session that
another agent paused.

## Check what is waiting before continuing

Invoke `status-session` to inspect the saved state without resuming work:

| Host | Invocation |
| --- | --- |
| ChatGPT/Codex with the llm-shared plugin | `$llm-shared:status-session` |
| Claude Code or Copilot skills | `/status-session` |
| Gemini through Antigravity workflows | `/status-session` |
| Grok with filesystem access | Ask it to read `.grok/commands/status-session.md` in the llm-shared clone |
| Another file-capable LLM | Ask it to read `instructions/status-session.md` in the llm-shared clone |

The first line tells you whether an unprocessed resume prompt exists, names
its path relative to your checkout, and which agent paused it. Exactly three
points follow: objective, progress, and next actions or blockers, with source
paths. For example:

> status-session: unprocessed resume prompt found at `.reviews/a.session-resume.local.md`
> (unused), paused by `claude`. Summary of the saved prompt; no work resumed.

When there is no prompt, or the exact prompt has already been used, the opening
says `no unprocessed resume prompt`. The three points then summarize the latest
notes, handoffs and journals in the artifact home, reconciling completed journal
entries with older next-action lists. Missing notes or uncertain state are
reported explicitly; an unreadable receipt is not treated as an absent one.

Status leaves the prompt, receipt and notes unchanged and creates no folder
when the artifact home is missing. It does not execute the recorded actions.
To continue a pending task, invoke `resume-session` as described below.

## Find which folder holds which paused session

Invoke `list-session` from any checkout, with the same host syntax as
`status-session` (`$llm-shared:list-session` in Codex, `/list-session` in
Claude Code, Copilot or Antigravity, `.grok/commands/list-session.md` for
Grok). It reads the private session journal
`%USERPROFILE%\.llm-shared\sessions.journal.md` (`$HOME/.llm-shared/` where
`USERPROFILE` is unset) and lists each folder with a session waiting to be
resumed. Each line starts with the folder and the agent that should resume it,
then the pause time, branch and HEAD, whether the prompt still matches on disk,
and a short summary. Every session in progress follows: resumed and not paused
since, so possibly interrupted by a reboot. After a reboot, invoke
`resume-session` in each of those folders, in the named agent, to resume from
the latest notes. For example:

> list-session: 2 session(s) waiting to be resumed, from `C:\Users\you\.llm-shared\sessions.journal.md`.
>
> 1. `C:\Users\you\git\app`: resume with `chatgpt` (OpenAI Codex), paused at
>    2026-10-17T01:45:20+02:00 on `feat/spec` at `163d276`; verified. ...

Each pause adds an entry with a summary of two or three sentences; each resume
adds one naming its source and agent. Per folder, the journal keeps only the
latest pause entry and the latest resume entry, so it stays small. Like
status, listing changes no file.

## Save the current session before leaving

Invoke the pause skill in your host:

| Host | Invocation |
| --- | --- |
| ChatGPT/Codex with the llm-shared plugin | `$llm-shared:pause-session` |
| Claude Code or Copilot skills | `/pause-session` |
| Gemini through Antigravity workflows | `/pause-session` |
| Grok with filesystem access | Ask it to read `.grok/commands/pause-session.md` in the llm-shared clone |
| Another file-capable LLM | Ask it to read `instructions/pause-session.md` in the llm-shared clone |

Give the consuming checkout path explicitly when it could be confused with
the llm-shared clone. The agent refreshes existing notes and saves the latest
prompt as `.reviews/a.session-resume.local.md`, or in the configured review
artifact home. On success, its final response starts with:

> pause-session: paused. Detailed resume prompt saved to `.reviews/a.session-resume.local.md`.
> Use `resume-session` to continue from this prompt.

The reported path is relative to the consuming checkout root and reflects any
configured artifact home. The agent then names the session journal it updated,
briefly describes the saved context, and stops task work. Each pause replaces that checkout's latest prompt; journals
and evidence retain the longer history.

The prompt's first line starts with the id of the agent that paused it:
`claude`, `chatgpt` (ChatGPT or Codex), `gemini`, `copilot`, `grok`, or
another host's lowercase name, as in `# claude: Resume session: ...`. If the
checkout already holds a prompt from another agent that was never resumed,
the pause asks before replacing it.

The prompt preserves the objective, user steering, permissions, decisions,
verified state, dirty-work ownership, evidence, live runs, blockers and ordered
next actions. Existing jobs can remain running. A saved prompt neither
finishes those jobs nor grants new authority to an external system.

Before leaving, check the reported file exists and that the saved next action
matches where you intended to stop. The agent fills the
[pause template](../../templates/pause-session.template.md); the
[template reference](../reference/templates.md#session-continuity-templates)
lists the context it preserves.

## Continue from a new session

Open the same checkout and invoke `resume-session` using the same host syntax,
or the corresponding Grok/canonical file. Once the agent finds an eligible
prompt, its opening resume status names the relative path and confirms its use:

> resume-session: found resume prompt `.reviews/a.session-resume.local.md` (unused); I will use it to resume this session.

Resume in the agent that paused the session. When the prompt's first line
names another agent, or no agent (prompts saved before that line existed),
the agent makes no announcement. It names the pausing agent and asks first:

> resume-session: resume prompt `.reviews/a.session-resume.local.md` (unused)
> for `Sentinel scope agreement` was paused by `chatgpt`; this session runs
> in `claude`. Do you want to override that and resume it here?

Answer yes to continue in the current agent; the receipt records the override.
Otherwise, invoke `resume-session` in the agent it names. `--force` does not
skip this question. For an unnamed author, the agent may suggest a likely host
from evidence in the prompt, labeled as a guess.

The state can also be `new prompt since previous use` or `forced reread`.
The agent then reads the latest prompt and required notes, checks disk and job
state, and writes `a.session-resume.used.local.md` beside the prompt before
continuing the authorized work in the same turn. Its response goes on with the
work instructed by the reconciled prompt and its results, or a concrete blocker
or pending human decision; it does not stop at the announcement or a summary.
If the initial checks prevent resuming, the opening diagnostic names the
relative path and reason instead of promising to use the prompt.

That flag records the prompt's SHA-256, checkout, time and whether force was
used. It confirms context recovery, not completion. A second invocation
without `--force` finds the prompt already used and resumes from the latest
notes instead, as after a reboot. It never falls back to an older unused
prompt. A fresh pause clears the flag after publishing the new
prompt, and the new digest also distinguishes it from an older receipt.

## Resume after a reboot without a pause

If a session ended without pausing, for example on a reboot, invoke
`resume-session` as usual. With no unprocessed prompt (none saved, or the
latest one already used), it resumes from the latest notes and names them:

> resume-session: no unprocessed resume prompt at `.reviews/a.session-resume.local.md`
> (latest prompt already used); I will resume this session from the latest
> notes: `.reviews/a.my-topic.step2.journal.md`, `.reviews/a.my-topic.step2.handoff.md`.

It selects the notes as `status-session` does, reads an already used prompt
as background, writes no usage receipt, and records the new resume date in the
session journal. If the journal says another agent last worked in that folder,
or has no entry for it, it asks for consent first, as for a prompt. Without
usable notes, it reports that nothing can be resumed.

## Read the same checkpoint again

To restart from the saved prompt itself rather than from later notes,
invoke `resume-session --force` (for example,
`$llm-shared:resume-session --force` in Codex or
`/resume-session --force` in Claude). This re-reads the same saved prompt and
updates the receipt after reconciliation. It does not waive permissions or
restart a recorded job automatically.

Use this after a crash only when you want to recover the same checkpoint.
To save work performed since that checkpoint, run `pause-session` again in the
current session first, then use a normal `resume-session` in the next one.

If the prompt is missing and the latest notes are too thin, return to the
original session, when it is still open, to pause it. If a
required file is missing or a different branch has unrelated work, resolve
that discrepancy first; the workflow keeps the usage receipt unchanged.
Malformed flags are reported rather than silently discarded. Keep the
prompt and receipt out of Git. For a review exchange, the resumed agent
also follows the existing review recovery and ownership gates.

For an independent review, a bare `resume` invokes
[review recovery](recover-an-independent-review.md). Use `resume-session` to
recover the broader saved task context; it still performs that review's
ownership checks before continuing the exchange. Neither command approves a
pending commit or review decision.

## Use the canonical files when discovery is unavailable

Load [list-session](../../instructions/list-session.md),
[status-session](../../instructions/status-session.md),
[pause-session](../../instructions/pause-session.md) or
[resume-session](../../instructions/resume-session.md) directly. Grok's
portable adapters are in [`.grok/commands/`](../../.grok/commands/); native discovery is
not assumed. A plain chat can help compose text but cannot verify a local
checkpoint or flag without filesystem tools.

For exact prompt selection, receipt fields, and failure cases, consult the
[artifact reference](../reference/artifact-files.md#session-checkpoints-and-usage-receipts).
