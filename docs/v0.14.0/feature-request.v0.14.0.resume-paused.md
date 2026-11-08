# Resume paused agent panes across TUIOS sessions

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Topic: resume-paused
- Source: [resume-paused draft](draft.v0.14.0.resume-paused.md)
- Deferred follow-up: [senv tuitp integration](#deferred-senv-integration-follow-up)

## Draft revision that introduces resume-paused

As a person working with several agent panes in persistent TUIOS sessions,
I want one command to resume the checkouts whose pause prompts are still
waiting, so that I do not have to visit every Windows Terminal tab and type
the appropriate agent command by hand.

The draft records a successful manual run on 2026-11-07 across six panes
(five Claude panes and one Codex pane). It requests a shared tool for agents
that are already running. Launch-time resumption already exists in senv's
`tuitp`, but does not resume those existing panes.

That agent-run experiment is evidence of TUIOS behavior, not an authorized
launch method for the delivered tool. Q16=B requires the person to launch it
from a terminal or shell; agents never launch it, even when asked. No review
role-isolation exception is introduced. Q20=A enforces this by refusing every
invocation, including `--dry-run`, from a recognized agent caller pane.

## Current behavior before the v0.14.0 resume-paused change

- `pause-session` saves `a.session-resume.local.md` in each checkout's
  artifact home. `resume-session` consumes it and records its SHA-256 in
  `a.session-resume.used.local.md`.
- People visit each pane, optionally clear its conversation, then enter
  `/resume-session` for Claude or `$llm-shared:resume-session` for Codex.
- TUIOS exposes Claude's harness and agent log, but Codex can appear with
  harness `(none)` and source `program`. Codex program status can be stale,
  and a successful `ask-agent` response does not prove the prompt was taken.
- Git Bash can rewrite slash-prefixed command arguments into Windows paths.
  Targeting another session with `ask-agent -s ... -w ...` can fail because
  its default caller pane is resolved in the target session.
- Clearing a conversation leaves background shells running. A resumed agent
  can consequently start a duplicate watcher.

## Command contract for resume-paused

Provide a `resume_paused` command through a `bin` launcher and a `tools`
module, following the arrangement of other llm-shared tools.

User clarification on 2026-11-08: one human invocation of `resume_paused` must complete the resolved resume and role assignments without further confirmation. The invocation authorizes consuming the intended pause in the resolved target and establishing its resolved requestor/reviewer roles, including required pause-author and recorded-role overrides. The human launch is the authorization. Saved intended assignments set its scope and are carried into the target workflows with it; the saved file alone grants no new permissions. Q28=A carries that launch authorization through a validated target-bound command marker, without another question. Under the subsequent Q25 user amendment, resolve targets and assignments from the pause handoff, validated against live evidence, without requiring pane-selection arguments. Unresolved identity follows the existing skip/report rules without an interactive selection prompt. Preserve exact-exchange takeover proof, exclusions and pane protections. Amend the shared `pause-session` capture contract and the `resume-session` and `review-resume` authorization workflows before implementing this command, and carry those dependencies into design, plans and validation. A repeated author or role confirmation or pane-selection question in this automated path is a failure to meet the requirement, not expected pending takeover.

```text
resume_paused [--dry-run] [--clear] [--except NAME[,NAME...]] [--switch-roles NAME[,NAME...]]
```

Support at least Claude and Codex. The command must operate on existing
TUIOS sessions without depending on senv or its launcher. Windows Terminal
tab titles recorded by a launcher are optional supplementary information.
Q17=A's per-tab/session role-switch support is retained, with Q25's user
amendment making the saved handoff the source of target and assignment data;
no routing argument or runtime selection question is required. Under Q27=B,
optional `--switch-roles NAME[,NAME...]` swaps the saved requestor and reviewer
targets of a saved requestor pause with a recorded pair. Match names exactly
and case-insensitively against session names and checkout folder base names, like
`--except`. Both pane identities still come from the handoff and must be
validated; the human launch authorizes the swap without further confirmation.
An unmatched switch name prevents all input. A matched checkout that does not
hold a saved requestor pause with a recorded pair, such as a reviewer or
single-agent pause, receives no input and makes the invocation fail.
The tool must work from a shell outside
TUIOS, where `TUIOS_PANE_ID` is unset, as well as from a shell pane within it.

### Carrying launch authorization into receiving workflows

Under Q28=A, each bulk-delivered resume command carries an explicit marker
bound to the current prompt SHA-256, receiving pane id and agent host,
resolved intended role and, for reviewer activation, the exact exchange.
For the resumed agent's `resume-session`, the digest also fixes the exchange
saved in that prompt's routing, and a required role override covers only that
exchange. For reviewer activation, the digest names the checkout's pause
prompt that the requestor consumed, checked against its receipt.
Use the assignment resolved for this invocation, including Q27=B's optional
role switch. The receiving `resume-session` or `review-resume` workflow
validates the marker against its current prompt, pane, host, role and exchange
before treating it as the human launch's consent for required author and role
overrides. The receiving workflow establishes its own pane as pause capture
does. An inherited `TUIOS_PANE_ID` alone is not enough, because a command run
under the shared Codex app-server daemon can carry another session's pane
variables. Independent read-only evidence must agree, such as the marked
pane's agent log or screen showing this exact marked command as its latest
input, in the same checkout and agent host. When that evidence is unavailable
or disagrees, treat the marker as mismatched.

A match proceeds without another confirmation. A mismatch grants
no authorization: report it and stop without consuming the prompt or claiming
a role, rather than asking again. An ordinary manually typed command without
a marker retains its existing consent behavior. The saved handoff alone
grants no permissions, and the bulk tool writes no authorization artifact.
Carry marker parsing and matching into both shared resume workflows, design,
plans and validation before bulk-command implementation.

## Pane discovery and waiting-prompt rules for resume-paused

Read `tuios list-agents --all-sessions --json` for each pane's session,
name, id, `cwd`, state, `ready`, harness and program status. Treat the pane's
folder as its checkout. Compare pane folders and receipt project roots using
the filesystem's path rules, so Windows case and separator differences identify
the same checkout.

Identify Claude through harness `claude-code`. Identify Codex through a
`program_status` record whose app is `codex`; use the pane name only as a
fallback.

For every checkout, apply the `resume-session` state table to the prompt
and receipt in its artifact home: `.reviews`, or the location declared by
`.review-artifacts.ini`. Check the prompt bytes and SHA-256, the receipt,
and the receipt's project root. The session journal can index checkouts
and pause times, but cannot replace prompt and receipt validation.

Read the pausing agent from the prompt's first line:

```text
# <agent-id>: Resume session: <task title>
```

`claude` means Claude and `chatgpt` means Codex. Other pausing-agent ids,
including `gemini`, `copilot`, `grok`, other host names and `unknown`, are
reported as unrecognized until supported. The prompt's `Session role` can be
`implementation`, `requestor`, `reviewer`, `documentation` or `other`.

The pause time is the prompt's `Snapshot:` timestamp, including its offset.
The journal's pause entry indexes that pause; it does not replace the prompt's
timestamp. Undatable or unreadable evidence is addressed by Q07 and Q08.

Under Q07=A, unreadable or uncertain required evidence prevents input for
that checkout, reports an error and fails the invocation while independent
valid checkouts continue. A global discovery failure prevents all input.
Under Q08=A, use screen evidence only when attributable to the current pause;
ignore proven older evidence and send no input when its attribution is uncertain.

### Pause handoff routing required by Q25

Evolve [pause-session](../../instructions/pause-session.md) and its
[template](../../templates/pause-session.template.md) to save the information
needed for automatic target selection in `a.session-resume.local.md`:

- The resolved checkout, snapshot time, historical pause author and saved
  session role, with the pausing TUIOS session and pane identities.
- The intended resumed agent and, for a review pair, the intended requestor
  and reviewer: each target's agent host, intended role, TUIOS session identity,
  pane id and name, resolved checkout, observation time and identifying evidence.
- The source of each intended assignment, preserving the latest explicit
  user role-switch direction or otherwise the verified current assignment.
  Historical authorship alone does not imply an intended requestor role.
- The exact review exchange identity for paired restoration, or an explicit
  not-applicable value for single-agent continuation. Never save ownership
  capabilities or credentials in routing metadata.

The pause workflow gathers this information through read-only observation of
its own pane, existing role state and recorded user direction; it must not
contact a counterpart or launch the bulk resume command. It records unknown
values and their reasons when evidence is unavailable, without asking a routing
selection question or inventing assignments. The rest of the pause is preserved.

At resume, the saved handoff determines the intended target. Validate its
checkout, host, session and pane identities against live discovery before any
input. Names are supplementary labels; an LLM name alone cannot distinguish
multiple panes, and a saved id must not be trusted after reassignment or reuse.
Do not choose a first match or substitute a different idle pane. Missing,
stale, conflicting or non-unique routing causes no input to unresolved targets
and a report under Q06/Q07, without asking the person to choose a pane or
supply routing arguments. The same rule applies to legacy handoffs without
routing; do not ask an interactive migration question. The earlier Q06
one-candidate rule does not substitute a pane when the handoff cannot identify
it, even if live discovery shows only one candidate. A saved exact exchange
validated as live is the one identifiable exchange under Q21, even when other
exchanges are live; an absent or unresolved saved identity does not authorize
choosing one of them. This requirement does
not remove older handoffs' readability through ordinary `resume-session`.

Carry pause capture, saved-routing consumption, live identity validation and
the no-question legacy behavior into design, plans and validation before
implementing the bulk command. Instruction/template changes document the
capture contract; they do not establish that runtime consumption is implemented.

Under Q29=A, extend the existing pause replacement guard for an unused or
new-since-use prompt to a different recorded pausing pane or saved session
role, even when its agent host id matches. Name the existing checkpoint's
agent, pane and role and ask before replacing it under `interactive_menu.md`.
Declining preserves the old prompt and stops the new pause. Compare historical
pausing identities, not the intended future assignments or Q27 role swap.
Legacy prompts without pane or role fields retain the host-id comparison.
A pane or role recorded as unknown, for the existing checkpoint or the current
pause, is not by itself a difference; compare the remaining recorded fields.
This is a pause-time guard, with one latest checkpoint per checkout; it adds
no confirmation during bulk resume.

## Checkout-wide duplicate-resume protection for resume-paused

Send no resume command to any pane of a checkout already being resumed,
including when the resuming agent differs from the pausing agent. Treat
that difference as the person's deliberate override. Any one of these
signals is sufficient:

- A valid receipt matches the prompt bytes, regardless of its `Resumed by`
  or `Agent override` values: the state table's latest prompt is already used,
  rather than still waiting. Receipt-only reporting is addressed by Q08.
- The session journal has a resume entry for the checkout later than the
  pause time.
- After the pause time, a pane received `resume-session` or `review-resume`,
  evidenced by a Claude agent-log `prompt` line or the command on a Codex
  screen. Q14=A counts `resume-session` in any pane and also `review-resume`,
  except reviewer-role continuation when the saved pause was not a reviewer's.
  Q26=A identifies reviewer-only continuation by the selected role, including
  native command prefixes and trailing explanatory context. A stopped attempt or
  declined override still suppresses automatic repetition; it does not prove
  successful resumption or Q18 takeover.
- A pane is waiting on the resume-session agent-override question, before
  a receipt has been written.

The report identifies the resuming pane and agent, and the pausing agent,
as in the draft's example:

```text
SKIP api: already resuming in api/Codex api (chatgpt), paused by claude
```

Q01=D introduces a distinct reviewer activation after requestor resumption.
The original checkout-wide skip must still prevent a duplicate requestor
resume. Q19=A permits a reviewer-only continuation when fresh evidence
verifies the same pause, selected resumed requestor and role assignment,
and that the counterpart still needs activation. Never clear or resume the
requestor again. Reapply exclusions and input protections, leave an already
claimed or waiting reviewer alone, and diagnose uncertain prior delivery
instead of automatically resending under Q11. Q22=A applies the leave-alone
rule on every run and never clears the counterpart.

Under Q27=B, compare a later continuation against the assignment resolved by
that invocation, with or without `--switch-roles`. It must match the requestor
already resumed. A mismatch sends no input. When `--switch-roles` names that
checkout, the argument cannot apply and the invocation fails. Without the
argument, the checkout is the expected already-resuming skip, and its report
names the resumed requestor and says that continuing the switched pair needs
`--switch-roles`. A continuation of a switched assignment therefore repeats
the switch argument.

## Target selection and protected panes for resume-paused

Select the intended resumed agent and requestor/reviewer targets from the
saved pause handoff under the Q25 user amendment to Q17=A. This includes a
recorded role switch for one tab while other tabs retain their assignments.
Q27=B also permits a late swap through `--switch-roles` for a recorded pair;
this changes the intended roles without selecting different panes.
Validate the recorded pane identities against live discovery, including when
several panes run the same LLM. No launch-time pane selection or runtime question
is required. Under Q06=C as amended by Q25, skip unresolved routing and list
the reason and candidates; never guess or choose an alternate merely because
a recorded target is protected. Send `/resume-session` to
Claude or `$llm-shared:resume-session` to Codex.

The user confirmed Q01 Option D on 2026-11-07: after identifying and resuming
the requestor, look for an actual counterpart LLM in the same tab/session and
checkout, then ask it to resume as reviewer and claim that role if needed.
A CMD or other plain shell pane is not an LLM counterpart and receives no
review-resume instruction. Counterpart activation is not conditional on this
run having cleared its pane. Existing input protections still apply.

This includes a person-requested switch of LLM roles in a particular tab:
the LLM that was reviewer can become requestor, and the former requestor can
become reviewer. For example, a Claude requestor/Codex reviewer pair can
resume as Codex requestor/Claude reviewer. The pause author's identity remains
historical evidence; it does not by itself determine the person's new role
assignment. Q17 as amended by Q25 covers saved assignment and pane routing, Q18 covers the evidence
required before reviewer activation, and Q19 covers an incomplete reviewer
restart on a later invocation. Review ownership evidence and role isolation remain in effect. The human
invocation supplies the resume and role-override authorization described
in the command contract; no repeated confirmation is permitted. Under Q18=A, activate the reviewer only
after evidence proves that the selected LLM consumed the intended pause and
restored requestor ownership for the exact exchange. A receipt or `Working`
alone is insufficient. Unresolved role identity or takeover evidence leaves the reviewer untouched
and is reported without a follow-up confirmation question. Q21=A limits
activation to a saved requestor pause with one identifiable live exchange.
Q23=A waits a bounded time for takeover and reports a pending reviewer step
without failing the run.
Q24=B and the user's one-command clarification authorize the resolved resume and requestor/reviewer assignments from this invocation, including required author and role overrides, without further confirmation. Amend both shared resume authorization workflows before implementation and validate the absence of repeated confirmation prompts.

Report each skipped pane or checkout with its reason: an `--except` match,
`needs_input` or a question block, a turn in progress (skip immediately under Q02=A),
the caller's own pane,
an unrecognized or absent pausing agent, no matching agent pane, or an
already-resuming checkout. Also report unresolved, missing, stale, conflicting
or legacy saved routing: unresolved targets receive no input. Missing or unknown
routing is an expected skip under Q06/Q10; contradictory or unreadable required
identity evidence is a classification error under Q07. Match the comma-separated `--except` names
against session names, complete pane names (including spaces) and checkout
folder base names. Q09=A requires case-insensitive exact matching; session
and folder matches exclude their scopes, while pane names exclude only those
panes. Excluded and caller panes still supply duplicate-resume evidence.
Report unmatched names; any unmatched exclusion prevents all normal-run input.

Never type into a pane on `needs_input`, a pane blocked on a question, or a
pane holding draft input. This also applies if a resumed Codex pane begins
waiting on the person. Never clear or type into the caller's own pane,
identified by `TUIOS_PANE_ID` when present; report a caller-pane safeguard
skip. Under Q16=B the caller is a shell pane, or no pane when launched outside
TUIOS. The historical agent-caller report is not the current launch contract.

Q03=A allows fresh idle Codex screen evidence to override stale `working`
status, but never `blocked` status, a question or the person's draft. An empty
input line is `›` followed only by the placeholder `Ask Codex to do anything`,
with no `• Working` or question; verify that signature for the Codex version
in use. Ambiguous or unsupported screens do not permit input.

Q13=A requires a fresh eligibility check before every input action, including
clear, resume, reviewer activation and the Q11 recovery Enter. Recheck the
pause, duplicate-resume evidence and pane protections, including changes caused
by another run. Skip changed targets without input and report the reason.

## Optional conversation clearing for resume-paused

When `--clear` is supplied, clear the selected conversation before resuming:

- For Claude, enter `/clear`, press Enter, wait until the pane is quiet,
  and confirm `session started (clear)` in its agent log. Skip the clear
  when the log already records one after the pause time and no later `prompt`
  line follows it (Q12=A). Skip only that redundant clear; still resume.
- For Codex, use its new-conversation command, to be confirmed for the
  version in use (`/new` or `/clear`), and confirm the result on screen.

If a clear cannot be confirmed, stop processing that pane without sending
its resume command. Clearing must respect the protected-pane rules above.
Under Q04=A, report the pane's background-shell indicator when present and
leave those shells running; do not enumerate or stop them. Under Q22=A,
`--clear` never clears the counterpart.

## Delivery and command-acceptance evidence for resume-paused

Call `tuios` with argument lists, never through a shell. Use the selector
form proven in the draft, without clearing the caller's `TUIOS_*` variables:

```text
tuios ask-agent --select 'session:S name:N' --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>
```

TUIOS splits selector terms on spaces; quotes do not group pane names.
For a pane name containing a space, the draft uses `*` in its place, such
as `name:Claude*api`. Verify that the selector matches exactly one pane
before delivery. Under Q07=A, an uncertain selector prevents input for that
checkout, reports an error and fails the invocation.

Use one worker per selected pane and dispatch across panes concurrently.
Confirm that Claude took the command through the matching agent-log
`prompt` line. Confirm that Codex took it through the command on screen
followed by `• Working`. An `ask-agent` response of `ok` or state `idle`
alone is insufficient.

Readiness before typing (Q03) and submission after typing are distinct.
Q11=C permits one bounded Codex recovery for this run's proven unsubmitted
command, covering its new-conversation clear, `resume-session` and reviewer
instruction. Retain the pre-typing capture that passed Q03 as proof that the
input was empty. After the delivery call returns, require two captures showing
the unchanged exact command on the input line, no placeholder below it and no
`Working`. Neither absence alone establishes safe recovery.

Only when that evidence proves text ownership and non-submission, and a fresh
Q13 check permits input, send Enter once with `tuios send-keys -s S -w ID Enter`,
where `ID` is the full id of the pane that received the command. Never omit
`-w`, retype the command or repeat Enter. Recheck for the command followed by
`Working` and, for a clear, its required new-conversation result. If ownership,
submission or eligibility is uncertain, send no further input. If acceptance
remains unproved, report unconfirmed and fail the invocation. Record whether
the recovery Enter was used. Claude has no Enter recovery; uncertain acceptance
follows Q11's Option A without an automatic resend.

## Preview and result reporting for resume-paused

`--dry-run` types nothing and reports what a run would do, including the
intended command, any clear action, task title, pausing agent and pause time.
Q15=A requires one line per checkout holding a prompt, including already-used
prompts. Report each target's routing source as saved or unresolved, with its
validation result or reason. Name the selected requestor and counterpart and report their separate
outcomes, including no LLM counterpart, skips and unconfirmed actions. Never
report CMD as a reviewer. Omit checkouts without prompts and non-target panes;
end with the omitted-pane count. Use only known resumer identity and time,
or `unknown`, under Q08=A.

These single-agent examples apply the Q12=A redundant-clear decision;
review-pair lines additionally distinguish both outcomes.

```text
RESUME api/Claude api: /resume-session for 'Fix the parser', paused by claude at 2026-11-07 00:06
RESUME web/Codex web: clear, then $llm-shared:resume-session for 'Review step 4', paused by chatgpt at 2026-11-07 01:05
RESUME docs/Claude docs: already cleared at 00:42, /resume-session for 'Update the guide', paused by claude at 2026-11-07 00:30
```

A normal run uses the same Q15=A scope. Q10=A makes expected skips, including
the caller-pane safeguard, and an empty plan successful. Classification
errors, unmatched exclusions, unmatched `--switch-roles` names, matched
checkouts that the switch cannot apply to, and unconfirmed planned actions
fail. Dry runs fail on classification errors, unmatched exclusions and the
same two `--switch-roles` errors. Under Q23=A, a reviewer
step still waiting for Q18 takeover after the bounded wait is reported as
pending and does not fail the run. A target that stops on an author, role or
routing confirmation question fails the run, because the one-command contract
forbids that question.
A target that reports a Q28 marker mismatch also fails the run; for a
requestor, it is not a pending takeover under Q23=A. Design selects how long
a single-agent target is observed after acceptance for these stops, as Q23=A
does for takeover.

## Acceptance criteria for resume-paused

1. Discover Claude and Codex panes across sessions and resolve waiting
   prompts using the existing artifact-home and receipt state rules.
2. Suppress delivery throughout a checkout when any documented signal
   shows it is already resuming, even under an agent override.
3. Select from the saved handoff under the Q25 user amendment to Q17=A and
   Q06=C, including recorded per-tab role switches and distinct identities
   for several panes of the same LLM. Require no pane-selection argument or
   runtime question. Report exclusions, unsupported pausers, missing matching
   panes, protected panes and the caller-pane safeguard.
   Under Q27=B, support a late swap of a recorded requestor/reviewer pair
   through `--switch-roles`, validate both saved targets and require no further
   confirmation. Unmatched names prevent all input; a matched checkout that
   does not hold a saved requestor pause with a recorded pair receives no input
   and fails the invocation.
4. Never type into question-blocked panes or panes holding draft input.
5. With `--clear`, confirm the required clear before delivery; omit a
   redundant Claude clear already evidenced after the pause, with no later
   prompt (Q12=A), and still resume. Report background shells without stopping
   them under Q04=A.
6. Resolve exactly one pane per delivery selector, use shell-free argument
   lists, and process independent target panes concurrently.
7. Require Claude log evidence or Codex screen evidence that the command
   was taken, and reflect unconfirmed planned deliveries in the exit status.
   Permit only Q11=C's single targeted Enter for proven tool-owned unsubmitted
   Codex input, across clear, resume and reviewer commands; never retype or
   retry uncertain delivery. Report recovery use and apply Q10=A outcomes.
8. Make `--dry-run` read-only with respect to pane input and report the
   intended actions and skip reasons.
9. Read prompts, receipts, the journal and the exact exchange's role state
   without modifying them. The tool never claims ownership or performs fenced
   exchange operations. `resume-session` remains the writer of receipts and
   resume entries; receiving agents retain their normal review workflows.
10. Keep the tool Python 3.12 compatible and verify its behavior using a
    fake `tuios` runner, without requiring live TUIOS. The selected test
    scope is whole suite.
11. For Q01=D review-pair restoration, resume the selected requestor first;
    require Q18=A pause-consumption and exact-exchange ownership evidence
    before reviewer activation. One invocation authorizes the resolved resume,
    Q17=A assignments and required author/requestor/reviewer overrides under
    Q24=B and the user's one-command clarification, without further confirmation.
    Amend and validate both shared resume authorization workflows before
    implementation. Under Q28=A, carry a target-bound marker with the prompt
    digest, receiving pane and host, resolved role and exact reviewer exchange.
    The receiving workflow proves its pane with independent read-only evidence,
    not an inherited `TUIOS_PANE_ID` alone.
    Matching markers permit the authorized overrides without another question;
    mismatches stop without prompt consumption or role claim. Unmarked manual
    commands retain their existing consent behavior. Preserve pane protections
    and never deliver a reviewer
    instruction to CMD.
12. Under Q19=A, a later run can complete only a verified missing reviewer
    action, respecting exclusions and protections without clearing or resuming
    the requestor again. Leave an already active reviewer untouched and
    diagnose uncertain delivery rather than resending. Under Q27=B, require
    the invocation's resolved assignment, including any switch, to match the
    resumed requestor; otherwise send no input. The mismatch fails the invocation
    when `--switch-roles` names the checkout and is an expected skip otherwise.
13. Apply Q16=B and Q20=A's human-only launch contract, including refusal
    from recognized agent caller panes for normal and dry runs, with no input
    and a nonzero exit. Under Q26=A, classify reviewer-only continuation by
    its selected role, including native prefixes and trailing context; when
    the saved pause was not a reviewer's, that continuation does not suppress
    requestor resumption. Uncertain role evidence prevents input under Q07/Q08.
14. Amend the shared pause instruction and template to capture automatic
    routing for single-agent and paired pauses, preserving historical and
    intended roles separately. Validate saved-routing consumption before
    bulk-command implementation. Cover same-LLM panes, recorded role switches,
    missing or legacy metadata, stale or reused ids, and conflicting evidence.
    Unknown values do not prevent saving the rest of a pause; unresolved resume
    targets receive no input and a report, never a selection or migration
    question. Capture must not contact the counterpart or launch `resume_paused`.
    Extend the pause replacement guard under Q29=A to a different recorded
    pausing pane or saved role, at pause time only, with legacy prompts keeping
    the agent-id comparison.

## Deferred senv integration follow-up

Q05=A defers changing senv's `tuitp` launcher to reuse the shared tool for
launch-time resumption. The current delivery handles existing panes and
remains independent of senv. This unchecked follow-up is tracked work outside
the current delivery, with no assigned target version or calendar reminder.

- [ ] At the resume-paused completion handoff, carry this item into a separate
  senv effort once the shared command is implemented and validated. Revisit
  it when next changing senv's launch-time resume behavior.
- [ ] In that effort, assess replacing `bin/tuitp_resume.py`'s separate
  `waiting_prompt` check with the shared tool's supported interface, preserving
  the launcher's intended startup behavior and validating the integration.
- [ ] Keep a link to this checklist in the resume-paused design, implementation
  plan and completion handoff. Preserve this section during question
  consolidation; close the follow-up only with senv integration evidence.

## Existing integration references for resume-paused

- `pause-session` and `resume-session`: existing prompt, receipt and
  agent-override behavior described by the draft.
- `.review-artifacts.ini`: checkout-specific artifact-home declaration.
- `program_status.py`: existing Codex OSC 7501 app reports described by the
  draft.
- `bin/tuitp_resume.py`, `waiting_prompt`: senv's existing launch-time check,
  mentioned in the draft as a possible later integration.

## Open questions for the v0.14.0 resume-paused feature request

### Q01: Reviewer companion panes

When the paused session held a review role (`Session role` is `requestor` or `reviewer`), should this command also send a review-resume command to the counterpart agent's pane, such as `review-resume as reviewer` after a requestor pause? The draft lists conditional, unconditional and absent companion wake-ups. A counterpart that was not cleared keeps its context and may already be waiting for requests. Q16 separately addresses the calling agent's role-isolation obligations.

#### BBQ for Q01

At a barbecue, waking the cook need not also summon the independent food inspector. In this picture: the cook is the paused requestor, the inspector is the reviewer, and summoning is sending a resume command.

#### Options for Q01

- Option A: Resume only the pausing agent; leave counterpart activation to the person.
  - Pro: Preserves existing counterpart context and the person's control over restarting it.
  - Con: The person may need a separate reviewer-resume action.
- Option B: Also resume the counterpart only when this run cleared its pane.
  - Pro: Restores reviewer activity after a fresh conversation.
  - Con: Expands which panes are cleared; calling-agent role isolation still needs the decision in Q16.
- Option C: Always resume the counterpart.
  - Pro: Attempts to restore both roles automatically.
  - Con: Can disturb an existing counterpart or duplicate its watcher; Q16 still governs the calling agent.
- Option D: After identifying and resuming the requestor, find an actual LLM counterpart in the same tab/session and checkout. If present and eligible, send its native review-resume instruction asking it to resume as reviewer and claim that role if needed, because the requestor has just resumed. Support the person's selection of switched LLM roles for that tab; a CMD or other plain shell is not a counterpart.
  - Pro: Restores the review pair in the person's chosen roles, including when the former reviewer becomes requestor; handles tabs containing only one LLM and a shell.
  - Con: Needs explicit role selection, requestor-resumption evidence, ownership reconciliation and reporting of an incomplete reviewer restart; Q16 still governs agent-run authority.

#### Recommended option for Q01

Option A: The person decides when to restart the counterpart; an unsolicited review-resume can duplicate a live reviewer's watcher and adds another delivery beyond the one Q16 addresses.

#### Answer to Q01: option D

The user chose D: identify and resume the requestor first, then check for an
LLM counterpart and ask it to resume as reviewer, claiming the role if needed.
The instruction conveys: "review-resume as reviewer, claim the role if you
have to, since the requestor just resumed their session". Use the receiving
host's native invocation, such as `/review-resume` for Claude and
`$llm-shared:review-resume` for Codex. A plain CMD shell receives nothing.
The person must be able to switch the requestor and reviewer LLMs for one
tab. This is not limited to a counterpart cleared by the current run.

The original writer and reviewer recommendation was A; it is retained above
as history. Q17-Q19 cover the role-switch details that this decision exposes.

User decision: confirmed — Option D, with per-tab LLM role switching and an actual LLM counterpart only. Confirmed on 2026-11-07.

#### Clarification proposed for Q01 in Q24

Historical proposal, superseded by the user's Q24=B decision:

> Proposed clarification awaiting confirmation (Q24): the typed reviewer
> instruction supplies context and requests normal role pickup but grants no
> role-override consent. A conflict still presents Override or Stop and the
> reviewer step is reported as awaiting consent. The Q01=D decision is unchanged.

Q24=B confirmed and clarified on 2026-11-08: the human invocation authorizes the resolved resume and role assignments, including required author and requestor/reviewer overrides. The native instructions must carry this authorization without asking again. Explicit assignments and unambiguous defaults follow the same one-command contract; shared authorization-workflow amendments are required before implementation.

### Q02: Busy panes

The draft lists a turn in progress as a skip reason but also asks whether to wait up to ten minutes. Should an invocation skip such panes immediately or wait for them to settle?

With Q01=D, this also applies to a busy counterpart after the requestor has
resumed. The command must not interrupt a busy former requestor merely to
make it the new reviewer. Q19 separately covers a later retry of that step.

#### BBQ for Q02

At a barbecue, a cook already carrying a hot tray can be passed over or waited for. In this picture: the cook is the busy pane, the tray is its current turn, and waiting is delaying resume delivery.

#### Options for Q02

- Option A: Skip panes in a turn immediately.
  - Pro: Keeps the bulk command predictable and avoids interfering with active work.
  - Con: A later invocation may be needed.
- Option B: Wait up to ten minutes for each busy pane to become eligible.
  - Pro: Can resume a pane that soon becomes idle.
  - Con: Extends runtime and requires clear timeout reporting.

#### Recommended option for Q02

Option A: The command targets paused panes; immediate skips match the draft's stated skip rule.

#### Answer to Q02: option A

Option A is proposed because the command targets paused panes; immediate skips match the draft's stated skip rule.

User decision: confirmed — Option A: skip panes in an active turn immediately, including a selected requestor or reviewer counterpart. Confirmed on 2026-11-07. This keeps the bulk run predictable; a later invocation may be needed. Q19 separately determines reviewer-only continuation.

### Q03: Codex readiness with stale status

When Codex program status says working but its screen appears idle, which evidence decides whether it can receive input? The prohibition on question-blocked panes and draft input remains unconditional.

#### BBQ for Q03

At a barbecue, an old busy sign may disagree with an empty serving counter. In this picture: the sign is program status, the counter is the Codex screen, and serving is typing a resume command.

#### Options for Q03

- Option A: Decide readiness from the current screen: an empty `›` prompt line, no `• Working` and no question. A stale `working` record does not prevent input, but any `blocked` program-status record does, whatever the screen shows.
  - Pro: Supports the stale-status case observed in the draft.
  - Con: Ambiguous screens must still be skipped.
- Option B: Require both program status and screen to indicate readiness.
  - Pro: Avoids overriding a conflicting status report.
  - Con: A stale working report can prevent resumption indefinitely.

#### Recommended option for Q03

Option A: The observed stale reports make status alone insufficient; require unambiguous current screen evidence before input.

#### Answer to Q03: option A

Option A is proposed because the observed stale reports make status alone insufficient; require unambiguous current screen evidence before input.

User decision: confirmed — Option A. Confirmed on 2026-11-07. The user selected A after distinguishing readiness before typing from the separately reported typed-but-unsubmitted delivery case. Questions, draft input and blocked status still prevent input; Q11 and follow-up review address submission recovery.

Readiness wording clarification from round 3: the empty Codex input line
contains only the prompt marker and its Ask Codex to do anything placeholder,
with no Working or question. Verify the signature for the installed version;
an ambiguous screen never passes readiness. Q11 separately governs submission.

### Q04: Background shells after a clear

Should `--clear` report surviving background shells, and should it ever stop them? The draft identifies duplicate watchers but does not settle the expected action.

#### BBQ for Q04

At a barbecue, clearing a table does not extinguish a grill left burning. In this picture: the table is the conversation, the grill is a surviving shell, and the warning is the shell report.

#### Options for Q04

- Option A: Report the pane's own background-shell indicator, such as Claude's `N shells` status line, as a warning and leave shells running. When no indicator is shown, report nothing.
  - Pro: Makes the duplicate-watcher risk visible without terminating work.
  - Con: The person must resolve old shells separately.
- Option B: Leave shell reporting outside this feature.
  - Pro: Keeps the output and scope smaller.
  - Con: The known duplicate-watcher risk remains less visible.
- Option C: Stop surviving shells automatically.
  - Pro: Can prevent a resumed agent from duplicating an old watcher.
  - Con: May terminate unrelated work and adds a new destructive responsibility.

#### Recommended option for Q04

Option A: Showing the shell count exposes the duplicate-watcher risk of a clear, while ending a shell remains the person's call.

#### Answer to Q04: option A

Option A is proposed because showing the shell count exposes the duplicate-watcher risk, while ending a shell remains the person's call.

User decision: confirmed — Option A. Confirmed on 2026-11-07. Report the pane's own background-shell indicator as a warning and leave shells running. When no indicator is shown, report nothing.

### Q05: senv integration scope

Does v0.14.0 require senv's `tuitp` to delegate its launch-time waiting-prompt check to this new tool, or is that later work? The draft requires the shared tool to work without senv.

#### BBQ for Q05

At a barbecue, a new serving station can open before the old trolley is rerouted through it. In this picture: the station is this tool, the trolley is tuitp, and rerouting is launcher integration.

#### Options for Q05

- Option A: Ship the standalone existing-pane command; defer tuitp integration.
  - Pro: Keeps acceptance focused on the requested shared tool.
  - Con: Two waiting-prompt checks may remain until later integration.
- Option B: Require tuitp integration in this delivery too.
  - Pro: Can align launch-time and existing-pane behavior sooner.
  - Con: Adds changes and validation in another project.

#### Recommended option for Q05

Option A: The draft describes tuitp reuse as a possible later change and explicitly removes a dependency on it.

#### Answer to Q05: option A

Option A is proposed because the draft describes tuitp reuse as a possible later change and explicitly removes a dependency on it.

User decision: confirmed — Option A, with an explicit tracked reminder for deferred senv integration. Confirmed on 2026-11-07. The user asked how Option B would be remembered; the draft and the requirement's Deferred senv integration follow-up section now retain an unchecked item, a completion-handoff trigger and instructions to carry its link into later effort documents. No integration date or target version is selected.

### Q06: Choosing among several panes of the pausing agent

When a checkout has several panes of the agent that paused it, which pane receives the command, and what happens when that pane is excluded, busy, question-blocked, holds draft input or is the caller's own pane? For Options A and B, "first" means first in `tuios list-agents --all-sessions --json` order. The first matching pane may hold an unrelated conversation that `--clear` would erase.

The pausing agent is the original default. Q17 must also establish the selected
requestor and counterpart under a per-tab role switch; these ambiguity and
protection concerns apply to both selected roles.

#### BBQ for Q06

At a barbecue, the first serving counter may be closed while another is open. In this picture: the counters are matching agent panes, closure is a protection or exclusion, and choosing another is fallback delivery.

#### Options for Q06

- Option A: Choose the first eligible matching pane; skip the checkout if none qualifies.
  - Pro: Can resume safely through another available pane.
  - Con: The destination can differ from the first discovered pane. When the caller's pane matches first, the report would both direct the person there and resume the checkout elsewhere.
- Option B: Choose the first matching pane and skip the checkout if it is protected.
  - Pro: Follows the draft's literal first-pane wording.
  - Con: An eligible later pane is unused. The first pane may hold another conversation, which `--clear` would clear.
- Option C: Resume only when the checkout has exactly one pane of the pausing agent; with several, skip the checkout as ambiguous and list the candidate panes.
  - Pro: Avoids resuming or clearing an unrelated conversation when the target is uncertain.
  - Con: A checkout with two panes of the same agent needs a manual resume.

#### Recommended option for Q06

Option C: An ambiguous target is uncertain evidence, so no input should be sent; the usual one-pane-per-agent layout is unaffected.

#### Answer to Q06: option C

Option C is proposed because an ambiguous target should receive no input, while the usual one-pane-per-agent layout remains unaffected.

User decision: confirmed — Option C. Confirmed on 2026-11-07. Resume only when the checkout has exactly one pane of the pausing agent; with several matching panes, skip the checkout as ambiguous and list the candidates. Q17 separately determines explicit per-tab role and target assignments for a role switch.

User amendment on 2026-11-08 (Q25): the handoff must record enough pane and
role identity to resolve targets automatically, including among several panes
of one LLM. The original one-candidate rule no longer forces a skip when saved
routing uniquely identifies and live evidence validates the intended pane.
Retain the no-guessing skip/report rule for unresolved identities, without a
selection question or required pane-selection argument.

Consequence of the Q25 decision, recorded on 2026-11-08: when the handoff
cannot identify a target, including a legacy prompt without routing, a single
live candidate does not replace the missing saved identity. That target gets
no input and an expected skip; the person can still resume it with ordinary
`resume-session`.

### Q07: Unreadable or uncertain checkout state

What should happen when the prompt, receipt, journal or required pane evidence cannot be read or validated, so neither waiting nor already-resuming state can be established, or when a delivery selector matches zero or several panes? If `list-agents` fails, no checkout can be classified and no input can be sent.

#### BBQ for Q07

At a barbecue, an unreadable reservation should not send a meal to a guessed table. In this picture: the reservation is resume evidence, the table is a checkout, and sending the meal is delivering input.

#### Options for Q07

- Option A: Do not type for that checkout, report an error, continue independent checkouts, and exit non-zero.
  - Pro: Avoids duplicate or misdirected resumes while retaining useful progress.
  - Con: One uncertain checkout makes the overall run unsuccessful.
- Option B: Abort the entire invocation on the first uncertainty.
  - Pro: Makes failure immediate and unambiguous.
  - Con: An unrelated damaged checkout blocks all remaining work.
- Option C: Ignore unavailable evidence and proceed using what remains.
  - Pro: Resumes more panes despite partial observations.
  - Con: Can miss an existing resumer or stale receipt.

#### Recommended option for Q07

Option A: Uncertain resume ownership must prevent input locally without blocking unrelated valid targets.

#### Answer to Q07: option A

Option A is proposed because uncertain resume ownership must prevent input locally without blocking unrelated valid targets.

User decision: confirmed — Option A. Confirmed on 2026-11-07. Do not type for the checkout with unreadable or uncertain required evidence; report an error, continue independent valid checkouts, and exit non-zero. If global pane discovery fails, no checkout can be classified and no input can be sent.

### Q08: Resume evidence belongs to the current pause

How should an old or undated Codex resume command on screen be treated when the rule requires evidence after the current pause? A journal resume entry can establish checkout activity without naming a pane, although the requested report names one.

#### BBQ for Q08

At a barbecue, yesterday's collection slip should not prove today's order was collected. In this picture: the slip is a resume command on screen, today's order is the current pause, and collection is an active resumption.

#### Options for Q08

- Option A: Count screen evidence only when attributable to the current pause. Ignore evidence shown to predate it, such as an earlier resume followed by the current pause. When attribution cannot be established, report uncertainty and do not type. Without a resuming pane, report what is known: the receipt's `Resumed by` and `Used at`, or `unknown`. A receipt-only example is `SKIP api: already resumed by chatgpt at 2026-11-07 08:12 (receipt), paused by claude`.
  - Pro: Prevents stale screen text and invented identity from deciding behavior.
  - Con: Some panes need human inspection.
- Option B: Treat any visible resume command as sufficient to skip the checkout.
  - Pro: Conservatively avoids sending duplicate commands.
  - Con: Old scrollback can suppress a genuinely waiting pause.

#### Recommended option for Q08

Option A: The draft explicitly requires post-pause evidence; unavailable identity should remain unknown rather than fabricated.

#### Answer to Q08: option A

Option A is proposed because the draft explicitly requires post-pause evidence; unavailable identity should remain unknown rather than fabricated.

User decision: confirmed — Option A. Count screen evidence only when attributable to the current pause; ignore evidence demonstrated to predate it. If attribution is uncertain, report uncertainty and send no input. Report only known resumer identity and time from the available evidence, or `unknown`; do not invent a pane identity.

Decision date: 2026-11-08. The user selected A. This keeps old terminal history from suppressing a genuinely waiting pause while preserving duplicate-resume protection when current-pause attribution is uncertain.

### Q09: Exclusion matching

Are `--except` values exact names or patterns, is matching case-sensitive, and does matching one pane exclude its entire checkout?

#### BBQ for Q09

At a barbecue, a do-not-serve label can identify one seat or the whole table. In this picture: the label is an exclusion value, the seat is a pane, and the table is its checkout.

#### Options for Q09

- Option A: Use case-insensitive exact names; session and folder matches exclude their scope, while pane-name matches exclude only that pane. Compare complete pane names including spaces, and use the checkout folder's base name. Exclusion stops clearing and typing only; excluded panes and the caller's own pane still provide already-resuming evidence. Report unmatched values; if any value matches nothing, a normal run types nothing.
  - Pro: Predictable Windows-friendly names and narrow pane exclusions.
  - Con: Does not support abbreviated names or wildcards.
- Option B: Use case-insensitive wildcard patterns with the same scope rules.
  - Pro: Convenient for excluding families of names.
  - Con: Pattern characters may exclude more panes than intended.
- Option C: Treat any matching name as excluding the whole checkout.
  - Pro: Gives one broad exclusion rule.
  - Con: A pane exclusion also suppresses other panes in its checkout.

#### Recommended option for Q09

Option A: Exact names avoid the selector wildcard ambiguity, and each match should affect the object the person named.

#### Answer to Q09: option A

Option A is proposed because exact names avoid the selector wildcard ambiguity, and each match should affect the object the person named.

User decision: confirmed — Option A. Match complete names case-insensitively and exactly, using the checkout folder's base name. Session and folder matches exclude their scope; pane-name matches exclude only that pane. Exclusions prevent clearing and typing, while excluded panes and the caller's own pane still supply already-resuming evidence. Report unmatched values; if any value matches nothing, a normal run sends no input anywhere.

Decision date: 2026-11-08. The user selected A. Exact scoped matching makes exclusions predictable and detects mistyped names before delivery.

### Q10: Skip and preview exit status

Does a deliberately skipped pane make the run fail, and what exit status should a dry run return when some checkouts cannot be classified? The draft defines success only for planned deliveries.

#### BBQ for Q10

At a barbecue, a declined meal differs from an order that could not be delivered. In this picture: the declined meal is an intentional skip, the failed order is an unconfirmed planned resume, and the tally is the exit status.

#### Options for Q10

- Option A: Expected skips, including the caller's-pane skip, and an empty plan succeed; classification errors, unmatched exclusions under Q09, or unconfirmed planned actions fail. Dry runs fail on classification errors or unmatched exclusions.
  - Pro: Separates exclusions from failures and makes previews useful in automation.
  - Con: Callers must inspect result lines to distinguish an empty run.
- Option B: Return non-zero whenever any discovered pane is skipped.
  - Pro: Draws attention to every pane left untouched.
  - Con: Routine exclusions and the caller's pane make success difficult.

#### Recommended option for Q10

Option A: The draft's every-planned-pane wording excludes deliberate skips from delivery failure, while diagnostic errors still need an unsuccessful result.

#### Answer to Q10: option A

Option A is proposed because the draft's every-planned-pane wording excludes deliberate skips from delivery failure, while diagnostic errors still need an unsuccessful result.

User decision: confirmed — Option A. Expected skips, including the caller's-pane skip, and an empty plan succeed. Classification errors, unmatched exclusions under Q09, or unconfirmed planned actions fail. Dry runs fail on classification errors or unmatched exclusions.

Decision date: 2026-11-08. The user selected A. Deliberate skips fulfill the protection rules; errors and unconfirmed required actions remain failures.

### Q11: Unconfirmed command acceptance

If delivery times out or acceptance evidence cannot be confirmed, should the tool resend the resume command automatically? A command may have been taken even when its confirmation was missed.

The user's 2026-11-07 comment and the reviewer's queued follow-up finding
identify a distinct case: the tool's command is visibly typed but not yet
submitted. The proposed recovery is one Enter followed by a fresh check
for `Working`, rather than retyping the command. The Q11 discussion and
follow-up review must reconcile that proposal with the options below and
the unconditional protection of the person's draft input. Neither absence
of `Working` alone nor an `ok` delivery result proves that Enter is safe.

#### BBQ for Q11

At a barbecue, losing a collection receipt does not prove the customer needs a second meal. In this picture: the meal is a resume command, the receipt is acceptance evidence, and a second meal is a resend.

#### Options for Q11

- Option A: Report the pane as unconfirmed, exit non-zero, and do not resend automatically.
  - Pro: Avoids duplicate prompts or input into an agent that has started working.
  - Con: The person may need to inspect the pane before retrying.
- Option B: Retry delivery automatically after the timeout.
  - Pro: May recover from a command that was never received.
  - Con: May send duplicate input or answer a new question accidentally.
- Option C: Keep Option A for uncertain acceptance, with one bounded Codex submission recovery. If fresh screen evidence establishes that this run's exact command remains unsubmitted in the input box, the input was empty before this run typed it, and a fresh protection check permits input, press Enter once and check again for the command followed by `Working`. The reported signature is the command on the input line with no `Ask Codex to do anything` line below it and no `Working`; neither absence alone proves recovery safe. Never retype the command or repeat Enter. If ownership of the text, submission state, or eligibility is uncertain, send no further input. Report unconfirmed and exit non-zero if acceptance is still unproved.
  - Pro: Covers the observed typed-but-unsubmitted case without retrying uncertain delivery or submitting the person's draft.
  - Con: Requires positive evidence of tool-owned unsubmitted input and a fresh protection check; unsupported or ambiguous screens still need inspection.

#### Recommended option for Q11

Option A: Once delivery is uncertain, a second input cannot be assumed safe.

Discussion recommendation on 2026-11-08: Option C incorporates the user's relayed finding and the reviewer's queued finding while retaining Option A for uncertain delivery. The original recommendation above is preserved. The subsequent user decision is recorded below; independent review remains required.

#### Answer to Q11: option C

Historical proposal: Option A was proposed because once delivery is uncertain, a second input cannot be assumed safe.

User decision: confirmed — Option C. Retain Option A for uncertain acceptance. Permit one Enter only when fresh evidence establishes that this run's exact Codex command remains unsubmitted, the input was empty before this run typed it, and fresh protection checks permit input. Never retype the command or repeat Enter. Protect the person's draft and send no further input if text ownership, submission state or eligibility is uncertain. Check again for the command followed by `Working`; if acceptance remains unproved, report unconfirmed and exit non-zero.

Decision date: 2026-11-08. The user selected C in the native picker. This covers the observed typed-but-unsubmitted case without retrying uncertain delivery. The absence of `Working` or the input placeholder alone does not establish safe recovery.

### Q12: Already-cleared preview wording

The draft's dry-run example labels an already-cleared pane as SKIP, while the clear rule says to skip only the redundant clear. Should an otherwise eligible pane still be resumed?

#### BBQ for Q12

At a barbecue, a clean plate need not be washed again before serving dinner. In this picture: the plate is the conversation, washing is clearing, and serving dinner is resuming.

#### Options for Q12

- Option A: Skip only the clear, still resume, and report RESUME with an already-cleared note. A logged clear counts only when no `prompt` line follows it.
  - Pro: Matches the clear rule and avoids leaving a waiting prompt untouched.
  - Con: Requires correcting the draft's SKIP example.
- Option B: Skip the entire pane when a post-pause clear already exists.
  - Pro: Preserves the example's literal SKIP label.
  - Con: A manual clear can prevent the requested resumption.

#### Recommended option for Q12

Option A: An already-performed preparatory action should not suppress the requested resume.

#### Answer to Q12: option A

Option A is proposed because an already-performed preparatory action should not suppress the requested resume.

User decision: confirmed — Option A. Skip only the redundant clear, still resume an otherwise eligible pane, and report `RESUME` with an already-cleared note. A logged clear after the current pause counts only when no later `prompt` line follows it.

Decision date: 2026-11-08. The user selected A. Clearing prepares the conversation; it must not suppress the requested resumption of the saved pause.

### Q13: Eligibility changes before input

What should happen when a prompt is replaced, another pane starts resuming, or a selected pane becomes blocked or holds draft input after discovery but before clearing or delivery, including changes caused by a concurrent `resume_paused` run?

#### BBQ for Q13

At a barbecue, an order can be cancelled while the server walks to the table. In this picture: the order is a planned resume, the walk is the interval after discovery, and cancellation is changed eligibility.

#### Options for Q13

- Option A: Recheck before each input action; skip changed targets without typing and report why.
  - Pro: Extends the draft's no-input rules to changes during a run.
  - Con: A preview or earlier plan can differ from the final actions.
- Option B: Treat the initial plan as authoritative throughout the run.
  - Pro: Keeps execution aligned with its starting plan.
  - Con: Can violate the protected-pane and already-resuming rules after state changes.

#### Recommended option for Q13

Option A: The unconditional protection rules must still apply at the moment input would be sent.

#### Answer to Q13: option A

Option A is proposed because the unconditional protection rules must still apply at the moment input would be sent.

User decision: confirmed — Option A. Recheck before each input action; skip changed targets without typing and report why. This includes a replaced pause prompt, another pane starting resumption, or changed busy, question-blocked or draft-input state, including changes caused by a concurrent run.

Decision date: 2026-11-08. The user selected A in the native picker. The final actions may differ from the initial plan or preview because input protections apply when input would be sent.

### Q14: Commands that count as already resuming

The duplicate-resume rule counts any post-pause `resume-session` or `review-resume` in any pane of the checkout. A reviewer restarted with `review-resume as reviewer` does not consume a requestor's pause prompt, and a resume that stopped on a blocker or a declined agent override leaves the prompt waiting. Which post-pause commands suppress delivery?

#### BBQ for Q14

At a barbecue, the inspector arriving does not mean the cook's order was picked up. In this picture: the inspector is a restarted reviewer, the cook's order is the paused requestor's prompt, and picking it up is resuming it.

#### Options for Q14

- Option A: Count `resume-session` in any pane. Count `review-resume` too, except `review-resume as reviewer` when the paused session's role is not `reviewer`. A counted command still counts when its resume then stopped or its override was declined.
  - Pro: Restarting a reviewer no longer hides a paused requestor, and an actual resume attempt blocks a duplicate.
  - Con: Command arguments must be established from the log or screen; a stopped attempt needs a manual resume.
- Option B: Count every `resume-session` and `review-resume`, as the draft lists.
  - Pro: Simple and conservative about repeated commands.
  - Con: Restarting the reviewer prevents resumption of the paused requestor.
- Option C: Count only `resume-session`.
  - Pro: Only the command that consumes the prompt counts.
  - Con: A requestor resumed directly through `review-resume` can receive a duplicate command.

#### Recommended option for Q14

Option A: It keeps protection against duplicate resumes without treating a reviewer restart as a resume of the paused session.

#### Answer to Q14: option A

Option A is proposed because it keeps protection against duplicate resumes without treating a reviewer restart as a resume of the paused session.

User decision: confirmed — Option A. Count `resume-session` in any pane. Count `review-resume` too, except `review-resume as reviewer` when the saved pause's role is not `reviewer`. A counted command still suppresses another automatic resume if its attempt stopped on a blocker or its author override was declined; this does not prove completed resumption.

Decision date: 2026-11-08. The user selected A. Reviewer-only activation must not hide a waiting requestor pause, while counted attempts prevent automatic repetition, including after a declined override.

#### Clarification proposed for Q14 in Q26

Confirmed clarification on 2026-11-08 (Q26=A): identify reviewer-role
`review-resume` by its selected role, including native command prefixes and
trailing explanatory context, rather than requiring the exact short quoted
command. When the saved pause was not a reviewer's, that continuation does
not suppress requestor resumption. Uncertain role evidence prevents input
under Q07/Q08. The Q14=A role distinction is preserved.

### Q15: Panes and checkouts that get a report line

Discovery reads every pane of every session, and both preview and run promise one line per pane, but the listed reasons cover only checkouts holding a prompt. Should the report also list panes whose checkout has no prompt, non-target panes beside the target, and checkouts whose prompt was already used?

Q01=D adds a possible second action in the same checkout. Whichever grouping
is chosen must identify the selected requestor and counterpart and distinguish
requestor resumption from reviewer activation, including no LLM counterpart
and a skipped or unconfirmed reviewer. A plain CMD pane is never reported as
a resumed reviewer. Q19 covers recovery when only the reviewer action remains.

#### BBQ for Q15

At a barbecue, the host's list can name every guest or only those still waiting for food. In this picture: guests are panes, waiting for food is a waiting prompt, and the list is the report.

#### Options for Q15

- Option A: Report one line per checkout holding a prompt: RESUME naming its target pane, or SKIP with the checkout or pane reason, including an already-used prompt. Omit checkouts without a prompt and non-target panes, and end with a line counting omitted panes.
  - Pro: Output grows with paused work and matches the mixed pane and checkout examples.
  - Con: An omitted pane is explained only by the closing count.
- Option B: Report every discovered Claude or Codex pane, including no-waiting-prompt skips and non-target panes.
  - Pro: Every supported pane is accounted for.
  - Con: Across many sessions the output is mostly lines needing no action.

#### Recommended option for Q15

Option A: The report shows what needs or received action; panes with nothing waiting add length without a decision.

#### Answer to Q15: option A

Option A is proposed because the report shows what needs or received action; panes with nothing waiting add length without a decision.

User decision: confirmed — Option A. Report one line per checkout holding a prompt, including already-used prompts: RESUME names its target pane; SKIP gives the checkout or pane reason. Omit checkouts without prompts and non-target panes, then give the omitted-pane count. Within each reported checkout, distinguish the selected requestor and counterpart and their separate outcomes, including no LLM counterpart and a skipped or unconfirmed reviewer. Never report a CMD pane as a resumed reviewer.

Decision date: 2026-11-08. The report stays focused on paused work while preserving Q01=D's separate requestor and reviewer outcomes; Q19 separately addresses a later reviewer-only continuation.

### Q16: Running the command from an agent pane

The draft's proven run was made by an agent from its own pane, and the caller-pane rule presumes an agent caller. Review-role isolation forbids a requestor from starting or messaging a reviewer session, and a reviewer from starting or messaging a requestor session. When an agent runs `resume_paused` and it types a resume command into another agent's pane, whose action is that? The current prohibition remains in effect until an exception is explicitly decided and implemented.

The confirmed Q01=D requires a future reviewer-resume delivery after the
requestor resumes, including a claim when the selected LLMs switch roles.
This question must cover that explicit user-directed action as well; Q01 does
not by itself amend the current shared isolation or ownership instructions.

#### BBQ for Q16

At a barbecue, a cook asked by the host to ring the dinner bell passes on the host's call. In this picture: the host is the person, the cook is the calling agent, and the bell is the typed resume command.

#### Options for Q16

- Option A: Let the command act for the person: an agent runs it only at the person's explicit request in its current conversation, never on its own initiative or as a step of a review or resume workflow. The shared role-isolation text gains that exception, in this delivery unless the person defers it.
  - Pro: Preserves the proven agent-run usage and makes its authority explicit.
  - Con: Requires a separately confirmed change to the shared role-isolation instruction.
- Option B: Only a person runs it from a terminal or shell pane; an agent never does.
  - Pro: Requires no role-isolation exception.
  - Con: Excludes the draft's agent-run scenario and reduces the purpose of caller-pane protection.
- Option C: An agent may run it, but checkouts paused in a review role are skipped when the caller is an agent pane.
  - Pro: Avoids delivery to paused review roles from an agent pane.
  - Con: Skips review checkouts the person wants resumed; the caller's role is not reliably known.

#### Recommended option for Q16

Option A: The typed command relays the person's own explicit request, which the isolation policy can name as an exception without letting either review role start the other; until that exception exists, the current prohibition applies.

#### Answer to Q16: option B

Option A is proposed because the typed command relays the person's own explicit request, which the isolation policy can name as an exception without letting either review role start the other; until that exception exists, the current prohibition applies.

User decision: confirmed — Option B. Only the person runs resume_paused from a terminal or shell pane; an agent never launches it, including when the person asks the agent to do so. No exception to shared review-role isolation is introduced by this effort. Q01=D's requestor-then-reviewer delivery, including a per-tab LLM role switch, is performed by the person-launched command.

Decision date: 2026-11-08. This excludes the draft's demonstrated agent-run invocation and retains the existing review-role isolation boundary. The original Option A recommendation is preserved above; existing caller-pane protection remains recorded for consistency review, without authorizing an agent launch.

### Q17: Selecting requestor and reviewer LLMs per tab

Q01=D confirms that one tab can resume with its LLM roles switched. The saved prompt still names the agent that paused it, while the person may now want the other LLM as requestor. How does the person select the new requestor for each tab, and how is its reviewer counterpart identified? A tab can contain one LLM plus CMD, two LLMs, or several possible LLM targets. Do not infer a switch from pane order or from which agent runs the command.

#### BBQ for Q17

At a barbecue, the host can reassign cook and inspector for one table without changing the other tables. In this picture: the table is a tab/checkout, the cook is requestor, the inspector is reviewer, and CMD is a spare chair rather than another worker.

#### Options for Q17

- Option A: Accept an explicit role assignment for each selected tab/session, naming its intended requestor LLM and, when needed, its reviewer pane. Without an assignment, retain the known requestor assignment, using the pause author only when the pause actually belonged to the requestor. A unique other supported LLM can be the counterpart; absent or ambiguous requestor evidence or several possible counterparts require selection rather than guessing. Plain shells never qualify.
  - Pro: Supports a switch in one tab while leaving other tabs' assignments unchanged, including a former requestor becoming reviewer.
  - Con: The person must identify the affected tab and resolve ambiguous role targets; command syntax remains a design detail.
- Option B: Ask for the requestor and reviewer assignment interactively for every relevant tab on every run, including dry runs.
  - Pro: Makes each tab's intended roles explicit without a stored default.
  - Con: Adds repeated interaction to a bulk command and to previews.
- Option C: Have the person establish the switched requestor and reviewer roles manually in their panes first; the bulk command only follows those established assignments.
  - Pro: Keeps role selection and ownership changes in the existing resume workflows.
  - Con: Requires visiting the tab before bulk resumption and reduces the requested switch convenience.

#### Recommended option for Q17

Option A: An explicit per-tab assignment expresses the person's intended switch without reassigning unrelated tabs or interpreting a CMD pane as a reviewer. Existing agent-override consent and ownership gates still apply; selecting a target is not evidence that the new requestor has resumed.

#### Answer to Q17: option A

Option A is proposed so the person can choose Codex as requestor and Claude as reviewer for one tab even when Claude authored its pause, while keeping other tabs unchanged. Q18 determines when the reviewer may be activated.

User decision: confirmed — Option A, with the explicit Q25 handoff-driven selection amendment on 2026-11-08. Support recorded role assignments per tab/session, including requestor/reviewer switches. The pause handoff must supply the intended resumed agent and requestor/reviewer pane identities and assignment evidence; the bulk command validates them against live panes. Do not require selection arguments or ask a routing question. Missing, stale or ambiguous routing is reported without input to unresolved targets. Never guess; plain shells never qualify. At pause, retain a verified current assignment absent explicit user direction; the historical author implies a requestor only when the saved role was requestor.

Decision date: 2026-11-08. This permits switching one tab's requestor/reviewer LLMs without changing unrelated tabs. The later Q25 user amendment supersedes the earlier requirement to identify panes in launch arguments: evolve pause capture so selection is automatic from the saved handoff. Q16=B requires a human shell launch. The user's one-command clarification supplies authorization for the resolved resume and roles without repeated confirmation; ownership evidence remains required. Saved destinations do not prove successful resumption; Q18 remains separate.

#### Clarification proposed for Q17 in Q25

Historical proposal, superseded by the explicit Q25 user amendment:

> Permit a requestor-pane assignment when several panes share one LLM; derive
> a default only from the exact exchange or a requestor-authored pause.

Confirmed Q25 clarification: save intended assignments and observed pane
identities in the pause handoff, with their evidence, then resolve targets
automatically by validating that routing against live state. Evolve the pause
instruction and template accordingly. No selection argument or question is
required; unresolved targets receive no input and a report.

### Q18: Evidence that the selected requestor has resumed

Q01=D orders reviewer activation after the requestor has resumed. Sending a command and seeing the agent start working proves acceptance, but the new LLM may then wait on the pause-author override question or on a review-role conflict. In a switched tab, what evidence is enough to proceed to the reviewer? The current resume-session instruction requires explicit author-override consent after its notice, and review-resume requires an explicit Override for a role conflict; this requirement must not silently treat delivery as that consent.

#### BBQ for Q18

At a barbecue, hearing the new cook acknowledge a call does not prove they have taken over the kitchen. In this picture: acknowledgment is command acceptance, taking over is restored requestor ownership, and calling the inspector is activating the reviewer.

#### Options for Q18

- Option A: Require evidence that the selected LLM consumed the intended pause and restored the requestor role for the exact review exchange before activating its counterpart. If it awaits override consent, role selection or other reconciliation, leave the reviewer untouched and report the pending step. For a concrete exchange, ownership must agree with the selected requestor; a receipt or a Working screen alone is insufficient. Existing consent gates remain in effect.
  - Pro: Preserves the user's requestor-first order and avoids waking a reviewer while the intended requestor has not taken over.
  - Con: Needs stronger evidence than command acceptance and can leave the reviewer step pending while the person answers a question.
- Option B: Activate the counterpart as soon as the selected requestor accepts its resume command, leaving its subsequent consent and ownership reconciliation to finish independently.
  - Pro: Restores the two panes sooner and reuses existing acceptance evidence.
  - Con: The reviewer can claim or start work before the selected requestor actually resumes, including when an override is later declined.

#### Recommended option for Q18

Option A: The user's wording requires an actually resumed requestor. Command acceptance does not establish that an agent switch or requestor-role claim succeeded.

#### Answer to Q18: option A

Historical proposal before Q24=B: Option A is proposed to distinguish accepting a resume command from successfully resuming in the selected role. Any future change that preauthorizes an override would require explicit requirements and matching instruction changes; none is decided here.

User decision: confirmed — Option A, with the explicit Q24=B and one-command authorization amendment on 2026-11-08. Before activating the counterpart, require evidence that the selected LLM consumed the intended pause and restored requestor ownership for the exact review exchange. Neither a receipt nor a Working screen alone suffices. The human invocation is sufficient authorization for its resolved pause target and requestor/reviewer assignments, including necessary author and recorded-role overrides. Do not stop for another confirmation of these operations. Unresolved identity or missing takeover evidence leaves the reviewer untouched and is reported under existing rules; it does not authorize guessing.

Decision date: 2026-11-08. This preserves Q01=D's requestor-first order, including Q17=A's per-tab role switch, while distinguishing command acceptance from successful resumption and role takeover. The original restrictions on advance author and role-override consent are expressly superseded by Q24=B and the user's one-command clarification on 2026-11-08. The invocation authorizes its resolved pause target and roles without additional confirmation; matching shared-workflow amendments are required before implementation. Q19 separately decides later completion of a pending reviewer action.

### Q19: Completing a reviewer restart after partial resumption

The requestor may resume successfully while its counterpart is busy, blocked, excluded or unconfirmed. On the next invocation, the prompt receipt or requestor activity already suppresses checkout-wide resumption under the original duplicate-resume rule. Should the command still complete the reviewer step from Q01=D? It must never resend the requestor's resume command or clear an active requestor to do so.

#### BBQ for Q19

At a barbecue, the cook can return while the inspector is still unavailable. In this picture: the returned cook is the resumed requestor, the absent inspector is the pending reviewer, and a later call completes the pair without restarting the cook.

#### Options for Q19

- Option A: Permit a reviewer-only continuation when current evidence verifies the same pause, the selected resumed requestor and its role assignment, and the counterpart still needs activation. Reapply exclusions and input protections, and do not clear or resume the requestor again. If the reviewer already claimed the intended role or is waiting for review work, leave it alone; uncertain prior delivery requires diagnosis rather than an automatic resend under Q11.
  - Pro: Completes a previously skipped reviewer step without duplicating requestor work or restarting an active reviewer.
  - Con: Must distinguish a missing counterpart action from an already completed or uncertain one using current evidence.
- Option B: Preserve the original whole-checkout skip once the requestor is resuming or resumed; the person completes any missed reviewer activation manually.
  - Pro: Keeps duplicate-resume protection and repeat-run behavior simple.
  - Con: A transiently busy or excluded counterpart leaves the pair incomplete after a bulk run.

#### Recommended option for Q19

Option A: The user requested restoration of the review pair. Separately checking the reviewer action lets a later run finish that restoration while preserving the no-duplicate-requestor rule.

#### Answer to Q19: option A

Option A is proposed for a switched tab where Codex resumed as requestor but Claude could not yet take its new reviewer role. A later run can activate only Claude when the evidence and protections allow it.

User decision: confirmed — Option A. Permit a reviewer-only continuation when current evidence verifies the same pause, the selected resumed requestor and its role assignment, and that the counterpart still needs activation. Reapply exclusions and input protections; never clear or resume the requestor again. Leave a reviewer that already claimed the intended role or is waiting for review work untouched. Uncertain prior delivery requires diagnosis rather than an automatic resend under Q11.

Decision date: 2026-11-08. This completes a previously skipped reviewer action while preserving duplicate-requestor protection, including when the tab's LLM roles were switched.

### Q20: Enforcing the human-only launch

Q16=B permits only the person to launch the command, including previews. What
observable behavior enforces that rule when the caller is a recognized agent
pane? Caller detection cannot prove human origin outside TUIOS.

#### BBQ for Q20

At a barbecue, a sign can reserve the dinner bell for the host, while a latch
can also stop kitchen staff ringing it. In this picture: the host is the
person, kitchen staff are agent callers, the bell is launching the command,
and the latch is refusal from a recognized agent pane.

#### Options for Q20

- Option A: Refuse all invocations, including `--dry-run`, from a recognized
  Claude or Codex caller pane, exit non-zero and send no input. State the
  human-only launch rule in help. Outside TUIOS, that rule still applies but
  caller identity cannot be established by pane detection alone.
  - Pro: Enforces the detectable part of Q16=B without an isolation exception.
  - Con: Blocks previews from agent panes, including a command the person types through an agent's shell escape such as Claude Code's `!` prefix, and cannot detect every caller outside TUIOS.
- Option B: Refuse normal runs from recognized agent panes, but allow previews.
  - Pro: An agent can prepare a read-only preview for the person.
  - Con: Changes Q16=B's prohibition on agents launching the command at all.
- Option C: State the rule in help and documentation, retaining caller-pane
  input protection without refusing agent-origin invocations.
  - Pro: Avoids caller classification as a launch prerequisite.
  - Con: Provides no runtime enforcement when an agent disregards the rule.

#### Recommended option for Q20

Option A: Preserve Q16=B's boundary wherever the existing pane classification
can establish an agent caller, while being explicit about its detection limit.

#### Answer to Q20: option A

Option A is proposed because refusal is observable and follows the confirmed
human-only contract without allowing agent previews implicitly.

User decision: confirmed — Option A. Refuse every invocation, including `--dry-run`, from a recognized Claude or Codex caller pane, exit non-zero and send no pane input. State the human-only launch rule in help. The rule still applies outside TUIOS, although pane detection cannot establish human origin there. Refusal also covers a command the person types through an agent shell escape, such as Claude Code's `!` prefix.

Decision date: 2026-11-08. The user explicitly selected A. This enforces the detectable part of Q16=B without introducing an exception to review-role isolation.

### Q21: Pauses that lead to reviewer activation

A checkout has one saved pause prompt, whichever role wrote it last. Which
saved roles lead to Q01=D reviewer activation, and what happens when the exact
live exchange cannot be identified? No option permits guessing ownership.

#### BBQ for Q21

At a barbecue, the cook's return may need an inspector, while the gardener's
return does not. In this picture: the cook is a paused requestor, the inspector
is the reviewer counterpart, the gardener is a non-review pause, and the work
order identifying the inspection is the exact live review exchange.

#### Options for Q21

- Option A: Activate a counterpart only for a `requestor` pause with exactly
  one identifiable live exchange. A `reviewer` pause resumes in its assigned
  reviewer, defaulting to its author, and wakes no requestor. Other roles
  resume one agent. With no live exchange, resume the requestor but report
  reviewer activation as not applicable; with several, resume the requestor
  but report the reviewer step as ambiguous without input to a counterpart.
  - Pro: Keeps Q01's review-role scope and Q18's exact-exchange evidence.
  - Con: An implementation pause that later requests review does not wake its reviewer.
- Option B: Use post-resumption exchange state rather than the saved role;
  activate only when exactly one live exchange names the selected requestor.
  - Pro: Includes implementation sessions that request code review.
  - Con: A documentation or other pause can activate a reviewer unexpectedly.
- Option C: Attempt reviewer activation for every pause with an LLM counterpart,
  still withholding input until Q18 establishes an exact exchange and takeover.
  - Pro: Gives every pause the same requested pairing behavior.
  - Con: Attempts to establish review context where no review may be in progress.

#### Recommended option for Q21

Option A: Limit automatic pairing to the saved review requestor role, and
report missing or ambiguous exchange evidence without choosing an exchange.

#### Answer to Q21: option A

Option A is proposed because it gives reviewer pauses their own destination
without treating every saved conversation as a requestor pause.

User decision: confirmed — Option A. Activate a counterpart only for a saved `requestor` pause with exactly one identifiable live review exchange. A saved `reviewer` pause resumes its assigned reviewer, defaulting to its author, and wakes no requestor. Other roles resume one agent. When no live exchange exists, resume the requestor and report reviewer activation as not applicable. With several live exchanges, resume the requestor and report the reviewer step as ambiguous, without input to any counterpart. Never guess exchange ownership.

Decision date: 2026-11-08. The user explicitly selected A. This keeps automatic pairing within the saved review-requestor role and preserves Q18's exact-exchange and takeover proof. An implementation pause that later requests review does not automatically activate its reviewer.

Clarification from the Q25 decision, recorded on 2026-11-08: a saved exact
exchange validated as live is the one identifiable exchange, even when other
exchanges are live. Without a valid saved exchange, several live exchanges
remain ambiguous. For a reviewer pause, the author default means the pausing
pane recorded in the handoff.

### Q22: The counterpart pane before reviewer activation

Q01=D allows activation even when this run did not clear the counterpart.
Q19=A leaves an already active reviewer alone on later runs. Should the tool
ever clear the counterpart, and should that leave-alone rule apply on every run?

#### BBQ for Q22

At a barbecue, an inspector still watching the grill need not be called again,
and wiping their notebook does not send them home. In this picture: the
inspector is an active reviewer, calling is reviewer activation, the notebook
is conversation context, and the inspector remaining is a surviving watcher.

#### Options for Q22

- Option A: Never clear the counterpart. On every run, leave it untouched when
  exact-exchange role state and current pane evidence establish an active
  reviewer. Otherwise activate it only under the normal protections. A shell
  indicator alone does not prove which exchange or role its process serves.
  - Pro: Applies Q19 consistently and avoids clearing a surviving watcher.
  - Con: A switched reviewer retains its former authoring context unless the person clears it.
- Option B: Never clear the counterpart, but always deliver to an eligible
  counterpart and rely on its review-resume workflow to retain its watcher.
  - Pro: Makes the first-run delivery rule simple.
  - Con: Can restart a reviewer whose surviving watcher is no longer known in context.
- Option C: Apply `--clear` to the counterpart too before reviewer activation,
  with Q04's background-shell report and all input protections.
  - Pro: A switched reviewer starts with a fresh conversation.
  - Con: Erases context and can duplicate a watcher that survived clearing.

#### Recommended option for Q22

Option A: Use the same proof of an active reviewer on first and later runs,
without clearing the counterpart or treating an arbitrary shell as proof.

#### Answer to Q22: option A

Option A is proposed to preserve Q19's no-duplicate-reviewer behavior throughout
the tool's use, including a person-selected role switch.

User decision: confirmed — Option A. Never clear the counterpart. On every run, leave it untouched when exact-exchange role state and current pane evidence prove that it is already serving as the intended reviewer, including waiting for review work. Otherwise, when activation is needed and eligible after Q18 takeover proof, send its native `review-resume` instruction to resume as reviewer and claim that role if needed, as required by Q01=D. Preserve its conversation context and all normal input protections. A background-shell indicator or former requestor context alone does not prove current reviewer ownership. Apply Q24=B and the user's one-command authorization: the resolved reviewer role and its required override need no further confirmation. This consent qualification was explicitly amended by the user on 2026-11-08.

Decision date: 2026-11-08. The user explicitly selected A after confirming that this option still sends the reviewer instruction when activation is needed. This extends Q19's no-duplicate-reviewer protection to first and later runs without clearing a potentially surviving watcher. A switched reviewer retains former authoring context unless the person clears it separately.

### Q23: Waiting for requestor takeover and reporting a pending reviewer step

Q18=A takeover can take a complete agent turn and stop on a consent question.
Does the run wait for it, and does an expected pending reviewer step fail the
run? Read-only exchange observation never authorizes the tool to claim a role.

#### BBQ for Q23

At a barbecue, the host can wait briefly for a new cook to take over before
calling the inspector, or come back later. In this picture: takeover is Q18's
evidence, the inspector is the counterpart reviewer, the waiting period is a
bounded tool wait, and coming back is Q19 reviewer-only continuation.

#### Options for Q23

- Option A: After requestor acceptance, wait a bounded time for Q18 evidence,
  with the duration selected in design and read-only observation. If it does
  not arrive, report the reviewer step as pending with the known reason or
  timeout. Expected pending takeover does not fail the run; classification
  errors and unconfirmed deliveries still fail under Q07 and Q10. A dry run
  shows reviewer activation as conditional on takeover.
  - Pro: Often restores the pair in one run while allowing human consent to take longer.
  - Con: Extends run duration and requires the person to notice a pending report.
- Option B: Do not wait. Activate only if takeover evidence already exists;
  otherwise report a pending step for Q19 continuation. Use Option A's outcome
  classification and conditional preview.
  - Pro: Keeps runs short without in-run takeover polling.
  - Con: Fresh requestor resumption normally needs a second run to restore its reviewer.
- Option C: Wait as in Option A, but fail the invocation when takeover remains
  pending, as well as for Q10 errors and unconfirmed delivery.
  - Pro: An incomplete pair is visible in the exit status.
  - Con: An unanswered human consent question makes an otherwise successful run fail.

#### Recommended option for Q23

Option A: Allow one-run restoration without classifying a legitimate consent
wait as an input-delivery failure; retain Q19 for later completion.

#### Answer to Q23: option A

Option A is proposed because command acceptance and completed takeover are
different outcomes, and a bounded wait can distinguish them in the report.

User decision: confirmed — Option A. After confirmed requestor command acceptance, wait a bounded time for Q18 takeover evidence using read-only observation; select the duration in design. If proof does not arrive, report reviewer activation as pending with the known reason or timeout. Expected pending processing alone does not fail the invocation. Under the user's subsequent one-command clarification, required author and role overrides are preauthorized; a repeated confirmation prompt is an automation failure, not an expected pending outcome. Classification errors and unconfirmed deliveries still fail under Q07 and Q10. A dry run shows reviewer activation as conditional on takeover. Observation does not authorize the tool to claim a role or answer a consent question.

Decision date: 2026-11-08. The user explicitly selected A. A bounded wait allows takeover processing to finish. The user's subsequent one-command clarification supersedes the rationale allowing consent questions to take longer: this automated path must not ask for those confirmations. Preserve Q18's proof requirement and Q19's later reviewer-only continuation; a successful exit with a pending report does not mean the pair was fully restored.

### Q24: Does the typed reviewer instruction grant override consent?

Q01=D asks the counterpart to claim the reviewer role if necessary, while
Q18=A preserves author and role-override consent gates. Confirm how the typed
instruction should be understood when the recorded reviewer LLM differs.

#### BBQ for Q24

At a barbecue, asking someone to inspect the grill need not hand them the
host's permission to replace another inspector. In this picture: the request
is the typed reviewer instruction, replacement is an LLM-role override, and
the host's explicit permission is the existing Override choice.

#### Options for Q24

- Option A: The instruction supplies context and requests normal role pickup,
  but grants no override consent. On a role conflict the reviewer presents
  `Override` or `Stop`; report its step as awaiting consent until resolved.
  - Pro: Makes Q01=D consistent with Q18=A and existing consent workflows.
  - Con: A requested role switch can still require another human answer.
- Option B: Treat an explicit per-tab role assignment as advance override
  consent for that exact reviewer assignment, requiring a deliberate amendment
  to Q18 and the shared review-resume consent rules before implementation.
  - Pro: Avoids a second question for the person's explicit switch.
  - Con: Reopens confirmed consent requirements and changes shared workflow authority.

#### Recommended option for Q24

Option A: Preserve the existing explicit consent boundary while making the
meaning of "claim the role if you have to" unambiguous.

#### Answer to Q24: option B

Historical proposal: Option A was proposed as the reviewer's clarification to Q01=D, without
silently recording it as the person's decision.

User decision: confirmed — Option B, with the user's explicit one-command clarification on 2026-11-08. Running `resume_paused` is sufficient authorization to consume the intended pause in its resolved target and establish the resolved requestor/reviewer assignments, including necessary pause-author and recorded-role overrides. The command and resumed agents must not ask the person to confirm these operations again. Explicit assignments and unambiguous defaults must carry this launch authorization into the shared workflows. Maximum automation is required. Amend Q18 and the shared `resume-session` and `review-resume` authorization contracts before implementation, preserving exact-exchange evidence and all pane protections. Unresolved target ambiguity is reported and skipped, without a runtime selection question.

Decision date: 2026-11-08. The user selected B, required maximum automation for specified roles, and then clarified the command-wide contract: "one command and it is done", not "one command, and I still need to confirm this or that". This explicitly amends earlier author/requestor/reviewer consent assumptions in Q17, Q18, Q22 and the Q23 pending-consent rationale. Keep the historical options and recommendations as history. Carry the matching shared-workflow changes and no-further-confirmation validation into design and plans; do not reintroduce these questions in the automated path.

### Q25: Identifying requestor panes and the default assignment

Q17=A names a requestor LLM, but a tab can contain several panes of that LLM;
Q06=C skips ambiguous candidates. What identifies a unique assigned pane, and
what evidence supplies the known requestor when no assignment is given?

#### BBQ for Q25

At a barbecue, naming the cooking team may leave two cooks answering; naming
one cook resolves it. In this picture: the team is an LLM kind, each cook is
a pane, the assignment is the person's selection, and the duty roster is
exact-exchange role state or a requestor-authored pause.

#### Options for Q25

- Option A: Permit an assignment to name the requestor pane as well as its
  LLM. Without an assignment, derive the known LLM from exact-exchange role
  state or the pause author only when it was a requestor pause. Such state
  does not distinguish two panes of the same LLM; require a unique candidate
  or explicit pane selection. Unresolved ambiguity still skips under Q06=C.
  - Pro: Makes per-tab switches usable without weakening ambiguity protection.
  - Con: Some tabs need the person to supply a pane-level assignment.
- Option B: Keep assignments limited to the LLM and apply Q06=C when several
  panes match; use the same restricted default-assignment evidence as Option A.
  - Pro: Keeps the assignment input smaller and preserves Q06 literally.
  - Con: The person must rearrange panes to resolve otherwise selectable targets.
- Option C (user amendment): Evolve `pause-session` and its handoff template
  to save intended roles and enough observed session/pane identity and evidence
  for automatic target selection. Resume validates the saved routing against
  live panes without selection arguments or questions. Missing, stale or
  conflicting routing is reported without input to unresolved targets.
  - Pro: Makes target selection part of the saved handoff and preserves the
    one-command automation requirement, including several panes of one LLM.
  - Con: Requires pause-capture and resume-consumption changes; legacy or
    unresolved routing must be reported rather than guessed.

#### Recommended option for Q25

Option A: A deliberate pane assignment resolves a genuine ambiguity, whereas
LLM identity in a role record alone cannot establish one running pane.

#### Answer to Q25: option C

Historical proposal:

> Option A is proposed as the reviewer's Q17 clarification, with the qualification
> that exact-exchange LLM ownership does not itself identify a unique pane.

User decision: confirmed — Option C, the user's explicit handoff-driven selection amendment on 2026-11-08. Selection must come from information saved in the pause-session handoff. Evolve the pause instruction and template to record intended resumed-agent/requestor/reviewer assignments, concrete session and pane identities, checkout and evidence so the bulk command resolves targets automatically, including multiple panes of one LLM. Do not require the person to choose a pane at launch or answer a selection question. Validate saved identities against live state; report unresolved, missing, stale, conflicting and legacy routing without input to unresolved targets or an interactive question. Amend Q17 and Q06 accordingly, preserving no-guessing protection and Q18 takeover proof. Carry the capture/consumption dependency into design, plans and validation.

User rationale, verbatim: "No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achive this". This supersedes both original options' reliance on launch-time pane selection or manual pane rearrangement. The historical recommendation remains unchanged; the user chose this amendment instead.

### Q26: Matching reviewer-only continuation commands

Q14=A exempts reviewer-role review-resume from requestor duplicate suppression.
Q01=D appends explanatory text to that command. Does the exception depend on
the selected role or on the command being exactly the short quoted form?

#### BBQ for Q26

At a barbecue, an inspector's arrival note can include an explanation without
becoming the cook's arrival note. In this picture: the note is a review-resume
invocation, inspector versus cook is the selected role, and the explanation
is the trailing context in Q01=D's typed instruction.

#### Options for Q26

- Option A: Match an invocation selecting the reviewer role, including its
  native command prefix and trailing context. When the saved pause was not a
  reviewer's, it does not suppress the requestor resume. Uncertain role evidence
  prevents input under Q07 and Q08 rather than being guessed.
  - Pro: Applies Q14's role distinction to the actual Q01 instruction.
  - Con: Requires role evidence rather than an exact short-string comparison.
- Option B: Exempt only the exact short command `review-resume as reviewer`;
  count variants with trailing context as duplicate-resume signals.
  - Pro: Keeps the recognized exception narrow.
  - Con: The required Q01 instruction can incorrectly suppress a waiting requestor.

#### Recommended option for Q26

Option A: The semantic reviewer role determines whether the paused requestor
was resumed; explanatory wording does not change that role.

#### Answer to Q26: option A

Option A is proposed as the reviewer's Q14 clarification, retaining uncertainty
protection instead of inferring a role from incomplete screen evidence.

User decision: confirmed — Option A. Identify reviewer-only `review-resume`
continuation by the selected reviewer role, including the native command
prefix and trailing explanatory context. When the saved pause was not a
reviewer's, this continuation does not suppress requestor resumption.
Uncertain role evidence prevents input under Q07 and Q08 rather than being
guessed or prompting for a runtime selection.

Decision date: 2026-11-08. The user selected A. The selected role determines
whether the paused requestor was resumed; the explanatory wording required
by Q01=D does not change that role or become a false duplicate-resume signal.

### Q27: Stating a role switch after the pause

Q17=A accepted an explicit per-tab role assignment at launch, naming the
requestor LLM. Q25=C removed pane-selection arguments, and the command now has
no role input. A switch must therefore be stated to the pausing agent before
the handoff is saved. The draft's own example, Codex taking over as requestor
from Claude, is often decided at resume time, for example when one LLM's
quota ran out overnight. Q25's user text rejects choosing panes at launch. It
does not say whether a role switch can still be named at launch.

#### BBQ for Q27

At a barbecue, the host can swap the cook and the inspector at serving time
without pointing at chairs, because the seating plan already says who sits
where. In this picture: the seating plan is saved routing, the swap is a role
switch, and pointing at chairs is pane selection.

#### Options for Q27

- Option A: Record role switches only at pause time. A later switch needs a
  fresh pause or a manual resume.
  - Pro: Assignments have one source, and the command needs no new argument.
  - Con: A switch decided after pausing has no one-command path, and a
    cleared conversation cannot pause again.
- Option B: Add an optional `--switch-roles NAME[,NAME...]` argument. Names
  are matched like `--except`, against session and checkout folder names. The
  argument swaps the saved requestor and reviewer targets of a saved requestor
  pause with a recorded pair. It names no pane: both panes come from the
  validated handoff. The launch authorizes the switch under Q24=B. An
  unmatched name prevents all input, like a Q09 unmatched exclusion. A matched
  checkout without a recorded pair gets no input, and the run fails.
  On a later run, Q19's reviewer-only continuation checks the resumed requestor
  against the assignment this invocation resolves, with or without the switch;
  a mismatch sends no input and is reported.
  - Pro: Covers a late decision in one command, with no pane selection and no
    question.
  - Con: Adds an argument, which can only swap a pair the handoff already
    recorded.
- Option C: The person edits the handoff's intended assignment by hand before
  launching.
  - Pro: No new argument.
  - Con: Hand edits to a private prompt are easy to get wrong, and nothing
    checks them before input.

#### Recommended option for Q27

Option B: The person can still switch roles at resume time, while every pane
comes from the handoff as Q25 requires.

#### Answer to Q27: option B

User decision: confirmed — Option B. Add optional
`--switch-roles NAME[,NAME...]` to swap the saved requestor/reviewer targets
of a saved requestor pause with a recorded pair. Match exact session and
checkout folder names case-insensitively, as for `--except`. Both panes come
from the validated handoff; the launch authorizes the swap without any
additional pane selection or confirmation. An unmatched name prevents all
input. A matched checkout without a recorded pair receives no input and makes
the run fail. Later Q19 reviewer-only continuation must match the assignment
resolved by that invocation, with or without the switch; a mismatch sends no
input and is reported.

Decision date: 2026-11-08. The user selected B. This covers a role switch
decided after pausing, including the draft's quota-change example, in one
command while preserving Q24's launch authorization and Q25's saved pane
selection. Carry this contract into design, plans and validation; it does not
establish that the command is already implemented.

Clarification from the Q27 decision, recorded on 2026-11-08: the switch
applies only to a saved requestor pause with a recorded pair. Any other
matched checkout, including a reviewer pause that records both targets, is
handled as a checkout without a recorded pair. On a later run, a mismatch
fails the invocation when `--switch-roles` names the checkout and is
otherwise the expected already-resuming skip.

### Q28: How the typed command carries the launch authorization

Q24=B makes the human launch sufficient authorization for author and role
overrides. Today `resume-session` accepts consent only as an explicit yes in
its own conversation, and `review-resume` only as an explicit `Override`. The
requirement asks both workflows to accept the launch instead. It does not say
how a receiving workflow tells a bulk-delivered command apart from the same
command typed by hand. Unless that also changes, the hand-typed command keeps
today's questions. Any process that can type into a pane can produce the same
text. That is already true of typed input today.

#### BBQ for Q28

At a barbecue, a host's note saying "seat this guest at table 4" is useful only
if the waiter can tell it from any scribbled note, and only for table 4. In
this picture: the note is the typed command, table 4 is the target pane and
prompt, and the waiter is the receiving workflow.

#### Options for Q28

- Option A: The typed command carries an explicit bulk-resume marker bound to
  its target: the prompt SHA-256, the receiving pane id, the intended role and,
  for a reviewer, the exact exchange. A marker that matches the receiving
  pane, host, current prompt digest and exchange counts as the person's
  consent, with no question. A mismatched marker grants nothing: the workflow
  reports the mismatch and stops without consuming the prompt or claiming a
  role. A command typed
  by hand without a marker keeps today's consent questions.
  - Pro: The authority covers only this launch, these prompt bytes and this
    pane. A replaced prompt or another pane cannot reuse it, and manual
    resumes are unchanged.
  - Con: Typed commands get longer, and both shared workflows need marker
    parsing and matching rules.
- Option B: In the pane named by the saved routing, any `resume-session` or
  `review-resume` skips the consent question, whoever typed it.
  - Pro: No marker, and manual resumes in that pane stop asking too.
  - Con: A saved prompt becomes consent. That contradicts the template's
    statement that the file grants no permissions, and today's rule that a
    saved prompt is not consent. An old handoff keeps authorizing later
    invocations.
- Option C: The tool writes a single-use authorization record in the artifact
  home, and the typed command refers to it.
  - Pro: The authority lives in a checked file rather than in typed text.
  - Con: Contradicts acceptance criterion 9's read-only tool and adds an
    artifact to create, expire and clean up. Any local process can still
    write it.

#### Recommended option for Q28

Option A: It meets the one-command contract on the bulk path only, and ties
the authority to exact bytes and to a pane the tool has just rechecked under
Q13.

#### Answer to Q28: option A

User decision: confirmed — Option A. Carry an explicit bulk-resume marker
with the delivered command, bound to the current prompt SHA-256, receiving
pane id and agent host, resolved intended role and, for a reviewer, the exact
exchange. The receiving workflow validates those values and accepts a match
as the human launch's consent for required author and role overrides without
another confirmation. A mismatched marker grants nothing: report it and stop
without consuming the prompt or claiming a role, with no fallback consent
question. Ordinary manually typed commands without a marker retain their
existing consent behavior.

Decision date: 2026-11-08. The user selected A. This carries Q24=B's launch
authorization to its resolved targets, including Q27=B's switched assignments,
while preserving the rule that the saved handoff alone grants no permissions
and the bulk tool's read-only artifact contract. Marker syntax, parsing and
matching belong in the design, plans and validation of both shared receiving
workflows before implementation; this decision does not establish that those
changes are already implemented.

Clarification from the Q28 decision, recorded on 2026-11-08: receiving-pane
validation requires independent read-only evidence, not an inherited pane
variable alone. Unavailable or conflicting evidence is a marker mismatch,
which fails the run rather than becoming pending takeover. A resumed agent's
required role override covers only the exchange fixed by the prompt digest
and saved routing. The reviewer marker uses that checkout's pause prompt,
validated against the requestor's consumption receipt.

### Q29: Pauses from two panes running the same host

`pause-session` asks before replacing an unused prompt only when the agent id
differs or is missing. Q25=C now supports several panes of one LLM in a
checkout. When a requestor and a reviewer both run Claude and both pause, the
second pause silently replaces the first unused prompt and its routing. Q21=A
then resumes only the role saved last. Should the replacement check also
compare the pausing pane and saved role?

#### BBQ for Q29

At a barbecue, two cooks in the same apron can each leave a note on the one
hook; the second note should not silently take the first note's place. In this
picture: the apron is the agent id, the hook is the checkout's single prompt
slot, and the notes are pause prompts.

#### Options for Q29

- Option A: Treat a different recorded pausing pane or saved role like a
  different agent id. Before replacing an unused prompt, name its pane and
  role, and ask, as a choice under `interactive_menu.md`.
  - Pro: Protects an unresumed checkpoint as the existing guard does. The
    question comes at pause time, never during the one-command resume.
  - Con: Adds a pause-time question for same-host pairs. Legacy prompts can be
    compared only by agent id.
- Option B: Keep the agent-id check. The last pause in a checkout wins, and
  the requirement documents the limitation.
  - Pro: The pause workflow does not change.
  - Con: A same-host pair loses the requestor's checkpoint and routing
    whenever its reviewer pauses last.
- Option C: Never replace an unused prompt saved by another pane or role. The
  second pause reports it and stops until that prompt is resumed or discarded.
  - Pro: No checkpoint is lost and no question is asked.
  - Con: The second pane cannot save its context until the first prompt is
    handled.

#### Recommended option for Q29

Option A: It extends a protection the pause workflow already has to the
same-LLM layout that Q25 supports.

#### Answer to Q29: option A

Option A is proposed because the pause workflow already asks before
discarding another agent's unresumed checkpoint.

User decision: confirmed: Option A. Extend the existing replacement guard
for an unused or new-since-use prompt to a different recorded pausing pane or
saved session role, even with the same host id. Name the existing checkpoint's
agent, pane and role and ask before replacing it as a choice under
`interactive_menu.md`. Declining preserves the old prompt and stops the new
pause. Legacy prompts without pane or role fields retain the host-id
comparison. Keep one latest checkpoint per checkout.

Decision date: 2026-11-08. The user explicitly selected A. This confirmation
occurs at pause time only and adds no question during one-command bulk resume.
The comparison concerns historical pausing identities, not intended future
role assignments or the Q27 switch.

Clarification from the Q29 decision, recorded on 2026-11-08: an unknown pane
or role, for the existing checkpoint or the current pause, is not by itself a
difference. Compare the remaining recorded fields. This guard is included
in acceptance criterion 14.
