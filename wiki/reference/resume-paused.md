# resume_paused bulk resume command

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

🔁 `bin\resume_paused.bat`, wrapping `tools\resume_paused.py`, resumes every
paused agent session that waits in a TUIOS pane, from the routing each
checkout's pause handoff saved. One human launch authorizes the saved resume,
its requestor and reviewer roles and the author and role overrides they need,
through a marker bound to each target; no question follows. This page lists
its arguments, result lines, exit status and the limits it discloses. To use
it, follow [pause and resume a working session](../how-to/pause-and-resume-a-session.md#resume-every-waiting-pane-at-once).

## Invocation model of resume_paused

**Human-only.** Run it yourself from a terminal, inside a TUIOS pane or
outside TUIOS. Agents must never run it, not even with `--dry-run` or
`--help`, and not at a person's request. A recognized agent caller (an agent
environment marker such as `CLAUDECODE` or `CODEX_THREAD_ID`, or a
`claude.exe` or `codex.exe` ancestor process) is refused before any TUIOS
listing, with no input and exit status 1. The receiving workflows call the
separate, read-only validator `bin\resume_paused_validate.bat`; that one is
agent-callable.

The launcher self-locates llm-shared, runs its newest
`venvs\python_3*llm-shared*` Python and forwards every argument to
`tools\resume_paused.py` only. It needs no `senv.bat` activation.

```text
resume_paused [--dry-run] [--clear] [--except NAME[,NAME...]] [--switch-roles NAME[,NAME...]]
```

## Arguments of resume_paused

| Argument | Effect |
| --- | --- |
| `--dry-run` | Types nothing. Reports each prompt-bearing checkout with its exact marked commands, any clear, the conditional reviewer and every skip reason. |
| `--clear` | Claude uses `/clear` and Codex uses `/new`. A Claude clear after the pause with a proven quiet TUIOS event tail is reported as already cleared. Otherwise the launcher confirms a fresh clear before resuming. The option applies to the resumed agent only. |
| `--except NAME[,NAME...]` | Excludes TUIOS sessions, pane labels or checkout folder names, matched exactly and case-insensitively. Repeatable. An unmatched name refuses the whole run. |
| `--switch-roles NAME[,NAME...]` | Swaps the saved requestor and reviewer of a saved requestor pause with a recorded pair, by TUIOS session or checkout folder name. Repeatable. An unmatched name refuses the whole run; a matched checkout without such a pair fails. A switched pair needs the switch again on every later launch. |
| `-h`, `--help` | Prints the help, which restates the human-only contract and the limits below. |

There is no timeout override. Any other argument, an abbreviation or an empty
name is a syntax error, exit status 2, before any discovery.

## What one launch of resume_paused does

1. Classifies the caller and refuses a recognized agent.
2. Lists every pane once across TUIOS sessions; a failed listing refuses the
   run.
