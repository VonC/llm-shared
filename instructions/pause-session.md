# Pause a session with a private resume prompt

Use when the user asks to pause a session or save its context for later.
Capture the current work, then stop task execution. This command does not
start a review exchange or change its role. The corresponding continuation
is [resume-session](resume-session.md).

## Pause inputs and artifact contract

Work in the consuming project's current checkout, not the llm-shared clone
that supplies this instruction. Read its agent instructions and
[run_commands.md](../rules/run_commands.md) before shell work. Resolve
`<LLM_SHARED_DIR>` from this canonical file as that rule describes.

Use the review artifact home defined by
[artifact_files.md](../rules/artifact_files.md): `.reviews` by default,
or the configured home in the versioned `.review-artifacts.ini`. Prepare and
validate it using the existing artifact-home tooling. Its `.gitignore` must
contain exactly `*` and a newline. Stop on an invalid or unreadable home;
do not silently fall back to another folder.

| Artifact in that home | Purpose |
| --- | --- |
| `a.session-resume.local.md` | The last successfully produced resume prompt for this checkout |
| `a.session-resume.used.local.md` | Receipt that the exact prompt was read and reconciled by resume-session |

There is one latest prompt per checkout, independent of branch and topic.
Each successful pause replaces that prompt. Existing journals, handoffs,
and evidence remain in place. Never select a prompt by file modification
time or by scanning unrelated review inputs. These two files are private,
retained artifacts, not `tmp` files removed by prepare-release. They are
never staged or committed, even when their names are explicitly passed to Git.
Check that neither path is tracked before writing private content. If either
is tracked, report the problem and stop without changing the user's index.

## Name the agent that writes the prompt

