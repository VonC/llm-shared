# Pause and resume a working session

Use this workflow to leave a session with enough private context for another
session to continue its work. Run it in the checkout being paused, using an
LLM host that can read and write that checkout.

These are commands to the LLM, not shell executables or `pw` subcommands.

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
artifact home. It reports the path, then stops task work. Each pause replaces
that checkout's latest prompt; journals and evidence retain the longer history.

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
or the corresponding Grok/canonical file. The agent reads the latest prompt
and required notes, checks disk and job state, then writes
`a.session-resume.used.local.md` beside the prompt before continuing.

That flag records the prompt's SHA-256, checkout, time and whether force was
used. It confirms context recovery, not completion. A normal second invocation
reports that the prompt was already used and stops. It never falls back to an
older unused handoff. A fresh pause clears the flag after publishing the new
prompt, and the new digest also distinguishes it from an older receipt.

## Read the same checkpoint again

If the resumed session was interrupted before it saved a fresh checkpoint,
invoke `resume-session --force` (for example,
`$llm-shared:resume-session --force` in Codex or
`/resume-session --force` in Claude). This re-reads the same saved prompt and
updates the receipt after reconciliation. It does not waive permissions or
restart a recorded job automatically.

Use this after a crash only when you want to recover the same checkpoint.
To save work performed since that checkpoint, run `pause-session` again in the
current session first, then use a normal `resume-session` in the next one.

If the prompt is missing, return to the original session to create it. If a
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

Load [pause-session](../../instructions/pause-session.md) or
[resume-session](../../instructions/resume-session.md) directly. Grok's
portable adapters are [here](../../.grok/commands/); native discovery is
not assumed. A plain chat can help compose text but cannot verify a local
checkpoint or flag without filesystem tools.

For exact prompt selection, receipt fields, and failure cases, consult the
[artifact reference](../reference/artifact-files.md#session-checkpoints-and-usage-receipts).