3. Plans each checkout holding a resume prompt: a used prompt reports its
   receipt; the private session journal, a manual attempt or prior dispatch for this prompt, or an outstanding author-override question in any pane can suppress another resume; the saved targets are validated against the
   live panes by full pane UUID, session, checkout and host; protected panes
   (the caller's own, excluded, blocked, holding a draft, busy, not ready)
   are skipped.
4. Takes a per-checkout guard without waiting; a guard another launch holds
   skips that checkout.
5. Re-checks every target immediately before each send, types the marked
   command as one shell-free argument, and proves its acceptance within a
   100-second budget. Only tool-owned, unsubmitted Codex input may get one
   recovery Enter; uncertain input is never retyped.
6. For a requestor, observes for at most 120 seconds that its receiver
   consumed the prompt and holds the current marked claim, then activates the
   missing reviewer only after positive no-wait evidence and the all-pane idle
   guard. A later launch continues only a verified missing reviewer, leaves an
   active reviewer alone and never resends an uncertain earlier delivery.

Checkouts are processed independently and concurrently; at most one input
operation is active per pane.

## Result lines of resume_paused

Each checkout holding a resume prompt, used prompts included, gets one line,
named by its folder, or by its full path when another reported checkout has
the same folder name. The last line counts the panes no reported checkout
targets. A run-wide refusal prints only its `REFUSED run:` line.

| Status | Meaning |
| --- | --- |
| `PLAN` | Dry run: what a launch would type. |
| `DONE` | Every planned input was accepted. |
| `PENDING` | A reviewer waits for takeover proof or for no-wait evidence; no input was sent to it. |
| `SKIP` | An expected skip: excluded, protected, used, already resuming, unusable routing, or a guard held by another launch. |
| `ERROR` | A classification failure of that checkout; independent checkouts continue. |
| `FAIL` | An execution failure: unconfirmed input or clear, a failed receiver, an unavailable guard. |

After the status come the title, the pausing agent and time, the prompt
state, the reason of a skip or error, the duplicate-resume evidence with its
known resumer and time or `unknown`, then each target: its role, host, TUIOS
session and label, short pane id, and its routing source with its validation
result, `(saved routing, validated)` or `(saved routing, not validated:
<reason>)`. A saved slot whose live pane runs no agent, such as a CMD shell,
reads `no LLM counterpart` (or `no LLM target`), never as a reviewer. A
checkout stopped on its routing says `routing unresolved: no target validated
or typed into`. A preview shows the exact marked command, its clear and its
takeover condition; a run shows the clear, the outcome, the receiver
observation (`prompt consumed`, `claimed g<n>`, `completion unconfirmed`), the
reason and any recovery Enter. Report-only notes follow in brackets. A
preview, for example:

```text
PLAN api: 'Fix the parser' paused by claude at 2026-11-07 00:06, prompt unused; requestor codex work/Codex api 77e5f39c (saved routing, validated): clear, then $llm-shared:resume-session --resume-paused <marker>; reviewer claude work/Claude api 2fd92f30 (saved routing, validated): after takeover, /review-resume --resume-paused <marker> [limits=claude-wait-scope]
SKIP old: 'Legacy pause' paused by claude at 2026-11-06 18:10, prompt unused; skip routing-missing; routing unresolved: no target validated or typed into
omitted 3 pane(s) without a prompt-bearing target; dry run, nothing typed
```

A run, for example:

```text
PENDING api: 'Fix the parser' paused by claude at 2026-11-07 00:06, prompt unused; requestor codex work/Codex api 77e5f39c (saved routing, validated): cleared, accepted, claimed g2; reviewer claude work/Claude api 2fd92f30 (saved routing, validated): pending: reviewer-wait-active [limits=claude-wait-scope]
DONE docs: 'Update the guide' paused by claude at 2026-11-07 00:30, prompt unused; requestor claude docs/Claude docs 0c4d5e6f (saved routing, validated): accepted, claimed g2; no LLM counterpart docs/cmd 1a2b3c4d (saved routing, not validated: target-not-agent): skipped: target-not-agent
SKIP old: 'Legacy pause' paused by claude at 2026-11-06 18:10, prompt unused; skip routing-missing; routing unresolved: no target validated or typed into
omitted 3 pane(s) without a prompt-bearing target
```

## Exit status of resume_paused

| Exit | Outcome |
| --- | --- |
| 0 | Success: every planned input accepted, expected skips, an empty plan, a reviewer pending takeover or no-wait evidence, or a receiver accepted with completion unconfirmed. |
| 1 | A failure: a recognized agent caller, a failed discovery, an unmatched `--except` or `--switch-roles` name, a classification error, a switch without a saved pair, unconfirmed input or clear, a marker mismatch or failed receiver, an unavailable guard. |
| 2 | Invalid command-line syntax. |

A dry run applies the same classification and name-validation failures.

## The limits=claude-wait-scope code

Every Claude reviewer activation outcome, and every preview showing a
conditional Claude activation, carries `limits=claude-wait-scope`. Before a
Claude reviewer is activated, the launcher checks the current shared reviewer waiters, ownership and visible panes. Five limits qualify those observations.

| Limit | Meaning |
| --- | --- |
| `detached-foreground-or-hook-work` | Processes detached by completed foreground commands or hooks may be missed (Q20=A). |
| `hook-configuration-history-unavailable` | Earlier hook-handler configuration history is unavailable (Q20=A). |
| `undetectable-backward-clock-change` | Backward clock changes since the last OS boot, offsetting ones included, can remain undetectable (Q21=A). |
| `roots-without-records` | Claude work outside visible panes and shared review waiters may be missed, including work surviving a parent’s exit, kill, `TaskStop` or timeout (Q26=A). |
| `running-local-command-not-yet-recorded` | A local shell command still running whose input is not yet recorded, and work it starts meanwhile, can be missed in a Claude root that has no TUIOS pane (Q27=B). |

The launcher checks for live shared `wait-request` and `wait-any-request` processes in the checkout. A surviving waiter after hibernation keeps the reviewer pending. A full restart removes that process. Unavailable process evidence also keeps the reviewer pending. An activation still requires the requestor's current marked claim and fresh idle-pane evidence. The ownership generation fences competing claims.

## Supported hosts and delivery evidence

Current Codex and Claude installations use TUIOS readiness and the visible empty editor. A styled empty-editor suggestion distinguishes the editor from an unsent draft. With suggestions hidden or a visually ambiguous blank input, the launcher leaves the pane alone. A changed editor layout produces a diagnostic for the affected checkout. Each host supplies its native resume, review-resume and clear commands. A schema 3 usage receipt proves the resumed pane consumed the saved prompt. The counterpart's current marked claim proves it took ownership.

Before typing, the launcher reserves the operation in `a.resume-paused.<prompt digest>.<phase>.local.json` in the checkout's configured review artifact home. A dry run creates no reservation. On an unconfirmed send, inspect the named pane, its usage receipt and current review ownership before acting. A clear reservation alone means the conversation may already have been cleared. If the command is still in the editor, review it there. If delivery failed and the prompt is unused, the operator can resume manually after checking the session. Leave the reservation in place to protect against automatic replay. On Windows, the manual receiver registers a counted attempt in `a.resume-paused.<prompt digest>.manual.local.json` before asking for consent. Bulk launches in any pane skip those prompt bytes even if the operator declines the override. A replacement prompt has its own digest.

If a Codex shell inherits a different pane UUID from a shared app-server, receiver validation refuses the marked command. Inspect the intended pane and the dispatch before resuming manually.

Prompts and schema 3 receipts keep the lines the installed `tuitp` launcher
reads. Its launch-time integration with this command is a separate, open
follow-up: see the
[deferred senv integration checklist](../../docs/v0.15.0/feature-request.v0.15.0.resume-paused.md#deferred-senv-integration-follow-up).
