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

## Requirement clarifications for resume-paused

These decisions consolidate the 29 confirmed user choices and their reviewed
clarifications. Later amendments recorded below govern the earlier choices
they refine. The pre-consolidation Git snapshot retains all question text,
alternatives, recommendations and original answers.

| Question | Decision and rationale | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | D: After the selected requestor resumes, activate an actual LLM counterpart with its native reviewer resume instruction and claim if needed. Support role switches per tab; a shell is never a counterpart. This restores both review roles. | Target selection and protected panes; acceptance criteria 11 and 12 | No companion action, shell activation, or activation conditional on clearing the counterpart. |
| Q02 | A: Skip a pane in an active turn immediately, including either selected review target. A later invocation can continue eligible work without delaying independent checkouts. | Target selection and protected panes | Waiting for busy panes or interrupting their work. |
| Q03 | A: Fresh, supported Codex screen evidence of an idle pane with empty input can override stale working status. Blocked status, a question or draft input still prevents input. Readiness and submission are separate checks. | Target selection and protected panes; delivery and command-acceptance evidence | Trusting stale working status absolutely, or overriding blocked or ambiguous evidence. |
| Q04 | A: Report the pane's background-shell indicator when present and leave those shells running. This exposes the duplicate-watcher risk without stopping independent work. | Optional conversation clearing; acceptance criterion 5 | Enumerating or stopping background shells. |
| Q05 | A: Deliver the shared command for existing panes independently of senv. Retain a tracked, unchecked senv integration follow-up, its completion-handoff trigger and links in later effort documents; no date or version is assigned. | Command contract; deferred senv integration follow-up | Integrating senv in this delivery or leaving the deferred work untracked. |
| Q06 | C, amended by Q25: Unresolved targets are skipped and their candidates reported. Validated saved routing governs selection even with several same-LLM panes; a sole live candidate cannot replace missing routing. This prevents guessed targets. | Pause handoff routing; target selection and protected panes | Selecting a first match, asking at launch, or substituting the only live candidate for unresolved handoff routing. |
| Q07 | A: Unreadable or uncertain required evidence causes no input to that checkout, an error and a failing invocation while independent valid checkouts continue. Global discovery failure prevents all input. | Pane discovery and waiting-prompt rules; delivery and command-acceptance evidence; result reporting | Guessing from incomplete evidence or silently treating classification errors as successful skips. |
| Q08 | A: Count screen evidence only when attributable to the current pause. Ignore proven older evidence; uncertain attribution prevents input. Report only known resumer identity and time, otherwise unknown. | Pane discovery and waiting-prompt rules; duplicate-resume protection; result reporting | Counting stale or uncertain screen evidence, or inventing resumer identity. |
| Q09 | A: Match exclusions exactly and case-insensitively against full session and pane names and checkout folder base names. Session and folder matches exclude their scopes; pane matches exclude only those panes. Excluded and caller panes still supply duplicate evidence. Unmatched exclusions prevent all normal-run input. | Target selection and protected panes; result reporting | Partial matching, case-sensitive matching, or ignoring unmatched exclusions. |
| Q10 | A: Expected skips, caller protection and an empty plan succeed. Classification errors, unmatched exclusions and unconfirmed planned actions fail. Preview also fails on classification or exclusion errors; Q27 adds switch errors. This separates protections from unsuccessful actions. | Preview and result reporting; acceptance criterion 7 | Failing every deliberate skip or succeeding despite errors and unconfirmed actions. |
| Q11 | C: Never resend uncertain delivery. For this run's proven unsubmitted Codex clear, resume or reviewer command only, retain the empty-input capture and require two unchanged post-delivery captures. After a fresh protection check, send one Enter to the full target pane id and verify acceptance again. Report recovery use; unproved acceptance fails. Claude has no Enter recovery. | Delivery and command-acceptance evidence; acceptance criterion 7 | Automatic resend, command retyping, repeated Enter, or recovery without proof of text ownership and non-submission. |
| Q12 | A: Skip a redundant Claude clear evidenced after the current pause only if no later prompt follows. Still resume an eligible pane and report RESUME with the already-cleared note. | Optional conversation clearing; preview and result reporting; acceptance criterion 5 | Clearing again or skipping the resume because clearing was already done. |
| Q13 | A: Freshly recheck pause identity, duplicate evidence and pane protections before every input action, including clear, resume, reviewer activation and recovery Enter. Changed eligibility causes a reported skip. This covers concurrent runs. | Target selection and protected panes; delivery and command-acceptance evidence | Acting from a discovery-time eligibility snapshot. |
| Q14 | A, clarified by Q26: Count resume-session in any checkout pane, and review-resume except reviewer-only continuation when the saved pause was not a reviewer's. Counted stopped or declined attempts still suppress repetition; they do not prove takeover. | Checkout-wide duplicate-resume protection | Counting every reviewer restart as requestor resumption, or ignoring requestor review-resume attempts. |
| Q15 | A: Report each checkout holding a prompt, including used prompts, with target identities and separate requestor/reviewer outcomes. Omit prompt-less checkouts and non-target panes, then count omitted panes. This keeps reporting focused without hiding the paired outcome. | Preview and result reporting | Listing every discovered pane or conflating requestor and reviewer results. |
| Q16 | B: Only a person launches the command from a terminal or shell. Agents never launch it, even at the person's request. The historical agent-run experiment is evidence only; review-role isolation receives no exception. | Draft revision; command contract; target selection; acceptance criterion 13 | Agent launches relaying human requests, or an agent-launch exception limited to non-review checkouts. |
| Q17 | A, amended by Q25: Support saved per-tab intended assignments, including role switches. Preserve explicit user direction or verified current assignment, separately from historical authorship. Validate the recorded targets without pane-selection arguments or runtime questions. | Command contract; pause handoff routing; target selection and protected panes | Inferring assignments from pane order, historical authorship alone, or launch-time selection questions. |
| Q18 | A, amended by Q24: Before reviewer activation, prove that the selected LLM consumed the intended pause and restored requestor ownership for the exact exchange. The human launch already authorizes necessary author and role overrides. A receipt or Working alone is insufficient; unresolved takeover leaves the reviewer untouched. | Carrying launch authorization; target selection and protected panes; acceptance criterion 11 | Reviewer activation based only on command acceptance or a receipt, and repeated override confirmation. |
| Q19 | A: A later run may perform only the verified missing reviewer action for the same pause and resolved requestor assignment. Reapply exclusions and protections; never clear or resume the requestor again. Leave an active reviewer alone and diagnose uncertain delivery. | Checkout-wide duplicate-resume protection; acceptance criterion 12 | Checkout-wide suppression of all reviewer recovery, duplicate requestor resumption, or uncertain automatic resend. |
| Q20 | A: Refuse normal and dry runs from recognized Claude or Codex caller panes, including agent shell escapes, with no input and a nonzero exit. State human-only launch in help. The rule also applies outside TUIOS, where pane detection cannot prove human origin. | Draft revision; target selection and protected panes; acceptance criterion 13 | Merely advisory enforcement or permitting preview from a recognized agent pane. |
| Q21 | A, clarified by Q25: Activate a counterpart only for a saved requestor pause and one identifiable live exchange. A valid saved exact exchange identifies it even among other live exchanges. Reviewer pauses resume their saved reviewer pane; other roles resume one agent. No live exchange makes pairing inapplicable; unresolved multiple exchanges remain ambiguous. | Pause handoff routing; target selection and protected panes | Pairing every saved role, waking a requestor from a reviewer pause, or guessing among exchanges. |
| Q22 | A: Never clear the counterpart. On every run, leave a reviewer already serving the exact exchange, including waiting, untouched. Otherwise send its native reviewer resume and claim instruction only after takeover proof and eligibility checks, with launch-authorized overrides. This preserves its context. | Target selection and protected panes; optional conversation clearing; duplicate-resume protection | Clearing the counterpart or treating former requestor context or a shell indicator as current reviewer ownership. |
| Q23 | A: After accepted requestor delivery, observe takeover for a bounded duration selected in design. Missing proof reports pending reviewer activation and does not alone fail; preview shows the dependency. Classification and delivery errors still fail. Repeated consent questions or marker mismatches are failures, not pending takeover. | Target selection and protected panes; preview and result reporting | Unbounded observation, failing expected pending processing alone, or letting the tool claim roles or answer consent questions. |
| Q24 | B: One human invocation authorizes the resolved pause consumption and requestor/reviewer assignments, including required author and role overrides, with no further confirmation. Amend and validate both receiving authorization workflows before bulk-command implementation. Saved routing limits scope but grants no permission by itself. | Command contract; carrying launch authorization; target selection; acceptance criterion 11 | Repeated confirmation, treating typed instructions as insufficient on the authorized bulk path, or giving the saved handoff permanent authority. |
| Q25 | User-defined C: Pause capture records intended assignments, concrete session/pane identities, checkout, observations and evidence, plus exact exchange or not-applicable. Gather read-only evidence without contacting a counterpart. Unknown values preserve the rest of the pause. Resume validates the handoff against live state; missing or legacy routing skips, while conflicting or unreadable required evidence errors. Carry capture and consumption into design, plans and validation. | Pause handoff routing; target selection; acceptance criteria 3 and 14; shared pause instruction and template | Launch-time pane selection, migration questions, guessed assignments, or a unique-live-pane fallback. |
| Q26 | A: Classify reviewer-only review-resume by the selected role, including native prefixes and trailing context. When the saved pause is not a reviewer's, that command does not suppress requestor resumption. Uncertain role evidence prevents input. | Checkout-wide duplicate-resume protection; acceptance criterion 13 | Matching only an exact short command string or guessing an omitted role. |
| Q27 | B: Optional --switch-roles swaps a saved requestor pause's recorded pair, using exact case-insensitive session or folder names and validated saved pane identities. Unmatched names prevent all input; an inapplicable matched checkout receives no input and fails. Later reviewer continuation must match the resolved assignment. A switched continuation repeats the flag; mismatch with the flag fails and without it is an expected already-resuming skip. | Command contract; duplicate-resume protection; target selection; reporting; acceptance criteria 3 and 12 | Pause-time-only switching, hand-edited routing, selecting new panes, or silently continuing a different assignment. |
| Q28 | A: Carry launch consent in a command marker bound to prompt SHA-256, receiving pane/host, resolved role and exact reviewer exchange. Independently establish the receiving pane; inherited `TUIOS_PANE_ID` alone is insufficient under the shared Codex daemon. Match authorizes scoped overrides; mismatch fails without consumption or claim and without fallback consent questions. Reviewer digest matches the requestor receipt. Manual unmarked commands keep existing consent behavior; no authorization artifact is written. | Carrying launch authorization; preview and result reporting; acceptance criterion 11 | Saved routing alone as consent, a new single-use artifact, unverified inherited pane identity, or permission beyond the digest-bound exchange. |
| Q29 | A: Before replacing an unused or new-since-use pause, also compare recorded historical pausing pane and saved role, even for the same host. Name the existing agent/pane/role and ask at pause time; decline preserves it and stops the new pause. Unknown values alone are not differences; compare remaining known fields. Legacy prompts retain host comparison. Keep one checkpoint per checkout and no bulk-resume confirmation. | Pause handoff routing; acceptance criterion 14; shared pause instruction and wiki | Same-host last-pause-wins, a hard replacement prohibition, comparing future assignments, or multiple checkpoints. |

## Existing integration references for resume-paused

- `pause-session` and `resume-session`: existing prompt, receipt and
  agent-override behavior described by the draft.
- `.review-artifacts.ini`: checkout-specific artifact-home declaration.
- `program_status.py`: existing Codex OSC 7501 app reports described by the
  draft.
- `bin/tuitp_resume.py`, `waiting_prompt`: senv's existing launch-time check,
  mentioned in the draft as a possible later integration.
