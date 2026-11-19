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

## Pause in a plan or read-only mode

A host's planning mode, such as Codex Plan Mode, does not prevent a pause.
Such a mode forbids changing repo-tracked state, and a pause changes none:
the prompt and its receipt are ignored and checked untracked above, the
step journal, handoff and question note it refreshes sit in the same ignored
artifact home, and the session journal lives outside every repository.
Writing them records the session; it carries out none of its plan. The user's
pause request asks for exactly these writes: make them in that mode as in any
other, then stop.

In that mode, write nothing else: no tracked file, no decision recorded in a
document, no command that carries the plan out. List such pending writes in
the prompt, as decisions held in the conversation only. Never skip the save
because of the mode alone, and never answer with a chat-only handoff before
trying it. Only a write the host itself rejects, through its sandbox or an
approval the user declines, stops the pause: report that rejection, give the
handoff in the chat and say that no checkpoint was saved.

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
Accept a receipt of schema 1, 2 or 3 as
[status-session](status-session.md#determine-whether-the-latest-prompt-is-unprocessed)
does, and classify it by its `Prompt`, `SHA-256` and `Project root` lines,
never by its schema. A valid receipt for the prompt's exact bytes makes the
prompt used, and one for other bytes makes it new since previous use. Another
schema, or a receipt that misses a line of its schema or carries another one,
is malformed: report the diagnostic and stop without replacing the prompt.
If that prompt is unused or new since previous use, compare it with this
pause, after gathering this pause's pausing pane and saved role as
[Record automatic resume routing](#record-automatic-resume-routing-in-the-handoff)
describes:

| Existing unused or new prompt compared with this pause | Before replacing it |
| --- | --- |
| Its agent id differs from yours or is missing | Ask |
| Its pausing pane differs from this pause's pausing pane, even with the same agent id | Ask |
| Its saved session role differs from this pause's saved role, even with the same agent id | Ask |
| Same agent id, and every pane or role known on both sides is equal | Replace without asking |

Read the existing prompt's pausing pane from its routing block's `pause.pane`
and its saved role from that block's `pause.session_role`. Without a routing
block that parses, its pane is unknown and its role is its `- Session role:`
value when that value is exactly one of the five role tokens, otherwise
unknown. Compare panes by full pane UUID and TUIOS session string, never by
label. A pane or role recorded as unknown, or missing from a legacy prompt,
for the existing checkpoint or the current pause, is not by itself a
difference; compare the remaining recorded fields. A legacy prompt without
pane or role fields therefore keeps the agent-id comparison. Compare
historical pausing identities, not intended future role assignments or a
recorded role switch.

Name the existing checkpoint's agent, pausing pane and saved role, marking
unavailable values as unknown: replacing it discards a checkpoint that was
never resumed. Ask it as a choice under
[interactive_menu.md](../rules/interactive_menu.md). If the user declines,
preserve the existing prompt and stop without writing a new one. This guard
applies at pause time only; it adds no confirmation to bulk resume. Keep one
latest checkpoint per checkout.

## Session journal across checkouts

Besides each checkout's prompt, pause-session and resume-session keep one
private session journal per user. It lists the paused and resumed sessions of
every checkout, so [list-session](list-session.md) can show which folder holds
which conversation and which agent should resume it.

- Path: `%USERPROFILE%\.llm-shared\sessions.journal.md`. Only where
  `USERPROFILE` is unset (Linux, macOS), use
  `$HOME/.llm-shared/sessions.journal.md`. Do not use `HOME` on Windows: a
  shell can point it at another folder, and other agents would not find it.
- A missing `.llm-shared` folder gets a `.gitignore` containing exactly `*`
  and a newline, and a missing journal the title and first paragraph of
  [session-journal.template.md](../templates/session-journal.template.md):
  the journal tool below creates both.
- Each entry follows one of that template's two forms: a level-two heading
  naming the event, agent id, timestamp and resolved checkout path, then its
  fields. Append new entries at the end of the file.
- Per checkout, keep only the latest pause entry and the latest resume entry.
  Writing a pause entry removes that checkout's older pause entry; writing a
  resume entry removes its older resume entry. Compare checkout paths using
  the filesystem's rules, and leave every other entry byte for byte.
- Write the journal only through the journal tool, never by hand: no editor,
  no regular-expression replacement, no one-off script, in any shell. Write
  your new entry alone, in the template's form, to a scratch file such as
  `a.tmp.session-journal-entry.md` in the artifact home. Then run two
  commands, each in its own shell call, never chained with each other or with
  the command that wrote the entry:

  1. `& "<LLM_SHARED_DIR>\bin\session_journal.bat" plan --add <entry file>`
     re-reads the journal, builds the new content in memory and refuses unless
     every other entry stays byte for byte and the entry count equals before,
     minus removed, plus added. It only reads the journal, and prints a JSON
     report. Check that `added` names your entry and that `removed` holds at
     most this checkout's older entry of the same kind; otherwise report the
     plan and do not apply it.
  2. `& "<LLM_SHARED_DIR>\bin\session_journal.bat" apply --manifest <manifest>`,
     with the `manifest` path the plan printed, replaces the journal only if it
     still has the bytes the plan read: after a timestamped backup (the newest
     50 are kept), through a temporary file beside it that is read back, then
     read back again.

  Where the Windows launcher does not apply, run
  `python3 -I <LLM_SHARED_DIR>/tools/session_journal.py` with the same
  arguments. Exit `2` means refused, with nothing written: fix the entry file,
  or plan again when the journal changed meanwhile. Never work around a
  refusal by editing the journal another way. Exit `3` means the replaced
  journal did not read back as planned: report it with the backup path it
  names.
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

For [question explanations](explain-undecided-questions.md), read and refresh
the document-specific continuation note and copy its phase into the pause
template. Preserve the fixed starting position `I`, endpoint and ordered IDs,
current/next/last undecided question, whether an explanation was delivered and
its explicit decision recorded, and the follow-up review authority or hold.
Run the full read-only decision scan: if the last answer was recorded but the
note still says `awaiting-user-decision`, reconcile it to
`follow-up-review-required`. The next action must resume explanation/decision
or initiate that review, not consolidate or restart the convergence menu.
If the follow-up was already published, record its exact round and resume it.

Keep private identifiers in the artifact home. Record credential locations
or access instructions, never credential values. Never persist review
ownership capabilities, tokens or session secrets in the prompt, receipt,
journal, logs or environment. A resumed review uses the identity and ownership
gates in [review-resume.md](review-resume.md), not a saved capability.

## Record automatic resume routing in the handoff

Fill the automatic resume routing section of
[pause-session.template.md](../templates/pause-session.template.md) on every
pause. The handoff must preserve enough information for a later human-launched
`resume_paused` invocation to select its targets without asking the person to
identify a pane or repeat a role assignment. Gather this information through
read-only inspection; never launch `resume_paused` or contact the counterpart
to obtain it.

When TUIOS is available, read `tuios list-agents --all-sessions --json` and
reconcile the caller's `TUIOS_PANE_ID`, when present, with that listing and
the resolved checkout. A command run by a process without its own console,
such as the shared Codex app-server daemon, can inherit pane variables from
another session. Record the pausing pane only when independent read-only
evidence agrees, such as that pane's screen or agent log showing this pause
request. Otherwise
record it as unknown with that reason.

Take identities from that JSON listing, never from its table view. A pane's
full UUID is its record's `window_id`, 36 characters long; the table view
prints only its first 8 characters. Its TUIOS session identity is the
record's `session` string, the session name the selector uses, not a numeric
id. Its label is the record's `name`, a supplementary label only, and its
agent session id is the record's `agent_session_id` when that is not empty.

Use the exact exchange's read-only role state and existing task notes to
establish assignments. Exchange role state names agent host natures, not
panes. For a same-host counterpart, record the independent evidence linking
the role to that pane, such as its agent log or screen showing its latest
`review-resume` role. A listing of two panes with
the same host does not establish which one owns a role; record the identity
evidence rather than selecting by listing order. A host name or a label alone
cannot distinguish multiple panes running the same LLM.

Separate historical authorship and the saved session role from intended
resume assignments. The pause author and saved role describe this pause only:
historical authorship never implies an intended requestor role. A session
holding the requestor role of a live exchange saves the role `requestor`, and
one holding its reviewer role saves `reviewer`. Preserve the user's latest
explicit role-switch direction and its source as the assignment source;
otherwise retain the verified current assignment. Record identity and evidence
only, never review ownership capabilities, tokens or credentials. Saving an
intended assignment does not itself change ownership or prove that a later
takeover has succeeded.

If TUIOS is unavailable, a pane cannot be identified, or an assignment is
unresolved, write an explicit unknown and its reason. Do not ask a routing
selection question or invent an identifier just to complete the pause.
Preserve the rest of the checkpoint. The future bulk resume must report
missing, stale or conflicting routing and send no input to unresolved targets,
without asking the person to choose a pane or supply routing arguments.
Routing is evidence to validate against live checkout, host, session and pane
identity before input, not permission to reuse an id blindly or choose the
first matching pane. Old prompts without a routing block, including those
with only an earlier prose routing table, remain readable by the ordinary
session workflow; bulk resume skips them and reports their routing limitation
without an interactive migration question.

### Write the routing JSON block

Write the routing as exactly one fenced block whose opening line is exactly
`` ```json resume-paused-routing `` and which holds one JSON object of schema
`resume-paused-routing`, version `1`. That block is the only routing source a
bulk resume reads. Write each part with exactly the keys below.

| JSON part | Value to record |
| --- | --- |
| `schema`, `version` | `"resume-paused-routing"` and the integer `1` |
| `pause.checkout` | The resolved absolute checkout root, as the prompt's `Project root` |
| `pause.snapshot` | The prompt's `Snapshot` timestamp |
| `pause.author` | Your agent id, as on the prompt's first line |
| `pause.session_role` | `implementation`, `requestor`, `reviewer`, `documentation` or `other` |
| `pause.pane` | The pausing pane: `host` (your agent id), `session`, `pane_id` and `label` |
| `observation` | `observed_at` (timestamp with numeric UTC offset), `assignment_source` (the recorded user role-switch direction with its date, or `verified current assignment`) and `evidence` (the read-only sources used) |
| `targets.resumed` | The target that receives the resume: a single agent, or the requestor or reviewer of a pair |
| `targets.requestor`, `targets.reviewer` | The intended requestor and reviewer of a paired review |
| `exchange` | `family` (`code` or `specification`), `document` (checkout-relative POSIX path of the reviewed document or implementation plan), `implementation_step` (the plan step of a code review, otherwise `null`), `umbrella` (checkout-relative umbrella draft path, or `null`), `occurrence` (a positive integer) and `round` (the round at pause, or `null`) |

A target object holds `role` (its intended role), `host` (`claude` or
`codex`), `session`, `pane_id`, `label`, `checkout` (the pause checkout),
`agent_session_id` (a string, or `null`) and `evidence` (what ties that pane
to that role). The exchange identifies the exact review exchange for
`resume-inspect` and `claim`; its `round` records the round at pause only; a
resume selects the current round from live protocol state.

- Unknown: replace the pausing pane, a target or the exchange with
  `{"unknown": "<reason>"}` when its evidence is unavailable, stale or
  contradictory. Keep the rest of the pause.
- Single-agent pause: `targets.requestor`, `targets.reviewer` and `exchange`
  are each `{"not_applicable": "<reason>"}`, all three or none. The resumed
  target is never not applicable.
- Paired pause: the requestor slot's role is `requestor` and the reviewer
  slot's role is `reviewer`. When the resumed target is one of them, write the
  identical object in both places.
- Every target's `checkout` is the pause checkout, and one pane UUID never
  appears in two different target objects.
- Write each checkout as an absolute Windows path with an upper-case drive
  letter, backslash separators and no trailing separator, with the same
  spelling everywhere; JSON escapes each backslash as `\\`.
- Strings are single lines without control characters. Write no other key,
  no duplicate key and no comment.

### Render the readable routing table

After the block and one empty line, write the readable table rendered from
that JSON. Its header line is exactly `| Routing item | Value |`, then
`| --- | --- |`, then these thirteen rows in this order. Each code span below
is one accepted cell, where `<...>` stands for the JSON value. Write `none`
for an empty label and for a `null` agent session id, umbrella or round, and
`not applicable` for a `null` implementation step. Escape a `|` inside a
value as `\|`.

| Row | Cell rendered from the JSON |
| --- | --- |
| Routing schema | `resume-paused-routing version 1` |
| Pause checkout | `<pause.checkout>` |
| Pause snapshot | `<pause.snapshot>` |
| Pause author | `<pause.author>` |
| Saved session role | `<pause.session_role>` |
| Pausing pane | `<host> in TUIOS session <session>, pane <pane_id>, label <label>` or `unknown: <reason>` |
| Observed at | `<observation.observed_at>` |
| Assignment source | `<observation.assignment_source>` |
| Observation evidence | `<observation.evidence>` |
| Resumed agent | `<role> on <host> in TUIOS session <session>, pane <pane_id>, label <label>, checkout <checkout>, agent session <agent_session_id>; evidence: <evidence>` or `unknown: <reason>` |
| Requestor | `<role> on <host> in TUIOS session <session>, pane <pane_id>, label <label>, checkout <checkout>, agent session <agent_session_id>; evidence: <evidence>`, `not applicable: <reason>` or `unknown: <reason>` |
| Reviewer | `<role> on <host> in TUIOS session <session>, pane <pane_id>, label <label>, checkout <checkout>, agent session <agent_session_id>; evidence: <evidence>`, `not applicable: <reason>` or `unknown: <reason>` |
| Review exchange | `<family> review of <document>, implementation step <implementation_step>, umbrella <umbrella>, occurrence <occurrence>, round at pause <round>`, `not applicable: <reason>` or `unknown: <reason>` |

Write no other routing table. A second routing block or table, or a cell that
differs from this rendering, makes a bulk resume refuse this routing as an
error; ordinary `resume-session` still reads the prompt.

For example, a code-review requestor pausing beside its reviewer writes this
block and table, the exact rendering of its JSON:

````markdown
```json resume-paused-routing
{
  "schema": "resume-paused-routing",
  "version": 1,
  "pause": {
    "checkout": "C:\\work\\example",
    "snapshot": "2026-11-19T00:31:00+01:00",
    "author": "claude",
    "session_role": "requestor",
    "pane": {
      "host": "claude",
      "session": "example",
      "pane_id": "5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b",
      "label": "Claude impl"
    }
  },
  "observation": {
    "observed_at": "2026-11-19T00:30:12+01:00",
    "assignment_source": "verified current assignment",
    "evidence": "tuios list-agents --all-sessions --json; review-exchange role state"
  },
  "targets": {
    "resumed": {
      "role": "requestor",
      "host": "claude",
      "session": "example",
      "pane_id": "5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b",
      "label": "Claude impl",
      "checkout": "C:\\work\\example",
      "agent_session_id": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d",
      "evidence": "own pane in list-agents; requestor of the exchange role state"
    },
    "requestor": {
      "role": "requestor",
      "host": "claude",
      "session": "example",
      "pane_id": "5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b",
      "label": "Claude impl",
      "checkout": "C:\\work\\example",
      "agent_session_id": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d",
      "evidence": "own pane in list-agents; requestor of the exchange role state"
    },
    "reviewer": {
      "role": "reviewer",
      "host": "codex",
      "session": "example",
      "pane_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f",
      "label": "Codex review",
      "checkout": "C:\\work\\example",
      "agent_session_id": null,
      "evidence": "its screen shows its latest review-resume as reviewer"
    }
  },
  "exchange": {
    "family": "code",
    "document": "docs/v1.2.0/plan.v1.2.0.example.md",
    "implementation_step": "3",
    "umbrella": null,
    "occurrence": 1,
    "round": 2
  }
}
```

| Routing item | Value |
| --- | --- |
| Routing schema | resume-paused-routing version 1 |
| Pause checkout | C:\work\example |
| Pause snapshot | 2026-11-19T00:31:00+01:00 |
| Pause author | claude |
| Saved session role | requestor |
| Pausing pane | claude in TUIOS session example, pane 5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b, label Claude impl |
| Observed at | 2026-11-19T00:30:12+01:00 |
| Assignment source | verified current assignment |
| Observation evidence | tuios list-agents --all-sessions --json; review-exchange role state |
| Resumed agent | requestor on claude in TUIOS session example, pane 5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b, label Claude impl, checkout C:\work\example, agent session 9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d; evidence: own pane in list-agents; requestor of the exchange role state |
| Requestor | requestor on claude in TUIOS session example, pane 5f0e6c1a-2b3d-4e5f-8a9b-0c1d2e3f4a5b, label Claude impl, checkout C:\work\example, agent session 9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d; evidence: own pane in list-agents; requestor of the exchange role state |
| Reviewer | reviewer on codex in TUIOS session example, pane c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f, label Codex review, checkout C:\work\example, agent session none; evidence: its screen shows its latest review-resume as reviewer |
| Review exchange | code review of docs/v1.2.0/plan.v1.2.0.example.md, implementation step 3, umbrella none, occurrence 1, round at pause 2 |
````

## Publish the latest prompt and finish pausing

1. Fill [pause-session.template.md](../templates/pause-session.template.md)
   as a prompt addressed to the next session. Start its first line with your
   agent id. Use actual paths and observed facts; replace every placeholder
   with a value, `none`, `not applicable`, or an explicit unknown. Include a
   fresh timestamp with numeric UTC offset. Write the `- Session role:` line
   as the routing's `pause.session_role` token alone, and the routing block
   and its table as
   [Record automatic resume routing](#record-automatic-resume-routing-in-the-handoff)
   describes.
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
   agent id and that it is ignored by Git and not tracked. Also check that
   the routing block parses as one strict JSON object and that each table
   cell equals its rendering from the JSON. If it or the flag
   is tracked, report the problem without changing the user's index. Do not
   claim a private checkpoint was saved safely.
6. Add a pause entry for this checkout to the
   [session journal](#session-journal-across-checkouts) with the journal
   tool's plan and apply commands, which remove its older pause entry: your
   host and model, branch and short HEAD, the prompt's
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
