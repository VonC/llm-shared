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
   as a prompt addressed to the next session. Use actual paths and observed
   facts; replace every placeholder with a value, `none`, `not applicable`,
   or an explicit unknown. Include a fresh timestamp with numeric UTC offset.
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
5. Read back the final prompt and verify that it is ignored by Git and not
   tracked. If it or the flag is tracked, report the problem without changing
   the user's index. Do not claim a private checkpoint was saved safely.

Return the absolute prompt path, a brief description of what it preserves,
and the invocation `resume-session`. Then stop the session's task work.