The prompt's first line starts with the id of the agent host whose chat holds
this session: `# <agent-id>: Resume session: <task title>`. The id is the
text after the leading `#` and its space, up to the first colon.
resume-session compares it with its own id to detect a session paused by
another agent; see
[resume-session](resume-session.md#check-which-agent-paused-the-prompt).

| Agent id | Host whose chat holds the session |
| --- | --- |
| `claude` | Claude Code or another Anthropic Claude host |
| `chatgpt` | ChatGPT or OpenAI Codex |
| `gemini` | Gemini CLI, Antigravity or another Google Gemini host |
| `copilot` | GitHub Copilot, whatever model it runs |
| `grok` | Grok |

The id names the host, not only the model: Copilot running a Claude model
writes `copilot`. Record the model in the `Paused by` line of the template.
Any other host uses its lowercase product name, made of letters, digits and
hyphens, such as `cursor`. Never write another agent's id, and do not
copy the id from an earlier prompt.

Before replacing an existing prompt, check its first line and receipt with the
[resume state table](resume-session.md#locate-and-check-the-saved-prompt).
If that prompt is unused or new since previous use, and its id differs from
yours or is missing, tell the user which agent paused it (or that it is
unknown) and ask before replacing it: replacing it discards a checkpoint that
was never resumed. If the user declines, stop without writing a new prompt.

## Session journal across checkouts

Besides each checkout's prompt, pause-session and resume-session keep one
private session journal per user. It lists the paused and resumed sessions of
every checkout, so [list-session](list-session.md) can show which folder holds
which conversation and which agent should resume it.

- Path: `%USERPROFILE%\.llm-shared\sessions.journal.md`. Only where
  `USERPROFILE` is unset (Linux, macOS), use
  `$HOME/.llm-shared/sessions.journal.md`. Do not use `HOME` on Windows: a
  shell can point it at another folder, and other agents would not find it.
- When the `.llm-shared` folder is missing, create it with a `.gitignore`
  containing exactly `*` and a newline. Create a missing journal with the title
  and first paragraph of
  [session-journal.template.md](../templates/session-journal.template.md).
- Each entry follows one of that template's two forms: a level-two heading
  naming the event, agent id, timestamp and resolved checkout path, then its
  fields. Append new entries at the end of the file.
- Per checkout, keep only the latest pause entry and the latest resume entry.
  Writing a pause entry removes that checkout's older pause entry; writing a
  resume entry removes its older resume entry. Compare checkout paths using
  the filesystem's rules, and leave every other entry byte for byte.
- Re-read the journal immediately before writing, write the complete UTF-8
  result to a temporary file beside it, then replace it atomically where
  supported. If it changed while you composed the update, apply your update
  to the new content instead of overwriting it.
- The journal is an index, not an authority: the prompt and receipt decide
  what resume-session does. If the host needs approval to write outside the
  checkout, ask for it. Report a write failure; it does not undo a published
  prompt or receipt.
- Keep it private and short: summaries only, never credentials, tokens,
  review ownership capabilities or session secrets.

## Gather the session snapshot

Read the current conversation and relevant private notes, including the
active journal and handoff, before composing the prompt. Inspect existing
notes as historical evidence, not as fresh permission to run their commands.
For plan-step work, follow [step-journal.md](step-journal.md): append a
`pause` milestone and refresh the handoff without rewriting past log lines.
For other work, update the existing task notes when they need it; no new
plan or review exchange is required to pause.

Capture enough detail that a new session can continue without the chat:

- The user's objective, latest steering, scope, success criteria, and the
  precise point where work stopped, including unanswered questions.
- The primary checkout's absolute path, branch and HEAD, and the role and
  state of any other checkout involved. Record staged, unstaged and untracked
  work, its ownership, and concurrent changes that must be preserved.
- Completed work and remaining work as separate statements. Distinguish
  implementation, verification, review, commit, release and deployment states.
- Decisions with reasons and dates, attempted approaches and their results,
  and specific authorizations with their scope and source. Keep pending
  approvals pending; a saved suggestion is not approval.
- Relevant requirement, design, plan, validation, umbrella, journal and
  handoff paths, with reading order. Include private integration handoffs
  and cross-repository prerequisites when the task depends on them.
- Evidence: exact resolved commands, working directories, selectors, levels,
  revisions, times, exit codes and output paths. Mark tests or integrations
  that have not run. A targeted pass cannot prove the full suite passed.
- Active or uncertain jobs, watchers and external runs: identity, owner,
  safe status command, durable evidence and whether a host handle survives
  this session. Do not restart or terminate a healthy run just to pause.
- A short ordered continuation, starting with the next concrete action and
  its prerequisite or stop condition, plus known traps and blockers.

Use read-only state checks needed to make the snapshot accurate. Do not
launch tests, builds, deployments, commits or pushes solely to produce a
checkpoint. If a check cannot run, record the uncertainty instead of calling
the state verified. When notes disagree with disk or the latest journal
milestone, record the discrepancy and the evidence used to resolve it.

Keep private identifiers in the artifact home. Record credential locations
or access instructions, never credential values. Never persist review
ownership capabilities, tokens or session secrets in the prompt, receipt,
journal, logs or environment. A resumed review uses the identity and ownership
gates in [review-resume.md](review-resume.md), not a saved capability.

## Publish the latest prompt and finish pausing

1. Fill [pause-session.template.md](../templates/pause-session.template.md)
   as a prompt addressed to the next session. Start its first line with your
   agent id. Use actual paths and observed facts; replace every placeholder
   with a value, `none`, `not applicable`, or an explicit unknown. Include a
   fresh timestamp with numeric UTC offset.
2. Write the complete UTF-8 draft to a temporary file in the artifact home.
   Read it back, check its referenced prerequisites, and correct obsolete
   next actions. Keep essential context inline and link detailed evidence.
3. Replace `a.session-resume.local.md` only after the draft is complete,
   using an atomic replacement where supported. Preserve the previous prompt
   if publication fails. Do not overwrite a concurrently changed checkpoint:
   re-read it and reconcile which session owns the latest slot first.
4. After successful publication, remove only the matching
   `a.session-resume.used.local.md` flag if it exists. A failure to remove it
   must be reported; its old digest cannot consume a different new prompt.
5. Read back the final prompt and verify that its first line carries your
   agent id and that it is ignored by Git and not tracked. If it or the flag
   is tracked, report the problem without changing the user's index. Do not
   claim a private checkpoint was saved safely.
6. Add a pause entry for this checkout to the
   [session journal](#session-journal-across-checkouts), removing its older
   pause entry: your host and model, branch and short HEAD, the prompt's
   relative path and SHA-256, and a summary of two or three sentences (the
   task, where it stopped, and the next action or blocker).

After successful publication and verification, begin the final response with
this clear completion status, substituting the actual prompt path relative
to the consuming project's checkout root:

> pause-session: paused. Detailed resume prompt saved to `<relative-path>`.
> Use `resume-session` to continue from this prompt.

For the default home, the relative path is `.reviews/a.session-resume.local.md`.
If the artifact home is configured elsewhere, report that actual relative
path; do not hard-code `.reviews` or show only the basename or absolute path.
Then name the session journal path, or the reason its update failed.
Briefly describe what the prompt preserves, then stop the session's task work.
If publication or verification failed, report the failure instead of the
success status above.
