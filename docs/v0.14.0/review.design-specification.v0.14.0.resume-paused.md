# Specification review transcript for v0.14.0

- Exchange: specification/design-specification/v0.14.0/resume-paused
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-09T09:55:25+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification resume-paused (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 1

### Requestor assessment for design-specification resume-paused (round 1)

The complete design and its twelve pending questions are ready for independent review. Review the design against the requirement's 29 confirmed decisions and their amendments. Do not reopen those decisions or infer user choices from proposed answers.

The design distinguishes verified current behavior from target behavior. It preserves human-only launch, read-only bulk discovery, exact saved routing, scoped marker consent, receiving-session ownership fencing, duplicate protection, clear and input safety, requestor-first pairing, and the deferred senv handoff. It specifies transport and observation bounds without claiming implementation or validation.

I found twelve unresolved design choices. Existing options include tradeoffs, recommendations and proposed answers, with every User decision pending. I consider them sufficient for the current draft, but request an independent search for missing questions and unsupported assumptions. In particular assess the feasibility of independent receiver/session proof, read-only claim-lineage evidence after protocol progress, and marker validation before protected mutations.

No independent reviewer wording suggestions exist for round 1. I clarified that receiver output must omit an ownership token and its digest; the public prompt digest remains part of correlation evidence.

### Change summary for design-specification resume-paused (round 1)

Initial design following the completed and consolidated requirement. Added source facts, target flow, evidence/routing contracts, marker consent, duplicate and input protections, host profiles, clearing, bounded delivery and takeover observation, later reviewer continuation, reporting semantics, acceptance examples and requirement traceability.

Added Q01-Q12 for routing grammar, consent encoding, result persistence, claim lineage, deadlines, host profiles, execution guard, human caller evidence, read-only protocol observation, reused pane identity, mutation revalidation and single-agent observation outcomes. All decisions remain pending. The requirement and its 29 confirmed choices are unchanged.

The separately authorized spelling correction removes achive from project spelling settings and changes its ten whole-word occurrences to achieve in the older requirement review transcript. This correction does not change requirement behavior and is outside this design review's substantive scope.

### Writer response for design-specification resume-paused (round 1)

Writer response:

This is the first independent review of the design. Please assess requirement consistency, completeness of design choices, actionable wording and missing open questions. Proposed answers are recommendations awaiting explicit human decisions. No implementation, commits, pushes or consolidation are authorized by this review request.

### Reviewer focus for design-specification resume-paused (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/[redacted]/git/llm-shared_resume-paused/.reviews/a.review-active.specification.design-specification.v0.14.0.resume-paused.md`
- `C:/Users/[redacted]/git/llm-shared_resume-paused/.reviews/a.review-requested.design-specification.v0.14.0.resume-paused.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-09T10:19:20+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 1

The design follows the requirement closely. All 29 confirmed decisions are
traced, the source facts I checked hold at this checkout, and the twelve
questions are real design choices. It is not ready for convergence: several
mechanisms rely on host evidence that the current TUIOS build does not provide
in the form the design assumes. I checked this with read-only TUIOS commands on
2026-11-09, without typing into any pane.

#### Live TUIOS evidence behind the design assessment for design-specification resume-paused (round 1)

| Observation | Source | Design text it affects |
| --- | --- | --- |
| `tuios agent-log` keeps the newest 256 entries per pane, in daemon memory only, each cut to one line with likely secrets masked. | `tuios agent-log --help` | Claude acceptance, receiver pane proof, Q03, Q19 continuation |
| Prompt and turn-end text is capped at 100 characters, and so are tool-call targets. Five Claude panes all showed a maximum of exactly 100. | `tuios agent-log --json` on five Claude panes | "exact marked input in its current agent log", Q02, the result line |
| Active Claude panes held 170 to 230 of the 256 entries about 40 minutes after their session start. | Same five panes | Q03 option A, Q19 later continuation |
| A background-task completion is logged as a Claude `prompt` entry whose text is `<task-notification>`. | This reviewer pane's own log | "latest actual input" in the receiver proof |
| Claude panes report an `agent_session_id`. All four Codex panes report no harness, no `program_status`, no agent session id, `confidence: none`, and a `working` state about 41 minutes old. | `tuios list-agents --all-sessions --json` | Codex identification, Q06, Q10 |
| Pane ids (`window_id`) are UUIDs. | Same | The "reused id" premise of Q10 |
| Fenced review commands carry the ownership token as a command argument, and the log keeps the first 100 characters of each tool-call target. | This pane's log | The capability statement in the receiving workflow section |

#### Source facts checked against the design table for design-specification resume-paused (round 1)

The table's claims hold for `ReviewArtifactConfiguration.load` and
`prepare_home`, `artifact_home` and `artifact_path`, the rejection of other
`resume-session` arguments, the Override-or-Stop gate and the coordination
record. Four further facts matter for the questions:

- The coordination record keeps only the current `owner`,
  `ownership_generation` and token digest. The generation advances only on a
  claim (`tools/review_exchange_ownership.py` lines 92-109). The transcript
  records a replaced role nature only after Override. There is no claim
  history, so Q03 option B's "existing review claim history" does not exist.
- `claim_selected` already rejects a changed round or occurrence under the
  transition lock (`tools/review_resume_identity.py` lines 97-101). Receiving
  checks before a claim therefore need to cover the prompt digest, routing and
  pane, not the round.
- The routing section of the pause template exists only on this branch
  (`d222792` is not in `main`). The installed skills resolve to the main
  checkout, so prompts paused today carry no routing table. The table cells are
  free prose.
- `resume-session` writes its receipt from the template as an agent action, and
  agents may never launch `resume_paused`. The design names no deterministic,
  agent-callable command that decodes and checks the marker.

#### Main findings for the resume-paused design for design-specification resume-paused (round 1)

1. Marker size against host evidence (Q02). A base64url JSON marker holding
   the root, digest, pane ids, pair and exchange identity runs to several
   hundred characters. The Claude agent log keeps 100, so "the exact marked
   input in its current agent log" (line 248) and the receiver's own pane
   proof (lines 161-163) cannot hold as written. Masking may also hide a long
   base64url run. Codex wraps a long input over several screen lines.
2. Receiver result channel (Q03, Q12). A result line with launch id, root,
   digest, pane, host, role, exchange and generation does not fit one
   100-character log entry. A successful receiver keeps working in the same
   turn, so its turn-end line arrives late. Each host profile needs a defined
   channel.
3. Durable takeover evidence (Q03, Q19). Claude pane evidence lasts roughly an
   hour of active work and is lost when the TUIOS daemon restarts. Under option
   A, Q19=A's later reviewer-only continuation then has nothing left to verify.
4. Proof after protocol progress (Q04). Durable state has no transition
   history, so option A's lineage can only come from pane output. Before
   reviewer activation, the generation moves past the requestor's claim only
   through a claim by an already active reviewer (Q22 leave-alone) or a
   competing pickup, where activation must not happen. Option B, with the
   leave-alone check first, covers both cases.
5. Pane identity across clears and for Codex (Q10). Claude Code starts a new
   session on `/clear`. The person often clears right after copying a paused
   conversation, and `--clear` does it too. Codex panes expose no session
   identity. Option A as written would skip most real targets.
6. Codex profile evidence (Q06). Codex panes show no version evidence in
   discovery. Under Q07=A, "fail classification when no unique compatible
   profile is established" fails every invocation that has a Codex target.
7. Activated reviewer observation (lines 264-269 and Q12). The 120-second
   bound covers single agents and requestor takeover. Nothing says how long an
   activated reviewer is observed for the marker mismatch or repeated question
   that the outcome table counts as failures.
8. Missing question: where the receiving workflows run marker validation.
9. The capability statement (lines 178-179) promises that captures used as
   evidence never show a capability. The design does not control that:
   existing commands print it.
10. Recovery budget (lines 250-252): a delivery call with `--timeout 100000`
    can use the whole 100-second action budget, leaving no time for Q11's
    recovery.
11. "Latest actual input" (line 163) fails when a host notification arrives
    after the marked command.
12. Execution guard location (Q07, line 214): it must stay outside the
    checkout for "no writes by the bulk reader" (line 362) to remain testable.

### Question verdicts for design-specification resume-paused round 1

All twelve questions are in scope and none reopens a confirmed requirement
decision. Every answer below is a reviewer proposal: each question still
awaits an explicit user decision. I differ from the writer's recommendation on
Q01, Q02, Q03, Q04 and Q10, and propose one new question, Q13.

| Question | Verdict | Writer | My answer | Change needed |
| --- | --- | --- | --- | --- |
| Q01 | Needed; option A's benefit is smaller than stated | A | B | State that no released prompt carries the table |
| Q02 | Needed; both options ignore host log limits | A | New option C | Add option C; tie the size bound to host profiles |
| Q03 | Needed; option B's premise is wrong, option A's limits are unstated | A | Revised B | Rewrite both options |
| Q04 | Needed; option A has no durable data source | A | B, after the leave-alone check | Rewrite the consequences |
| Q05 | Agree | A | A | Recovery budget wording |
| Q06 | Agree; the outcome for missing evidence is unstated | A | A | Name the Codex evidence and its outcome class |
| Q07 | Agree | A | A | Keep the guard outside the checkout |
| Q08 | Agree | A | A | None |
| Q09 | Agree | A | A | None |
| Q10 | Needed; both options miss clears and Codex | A | New option C | Add option C |
| Q11 | Agree | A | A | Note the existing claim lock; depends on Q13 |
| Q12 | Agree; scope too narrow | A | A, extended | Cover the activated reviewer |
| Q13 (new) | Missing | None | A | Add the question |

#### Q01 verdict on routing representation for design-specification resume-paused (round 1)

I would choose option B. The installed skills resolve to the main checkout,
whose pause template has no routing section, so no released prompt carries
the table. Its cells are free prose ("read-only evidence; user direction where
applicable"). A "complete grammar" over them would amount to inference. If Q10
adds identity fields, the table also lacks them. Since the template is still
unreleased, this delivery can make the versioned JSON block its single source,
with the table rendered from it for people to read.

Replacement recommendation: "Option B: no released prompt holds the routing
table, and its prose cells cannot be read without inference. Bulk launch
requires the JSON block; table-only and routing-free prompts stay readable
through ordinary `resume-session` and are skipped with a reason."

#### Q02 verdict on marker transport for design-specification resume-paused (round 1)

Both options assume the full marker can be compared exactly in pane evidence.
The Claude agent log keeps 100 characters per prompt entry and masks likely
secrets, and Codex wraps long input on screen. I would choose a new option C:

```md
- Option C: Use a compact versioned marker: a random launch id first, then
  the receiving pane id, the resolved role and a SHA-256 binding over the
  canonical root, prompt digest, receiving pane and host, role, pair and exact
  exchange with its round. The receiver recomputes the binding from its own
  prompt, routing and live exchange. Each host profile states how many leading
  characters its evidence keeps; the launch id must fall inside them.
  - Pro: Fits the Claude agent log's 100-character entries and keeps Codex
    input short; one validator computes the same binding for both workflows.
  - Con: A mismatch cannot name the differing field from the marker alone, so
    the receiver and the bulk tool each report the values they bound.
```

If option A stays, its size bound must come from each host profile's logged
form, and the launch id must lead the payload.

#### Q03 verdict on takeover evidence persistence for design-specification resume-paused (round 1)

Option A's con must state the measured limits: 100 characters per entry, 256
entries per pane, daemon memory only, and active panes filling it within about
an hour. Option B refers to an "existing review claim history" that does not
exist. I would choose a revised option B:

```md
- Option B: Write non-secret bindings into existing durable records.
  `resume-session` adds the launch id and receiving pane to its receipt (a new
  receipt schema version), and a marked `claim` records the launch id with the
  generation it issued in the coordination record. Neither holds a token or a
  token digest.
  - Pro: Takeover proof and Q19's later continuation survive log eviction,
    daemon restarts and cleared screens; Q04 becomes a comparison of durable
    fields.
  - Con: Adds a receipt schema version and a coordination field, with legacy
    parsing for both, and gives the review exchange claim a marker input.
```

Reason: Q19=A is a confirmed requirement, and option A makes it unavailable
after about an hour of requestor work or any daemon restart.

#### Q04 verdict on proof after protocol progress for design-specification resume-paused (round 1)

I would choose option B, with Q22's leave-alone check applied first. The
generation advances only on a claim, and the record keeps no claim history.
Before reviewer activation, a newer generation can only come from a claim by
an already active reviewer, which the leave-alone check reports, or from a
competing pickup, which must block activation. Option A's "transition
evidence" would rest on pane output alone. If Q03 records the marked claim's
generation durably, option B checks durable fields only.

Replacement for option B's con: "Before activation, only an already active
reviewer or a competing pickup can advance the generation. The leave-alone
check reports the first; the second correctly blocks activation."

#### Q05 verdict on time budgets for design-specification resume-paused (round 1)

Option A is right. Add one sentence: the delivery call may use its full
`--timeout 100000`, so either Q11's recovery and acceptance checks get a
separate bounded window after the call returns, or recovery runs only within
the remaining budget and is otherwise reported as unconfirmed.

#### Q06 verdict on host profile selection for design-specification resume-paused (round 1)

Option A is right, but the question must say where Codex version evidence comes
from. Observed Codex panes expose no harness, program status or version in
discovery. It must also name the outcome when no profile is established. Under
Q07=A that outcome is a classification failure, which would fail every run
with a Codex target in the observed setup. If that is not intended, raise it as
a question to the person; do not reclassify it silently.

#### Q07 verdict on the execution guard for design-specification resume-paused (round 1)

Option A is right. Name where the guard lives: an OS named lock, or a lock file
under the user's temporary directory keyed by the canonical root digest. It
must never sit in the checkout or its artifact home, so "no writes by the bulk
reader" stays testable.

#### Q08 and Q09 verdicts for design-specification resume-paused (round 1)

I agree with option A for both, with no change.

#### Q10 verdict on saved pane identity for design-specification resume-paused (round 1)

Both options assume an agent instance identity that survives a clear. Claude
Code starts a new session on `/clear`, which the person often runs right after
copying a paused conversation and which `--clear` runs itself. Codex panes
expose no session identity. Option A would skip nearly every real target.
TUIOS pane ids are UUIDs, so "reuse" in practice means a pane now running
another host, checkout or session. I would choose a new option C:

```md
- Option C: Treat the live pane id, host, checkout and TUIOS session as the
  target identity, and record the agent session id only as supporting
  evidence. A change of host, checkout or session is a reassignment and skips
  the target; a changed agent session id alone is reported, not refused.
  - Pro: Survives routine clears and the tool's own `--clear`, and works for
    Codex panes that expose no session id.
  - Con: Treats a restarted agent of the same host in the same pane as the
    same target, and relies on pane id uniqueness across saved TUIOS sessions
    restored after a daemon restart, which the design must confirm.
```

Lines 135-137 then require "evidence tying the id to the current pane, host,
checkout and session" in place of "the current agent session".

#### Q11 verdict on revalidation before the claim for design-specification resume-paused (round 1)

Option A is right. Add that `claim_selected` already rejects a changed round
or occurrence under the transition lock, so the receiving recheck before the
claim covers the digest, routing and pane. It runs through the Q13 validator.

#### Q12 verdict on completion evidence for design-specification resume-paused (round 1)

Option A is right. Extend it to every accepted receiver, including an
activated reviewer: an observed marker mismatch or repeated question fails,
and no explicit failure by the bound reports accepted with completion
unconfirmed.

#### Proposed Q13 on the receiving validation surface for design-specification resume-paused (round 1)

Add this question in the template's shape:

```md
### Q13: Receiving-side marker validation surface

Both receiving workflows must decode the marker, prove their pane and recheck
bindings before the receipt and the claim. `resume_paused` refuses agent
callers, so it cannot run these checks. Where should they run?

#### BBQ for Q13

A courier checks a parcel seal with the depot scanner instead of by eye. In
this picture: the seal is the marker, the scanner is a shared validator, and
checking by eye is instruction-only validation.

#### Options for Q13

- Option A: Add a separate read-only, agent-callable validator launcher shared
  by `resume-session` and `review-resume`. It decodes the marker, recomputes
  the binding, reads pane evidence and a read-only exchange snapshot, and
  returns typed JSON, with no writes and no capability.
  - Pro: One deterministic implementation for both workflows and hosts, and
    Q11's rechecks become one command before each protected mutation.
  - Con: Adds a public launcher that must stay separate from the human-only
    `resume_paused` and its caller refusal.
- Option B: Validate in the instructions only: each workflow tells the agent
  how to decode the marker and compare it with the evidence.
  - Pro: Adds no executable surface.
  - Con: Strict decoding, duplicate-key rejection and binding comparison rely
    on model reasoning, which tests with fake TUIOS output cannot cover.

#### Recommended option for Q13

Option A: deterministic checks keep both receiving workflows on one contract
and make the marker rules testable.

#### Answer to Q13: option A

Option A: Add a separate read-only, agent-callable validator launcher shared
by `resume-session` and `review-resume`. Deterministic checks keep both
receiving workflows on one contract and make the marker rules testable.

User decision: pending
```

### Requested changes for design-specification resume-paused round 1

Requested changes:

Line numbers refer to the reviewed design. The question changes are listed in
the question verdicts above; the changes below are to the design body.

#### Host evidence facts in the source table for design-specification resume-paused (round 1)

Add rows to "Confirmed source facts for resume-paused" for:

- `tools/review_exchange_ownership.py`: the generation advances only on a
  claim, and no claim history is kept.
- The TUIOS agent log: 256 entries per pane in daemon memory, one line per
  entry, 100 characters for prompt, turn-end and tool-target text, likely
  secrets masked.
- `tuios list-agents`: Claude panes report `agent_session_id`; observed Codex
  panes report no harness, program status or session id.

Reconfirm each against the TUIOS build you name as supported, with read-only
commands only, and cite the command used.

#### Logged-form matching for markers for design-specification resume-paused (round 1)

Lines 161-163 and 248 compare "this exact marked command". Replace that with
a comparison against the host profile's logged form of this run's marked
command, for example:

```md
Prove the receiving pane independently: its agent log or capture must show
this run's marked command, in the host profile's logged form and recorded
after delivery, as the latest typed input in the same checkout and host.
Host-generated entries, such as Claude's `<task-notification>` prompts, are
not typed input.
```

Claude acceptance (line 248) then requires "this run's marked command in the
Claude profile's logged form as a `prompt` entry recorded after delivery". Keep
the launch id inside the logged prefix (see Q02).

#### Result line channel per host profile for design-specification resume-paused (round 1)

Lines 271-276 must name where each host's result line appears and how long it
can be. On Claude, one log entry keeps 100 characters, and a successful
receiver keeps working in the same turn. One workable shape: a compact result
line (launch id, outcome and, after a claim, the generation) as the first line
of a stopping turn's final message, with success proved by durable records if
Q03 takes option B. State the Codex form on screen.

#### Activated reviewer observation for design-specification resume-paused (round 1)

Extend lines 264-269 so the 120-second bound and Q12's outcome classes also
apply to an activated reviewer. Reviewer acceptance alone is not reviewer
completion.

#### Capability handling wording for design-specification resume-paused (round 1)

Replace lines 178-179 with:

```md
Capabilities stay in receiving-session memory and are never sent to the bulk
tool or written into routing, markers or result lines. Existing commands can
show a capability in pane output or log entries, so the bulk tool extracts
only the defined marker, result and readiness patterns from captures and logs,
keeps raw text in memory only, and never prints or stores it.
```

#### Codex identification wording for design-specification resume-paused (round 1)

Lines 88-90: state that observed Codex panes expose no harness or program
status, so the pane-name fallback is the normal Codex path today, and name the
supported name signature.

#### Validation coverage additions for design-specification resume-paused (round 1)

Add to lines 357-363: logged-form truncation and masking, host notification
prompts between delivery and proof, a cleared Claude pane with a changed agent
session id, Codex panes without program status, an activated reviewer that
stops on a marker mismatch, recovery near the end of the action budget, and
evidence evicted before a later reviewer-only continuation.

### Writer instructions for design-specification resume-paused round 1

Another automated review round is needed for the requested changes above.

1. Apply the body changes and restate Q01 to Q04, Q05, Q06, Q07, Q10, Q11 and
   Q12 with the verified facts. Add Q13 in the template's shape, with its BBQ
   section.
2. Where my answer differs from your recommendation (Q01, Q02, Q03, Q04 and
   Q10), either adopt mine, or keep yours and answer the evidence in the
   question text. Either way, present both answers so the person can decide.
3. Leave every `User decision: pending` line as it is. Neither reviewer nor
   writer records a user choice.
4. Reconfirm the TUIOS facts on the build you name as supported, using only
   read-only commands (`list-agents`, `agent-log`, `capture-pane`, help
   output). Never type into a pane. Where a fact cannot be confirmed, say so
   in the source table rather than assuming it.
5. Do not change the requirement or its 29 decisions. If a change seems to
   need one, for example the outcome class for an unestablished Codex profile
   under Q07=A, raise it as a question to the person.
6. Run the decision scanner, Markdown lint and spell check on the design, then
   request the next review round. This answer authorizes no consolidation,
   implementation, staging or commit.

### Final reviewer decision for design-specification resume-paused round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-09T10:32:34+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 2

### Requestor assessment for design-specification resume-paused (round 2)

The updated design and thirteen pending questions are ready for round 2. The requirement's 29 confirmed decisions are unchanged. No question or human answer has been removed; original options and writer/reviewer recommendation history remain visible.

I consider the question set sufficient after adding Q13 for the missing deterministic receiving validator. Accepted findings now cover volatile/truncated evidence, durable marked-claim bindings, current-generation comparison, clears, absent Codex identity/version evidence, result channels for every receiver, recovery budget exhaustion, external execution locks and capability exposure in raw logs. The document explicitly states that marked full-input profiles and restored-session UUID behavior are not validated and must be validated for both hosts before release.

The writer adopts reviewer proposals Q01=B, Q02=C with complete-input proof, Q03=revised B, Q04=B and Q10=C with the confirmed conflict outcome retained. Other recommendations remain A. All thirteen User decision lines remain pending. Full-command proof cannot be replaced by a truncated correlation prefix under the confirmed requirement. Known host/checkout/session reassignment remains a classification error, rather than a skip. Those two differences are deliberate and explained, not implicit requirement changes.

Read-only observations reconfirm TUIOS 0.12.1 commit 850335c, 256 volatile masked entries, sampled prompt text reaching 100 characters, host notification prompt entries, UUID pane ids and missing Codex harness/session ids. Unlike the reviewer's earlier observation, the later writer sample exposes Codex app status; the design handles both. Capture help supports row unwrapping but does not prove the host retained a complete marked command. No keys were sent to any pane and the bulk launcher was never invoked.

### Change summary for design-specification resume-paused (round 2)

Revised the body and Q01-Q12 after round 1 and added Q13. New routing uses authoritative versioned JSON with a derived human table. Compact markers bind the entire canonical assignment; a short logged prefix is supplementary to complete typed-input proof. Receipts gain proposed schema 3 binding fields, and marked claims atomically bind their generation in existing coordination, with no new authorization or continuation artifact.

Added read-only host/source evidence, clear-tolerant pane identity, current-generation takeover checks after the active-reviewer leave-alone check, an external per-checkout guard, a shared read-only receiving validator, profile/version requirements and explicit unsupported-profile failure consequences. Added bounded compact host results, continuing-turn durable success proof, observation for activated reviewers, capability extraction limits and remaining-budget-only recovery.

Expanded validation to truncation/masking, host notifications, full-input rendering, clear-induced session changes, absent Codex app status, reviewer marker failure, exhausted recovery budget and later continuation after log eviction/restart. All thirteen decisions are pending. Original question IDs, options and proposal history are preserved; the requirement is unchanged.

### Writer response for design-specification resume-paused (round 2)

Writer response:

Accepted the substantive round 1 findings and adopted the changed recommendations, with two requirement-preserving qualifications. First, a 100-character log prefix proves correlation only: the exact marked typed command still needs a tested full capture or pane-bound transcript. This is a delivery prerequisite, explicitly unvalidated here, rather than an assumption that truncation preserves the command. Second, Q10 option C retains classification failure for known target reassignment under confirmed Q07; only unavailable routing/identity skips. The reviewer's proposed skip for known reassignment would conflict with that rule.

Q03 no longer assumes a claim history. New non-secret fields are added by receivers to existing receipt/coordination records; ordinary transitions retain them and a superseding claim invalidates them. Existing token-digest storage is unchanged. Q04 checks current generation after the active-reviewer leave-alone check. Q13 separates deterministic agent-callable validation from the prohibited agent invocation of the bulk command.

The evidence table names the checked build and commands, and distinguishes varying Codex app status from absent session/version evidence. No marked-input acceptance or clear syntax has been live-tested. Please assess whether the explicit prerequisite gates and revised options fully address the evidence limits without weakening confirmed requirements. All answers remain proposals. No consolidation, implementation, staging, commit or push is authorized.

### Reviewer focus for design-specification resume-paused (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-09T10:44:07+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 2

Round 2 resolves most of round 1. The compact marker, durable bindings,
current-generation proof after the leave-alone check, clear-tolerant pane
identity, the shared validator, the external guard, the budget wording and the
evidence table all read correctly against the code and the requirement.

The writer's two qualifications are right, and I withdraw the round 1
suggestions they replace:

- The requirement asks for "this exact marked command" as independent
  evidence, so a logged prefix can only corroborate it. A prefix-only proof
  would have weakened Q28.
- Q25 makes conflicting required evidence an error, so a known reassignment is
  a classification failure, not the skip I proposed for Q10.

One gap is more than wording: the complete-input channel for Codex rests on a
TUIOS feature that does not do what the design needs.

#### Evidence checked for the round 2 design changes for design-specification resume-paused (round 2)

| Observation | Source | Design text it affects |
| --- | --- | --- |
| `--unwrap` joins "the rows that the pane wrapped because a line was longer than the pane. Each line then comes back as the program wrote it." | `tuios capture-pane --help` | Line 53, lines 189-190, line 301 |
| Both agent interfaces lay out their own text rows, so a long input comes back split as the program wrote it, not as one line. Confirm with a read-only capture. | Same help text; full-screen agent rendering | Complete-capture proof for both hosts |
| Codex session files start with a `session_meta` record holding `id`, `session_id`, `cwd`, `timestamp` and `cli_version` (0.167.0 on this machine), followed by the user messages. | Key names of the newest `~/.codex/sessions` file | Codex full-input proof, Q06 version evidence |
| TUIOS supports Codex hooks through Codex's `hooks.json`, reporting pane state and the conversation id. `tuios integration status codex` reports it not installed here. | `tuios integration --help` and `status` | Codex identity and version source |
| Only a newly issued claim advances the generation: `start`, a `pickup`, or a `wait-request`, `wait-answer` or `reclaim` that moves ownership to the other role (`tools/review_exchange_core.py` lines 206-236 and 286-306). | Source | Line 358 |
| `CoordinationRecord.from_dict` rejects unknown keys through `strict_fields` (lines 206-223). | Source | Lines 328-337, rollout |

#### Findings that remain for the resume-paused design for design-specification resume-paused (round 2)

1. Codex complete-input proof (lines 189-190 and 298-301). "A complete
   capture with tested row unwrapping" relies on `--unwrap`, which only joins
   pane-level wraps. Codex wraps its own rows. Three channels exist, each with
   different costs: screen rebuilding, the Codex session file found by the
   unique launch id, or TUIOS Codex hooks reporting the conversation id. This
   is a design choice the person should see, so I propose Q14.
2. Claude complete capture (line 189). The same limit applies to a Claude
   screen capture. The session-id-tied transcript is the workable Claude
   channel. A screen capture can only corroborate.
3. Codex recovery Enter (lines 309-312). An unsubmitted command is in no
   session file. Recovery needs the input box to show the complete command
   under the Codex profile. When the profile cannot prove that for a wrapped
   command, no recovery Enter is sent.
4. Generation wording (lines 357-358). "Ordinary protocol progress does not
   advance the generation" is not precise: a counterpart's wait claim does.
   The leave-alone check already covers that case, so only the sentence
   changes.
5. Absent versus conflicting target (lines 148-153 and Q10 option C). The
   design does not say which class applies when the saved pane UUID is no
   longer listed, or is listed with no agent. Both are common after a person
   closes an agent. The error-or-skip outcome changes the exit status.
6. Forward compatibility (lines 328-337). Readers from before this version
   reject a coordination record carrying the new binding fields. The same
   holds for a schema 3 receipt read by an older `resume-session`. The rollout
   must turn on the marked route only once every reader of those exchanges
   runs this version.

### Question verdicts for design-specification resume-paused round 2

I agree with every current recommendation, Q01 to Q13. Each still awaits an
explicit user decision; none is recorded. One new question is needed, Q14.

| Question | Verdict in round 2 | Recommendation | My answer | Change needed |
| --- | --- | --- | --- | --- |
| Q01 | Agree | B | B | None |
| Q02 | Agree, including the full-command proof gate | C | C | Point the complete-input channel to Q14 |
| Q03 | Agree | B | B | Add the forward-compatibility sentence |
| Q04 | Agree | B | B | None; line 358 is fixed in the body |
| Q05 | Agree | A | A | None |
| Q06 | Agree; the consequence is now stated | A | A | Mention the Q14 option C source of Codex version |
| Q07, Q08, Q09 | Agree | A | A | None |
| Q10 | Agree; the writer's error class is right | C | C | Say which class a missing or agent-less pane takes |
| Q11, Q12, Q13 | Agree | A | A | None |
| Q14 (new) | Missing | None | B | Add the question |

#### Round 2 notes on Q06 and Q10 for design-specification resume-paused (round 2)

Q06: option A's con can add that TUIOS Codex hooks (Q14 option C) would tie a
`cli_version` to the pane before delivery. Without them, the Codex version is
known before delivery only from a banner still in scrollback.

Q10: option C should say how it classifies a saved pane UUID that is missing
from discovery, or listed with no agent. Q25 makes "absent targets" an
expected skip and a "known conflicting identity" an error. A pane now running
a different agent host is a conflict; a missing or agent-less pane reads as
absent. If you see it differently, put it to the person rather than choosing.

#### Proposed Q14 on Codex complete-input proof for design-specification resume-paused (round 2)

Add this question in the template's shape:

```md
### Q14: Codex complete-input proof channel

Q02 requires proof of the complete marked command. `capture-pane --unwrap`
joins only rows the pane wrapped; Codex lays out its own rows, so a long input
comes back split as Codex wrote it. Observed Codex panes report no
conversation id. How should the Codex receiver and the bulk tool prove the
complete typed command?

#### BBQ for Q14

A depot can read a long address off a folded label, or look the parcel up in
its own ledger by tracking number. In this picture: the folded label is the
Codex screen, the ledger is Codex's session file, and the tracking number is
the unique launch id.

#### Options for Q14

- Option A: Rebuild the command from the screen with a tested Codex layout
  profile (prompt prefix, indentation and break rules), using `--unwrap` only
  for pane-level wraps.
  - Pro: Pane-bound by construction; reads nothing outside TUIOS.
  - Con: Depends on Codex rendering details that can change between versions,
    and a break at a space is ambiguous unless the profile proves otherwise.
- Option B: Find the Codex session file whose latest user message is exactly
  this run's marked command, with the checkout as its `cwd` and a time after
  delivery. Tie it to the target pane through that pane's screen showing the
  command's leading part, with the same unique launch id, followed by
  `Working`.
  - Pro: Reads the complete input exactly, as the Claude transcript proof
    does, and the same file's `cli_version` confirms the version after
    delivery.
  - Con: The session-file location and format become part of the Codex
    profile; the pane tie rests on the unique launch id, not a pane-reported
    id; the files hold whole conversations, so only the defined fields are
    read, in memory.
- Option C: Require TUIOS Codex hook integration so the pane reports its own
  Codex conversation id, then read that session file.
  - Pro: A direct pane-to-session tie, with `cli_version` available before
    delivery for Q06.
  - Con: A setup step on every machine (not installed on the observed one),
    and hook attribution under the shared Codex app-server daemon must be
    proved, because inherited pane variables can name another pane.

#### Recommended option for Q14

Option B: exact complete input without layout rebuilding, host setup or
inherited pane variables. Q06's pre-delivery Codex version evidence stays as
stated there.

#### Answer to Q14: option B

Option B: Prove the complete Codex command from the session file whose latest
user message is this run's marked command in the same checkout, tied to the
target pane by the unique launch id on its screen followed by `Working`.

User decision: pending
```

### Requested changes for design-specification resume-paused round 2

Requested changes:

Line numbers refer to the round 2 design.

#### Corrected capture facts in the source table for design-specification resume-paused (round 2)

Line 53: replace the `capture-pane` row with: "`--unwrap` joins only rows the
pane wrapped; a program that lays out its own rows comes back as it wrote
them. Both agent interfaces do, so screen captures cannot prove a long command
in full on their own." Add two rows. Codex session files hold `session_meta`
(`id`, `cwd`, `cli_version`) and the user messages. TUIOS supports Codex hooks
reporting the conversation id; they are not installed on the observed machine.
Confirm the layout claim with one read-only capture.

#### Complete-input channel per host for design-specification resume-paused (round 2)

Lines 189-190: "Claude needs the host transcript tied through its observed
session id; a screen capture only corroborates. Codex uses the channel chosen
in Q14." Lines 298-301: Claude acceptance keeps the logged `prompt` entry plus
transcript proof. Codex acceptance requires the command's leading part, with
the launch id, on screen followed by `Working`, plus the Q14 proof.

#### Codex recovery evidence for design-specification resume-paused (round 2)

After line 312, add: "An unsubmitted command is in no session file. Recovery
requires the Codex profile to prove the complete command in the input box;
when it cannot, send no recovery Enter and report unconfirmed delivery."

#### Generation wording in the takeover proof for design-specification resume-paused (round 2)

Lines 357-358: replace "Ordinary protocol progress does not advance the
generation." with "Transitions by the current owner keep the generation; only
a newly issued claim advances it, such as a pickup or a counterpart's wait
claim."

#### Absent and conflicting targets for design-specification resume-paused (round 2)

After line 150, add the classification for a saved pane UUID that is missing
from discovery or listed with no agent (absent, expected skip) and for one now
running another agent host (conflict, classification error). Add both to the
acceptance examples. If this does not follow from Q25 as you read it, raise it
as a question.

#### Rollout order for the new binding fields for design-specification resume-paused (round 2)

After line 337, add: "Readers before this version reject unknown coordination
fields and do not know receipt schema 3. Turn on the marked route only after
every reader of these exchanges runs this version."

### Writer instructions for design-specification resume-paused round 2

Another automated review round is needed for Q14 and the body changes above.

1. Add Q14 in the template's shape, with its BBQ section, and keep the history
   note style used for Q01 to Q13. Apply the body changes and the Q06 and Q10
   notes.
2. Keep every `User decision: pending` line unchanged; no answer is a user
   decision.
3. Confirm the layout and Codex session-file facts with read-only commands
   only (`capture-pane`, `list-agents`, `integration status`, key names of a
   session file). Never type into a pane, install hooks or open conversation
   content beyond the key names you cite.
4. Do not change the requirement. If the absent-target classification or
   another point seems to need a requirement change, raise it as a question.
5. Run the decision scanner, Markdown lint and spell check on the design, then
   request the next review round. This answer authorizes no consolidation,
   implementation, staging or commit.

### Final reviewer decision for design-specification resume-paused round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-09T10:58:15+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 3

### Requestor assessment for design-specification resume-paused (round 3)

#### Design assessment for resume-paused round 3 for design-specification resume-paused (round 3)

The design now has fourteen distinct questions, all explicitly pending user
decision. The proposed answers remain Q01=B, Q02=C, Q03=B, Q04=B, Q05=A,
Q06=A, Q07=A, Q08=A, Q09=A, Q10=C, Q11=A, Q12=A and Q13=A; new Q14 proposes B.
The options and recommendation history remain. No confirmed requirement
decision was changed, and no further missing question is currently identified.

Round 2's substantive recommendations are accepted. Complete input cannot be
proved by pane unwrapping alone. Q14 exposes screen reconstruction, session
files and hooks with their costs. The proposed session-file channel retains
independent pane correlation, exact latest typed-input comparison and strict
failure on missing or ambiguous evidence. Pre-delivery version selection and
unsubmitted-input recovery retain separate proof gates.

Read-only checks confirmed capture help's pane-wrap semantics, interface-created
breaks in the Claude capture, Codex session metadata keys including session
identity, checkout, timestamp and cli_version 0.167.0, and absent Codex hook
installation. Conversation contents were not inspected; neither a complete
Codex input profile nor hook attribution was validated. Source confirms strict
coordination fields and newly issued claim generation semantics. The fourteen
question scanner has no diagnostics. No pane input, hook installation, bulk
launch or implementation was performed.

### Change summary for design-specification resume-paused (round 3)

#### Design changes for resume-paused round 3 for design-specification resume-paused (round 3)

Added Q14 with three complete-input channel options, BBQ explanation, proposed
answer B and an explicit pending user decision. Related body text uses the
proposed exact session-file input channel with fresh launch-id pane correlation;
Claude uses its session-id-tied transcript and capture only corroborates.

Clarified that unsubmitted Codex text is absent from the session file: recovery
Enter requires the tested layout profile to prove the entire exact input box
command, otherwise delivery is unconfirmed without recovery. Added the source
metadata and integration observations, and kept pre-delivery version evidence
independent of post-delivery file matching.

Clarified generation issuance, absent versus conflicting saved targets, and the
all-readers compatibility rollout for new coordination fields and schema 3
receipts. Added acceptance and validation cases; updated Q02, Q03, Q04, Q06 and
Q10 consistently, preserving prior options, history and pending decisions.

### Writer response for design-specification resume-paused (round 3)

Writer response:

#### Writer response for resume-paused round 3 for design-specification resume-paused (round 3)

Accepted all six round 2 findings. No substantive disagreement remains.
The reviewer withdrew the earlier prefix-only consent and reassignment-skip
suggestions; the stricter exact-command and known-conflict requirements remain.

Q14 follows the proposed B channel while stating the unvalidated boundaries:
metadata is confirmed, complete typed-input parsing and pane correlation still
require a tested profile. This check did not inspect conversation content or
claim that session metadata alone identifies a pane. The Claude read-only
capture confirms interface-created breaks survive pane unwrapping. Codex
screen reconstruction remains a distinct tested-profile obligation rather than
a claimed consequence of the unwrap option.

Missing UUIDs and agent-less panes are classified as absent expected skips,
consistent with the settled absent-target requirement; changed live hosts are
classification errors. All-readers rollout prevents older strict readers from
encountering unsupported binding fields. All fourteen user decisions remain
pending. Please assess Q14 and the related edits for convergence, without
consolidating or treating any proposed answer as a user decision.

### Reviewer focus for design-specification resume-paused (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-09T11:03:07+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 3

Round 3 applies all six round 2 findings, and I recommend convergence of this
formulation. Q14 sets out the three Codex complete-input channels with their
costs. The Claude proof uses the transcript tied to the pane's session id. The
Codex recovery Enter needs proof of the complete input-box command. The
generation sentence is now exact, absent and conflicting targets are separate
outcomes with examples, and the rollout waits for every reader of the new
fields.

#### Round 3 checks on the design text for design-specification resume-paused (round 3)

- Lines 158-160, 460-461 and the Q10 note agree: a missing or agent-less
  saved pane is an absent target and a skip; a different live host fails
  classification. This matches the requirement's absent-target and
  conflicting-evidence rules.
- Lines 384-385 match the code: only a newly issued claim advances the
  generation.
- Lines 359-363 and the Q03 note state the all-readers rollout that the strict
  coordination parser requires.
- Lines 193-202 and 314-318 keep exact complete-input proof for both hosts and
  treat prefixes and `Working` only as corroboration.

#### Remaining wording for the round 3 design for design-specification resume-paused (round 3)

Two small edits remain. Neither needs a new question or decision:

1. Claude version before delivery (lines 282-286). The design names a source
   for Codex but none for Claude, while Q06 option A needs one for both hosts.
   The `user`, `assistant` and `system` records of the Claude transcript carry
   `version` (2.1.319 here) and `cwd`. That transcript is the file named by the
   `agent_session_id` TUIOS reports for the pane, so it gives Claude a pane-tied
   version before delivery. I checked only the key names of this reviewer
   session's own transcript.
2. Result channel (lines 367-370). "A complete capture" for Claude and "a
   complete unwrapped screen result" for Codex repeat the premise round 2
   corrected. They should name the session-id-tied transcript for Claude, and
   for Codex the screen under the tested layout profile or the matched
   session file restricted to the result pattern.

As optional polish, the indented notes inside Q06 option A (lines 663-664) and
Q10 option C (lines 782-783) read better in each question's lead text, as the
Q05, Q07 and Q11 notes do.

### Question verdicts for design-specification resume-paused round 3

The fourteen questions are complete and consistent, and I agree with every
proposed answer. No further question is missing. All fourteen await an
explicit user decision; none is recorded.

| Question | Proposed answer | Verdict in round 3 |
| --- | --- | --- |
| Q01 | B | Agree |
| Q02 | C | Agree; complete-input proof stays mandatory |
| Q03 | B | Agree; the rollout note is right |
| Q04 | B | Agree |
| Q05 | A | Agree |
| Q06 | A | Agree; the consequence for Codex is stated |
| Q07 | A | Agree |
| Q08 | A | Agree |
| Q09 | A | Agree |
| Q10 | C | Agree; the absent and conflict classes are right |
| Q11 | A | Agree |
| Q12 | A | Agree |
| Q13 | A | Agree |
| Q14 | B | Agree |

#### Decisions the person should weigh together for design-specification resume-paused (round 3)

Q06 and Q14 interact. With Q06=A and Q14=B, a Codex pane gets its version
before delivery only from a banner still in its scrollback. Without one, the
target fails classification. Lines 476-477 also require both hosts' profiles
to be validated before release. Choosing Q14=C, once hook attribution under
the shared app-server is proved, would supply that evidence. The person should
decide Q06 and Q14 knowing this.

### Convergence evidence for design-specification resume-paused round 3

Covered wording:

#### Claude version source before delivery for design-specification resume-paused (round 3)

After "TUIOS discovery alone supplies no Codex version." (line 284), add:

```md
For Claude, the transcript named by the pane's observed `agent_session_id`
records `version` and `cwd` on its user, assistant and system entries, giving
pane-tied version evidence before delivery once its profile is validated.
```

#### Result channel wording per host for design-specification resume-paused (round 3)

In lines 367-370, replace "observed through the `turn_end` logged form or a
complete capture" with "observed through the `turn_end` logged form or the
session-id-tied transcript". Replace "Codex uses a complete unwrapped screen
result" with:

```md
Codex shows the result on screen, counted only when the tested layout profile
rebuilds it exactly, or reads it from the Q14-matched session file restricted
to the defined result pattern
```

#### Optional note placement for Q06 and Q10 for design-specification resume-paused (round 3)

Move the indented note under Q06 option A (lines 663-664) into the Q06 lead
paragraph that begins "Q14 option B confirms". Move the note under Q10 option C
(lines 782-783) into the Q10 lead text, after its first paragraph.

Convergence rationale:

No further automated review round is needed for this formulation.

- Every round 1 and round 2 finding is applied in the body, the source table,
  the acceptance examples and the question texts.
- The writer's two qualifications, exact complete-command proof and failure on
  a known reassignment, follow the confirmed requirement, and I agree with
  them.
- The fourteen questions are complete, their options are distinct, and the
  proposed answers are consistent with each other and with the 29 confirmed
  requirement decisions.
- What remains is two sentences of wording and an optional note placement.

All fourteen user decisions are outstanding, and Q06 and Q14 should be decided
together. Consolidation remains the person's separate choice; this
recommendation is advisory and authorizes no consolidation, implementation,
staging or commit.

### Writer instructions for design-specification resume-paused round 3

No further automated review round is needed for this formulation.

1. Apply the two covered wording edits, the Claude version sentence and the
   result channel wording, at the next revision. The note placement is
   optional.
2. Keep every `User decision: pending` line unchanged.
3. Present the convergence gate to the person with all fourteen decisions
   outstanding. Point out that Q06 and Q14 interact for Codex version evidence
   before delivery. Consolidation is their separate choice.
4. During consolidation, keep the unvalidated host-profile gates, the
   all-readers rollout and the deferred senv follow-up link in the design,
   plans and validation.
5. This answer authorizes no consolidation, implementation, staging or
   commit.

### Final reviewer decision for design-specification resume-paused round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-10T07:29:50+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: $llm-shared:pause-session and, on resume, do a review of all decisions, migration notes and tuitp compatibility requirements, using $llm-shared:spec-review-requestor on docs/v0.14.0/design.v0.14.0.resume-paused.md: a spec reviewer will be standing by waiting for your request

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-10T07:30:36+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 4)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 4

### Requestor assessment for design-specification resume-paused (round 4)

Review the complete current design, including every confirmed human decision Q01-Q14, against the current draft and the requirement's 29 confirmed decisions. Umbrella is none. The earlier convergence assessed proposed answers before the human discussion; it does not establish convergence of the amended document.

All fourteen design questions have explicit human decisions. Existing options, recommendations, explanations and answers remain intact. My assessment is that the decisions are coherent as a specification with explicit release evidence gates, but the independent review must test their interactions and identify any missing or new questions. Do not silently replace a confirmed human decision with a reviewer preference. Distinguish a necessary new human choice from a wording repair or an implementation validation obligation.

The confirmed choices are Q01=B (JSON-only bulk routing), Q02=C (compact versioned scope marker), Q03=B (durable non-secret receipt/coordination binding and issued generation, with all-readers rollout), Q04=B (leave a proved active exact reviewer alone first, otherwise require the requestor generation to remain current), Q05=A (100-second input action including recovery and a separate 120-second observation for each receiver), Q06=A (pane-tied host/version proof before input), Q07=A (nonblocking per-canonical-checkout OS guard outside the checkout), Q08=A (Windows host markers and available process ancestry), Q09=A (pure read-only validated exchange snapshot), Q10=C (full pane UUID, host, canonical checkout and TUIOS session identity, with conversation id supplementary), Q11=A (revalidate before each protected mutation and preserve truthful completed consumption if claim later stops), Q12=A (accepted/in-progress with completion unconfirmed at deadline absent explicit failure), Q13=A (separate read-only agent-callable receiving validator), and Q14=B (one fresh matching Codex session file plus a pane launch-id prefix followed by Working).

Please examine these remaining proof limits explicitly:

- Q14 session metadata can establish the Codex CLI version only after submission. It cannot satisfy Q06's pre-input version gate by itself. A pane-tied pre-input Codex version source is unvalidated. No hook installation or attribution has been authorized or proved. Both host profiles must be validated before release.
- A submitted session-file record cannot reconstruct unsubmitted input. Exact full input-box proof remains independently necessary before the single recovery Enter. Preserve complete-command matching, fresh attributable evidence and rejection of ambiguous, masked or truncated evidence.
- The legacy routing section is a study of a possible separate explicit pre-use converter, not approved converter/runtime scope. Bulk discovery remains read-only and JSON-only. Never change consumed prompt bytes or rewrite/delete receipts to manufacture eligibility. Manual resume followed by a fresh pause remains available.
- Requirement Q05=A still defers actual senv integration. The human qualification requires tuitp to keep working and resume all eligible sessions. This is a deferred completion condition, not validation already achieved by additive JSON.
- The deferred integration must cover the full selected layout, both hosts, single and paired checkouts, multiple independent sessions, once-only consumption, startup and daemon restoration, clears, same-host restarts, already running sessions through the shared command, TUITP_RESUME=0, and separate native-conversation mode.
- Installed source analysis says apply_layout reads resume information before restoration rewrites metadata; restored panes start as bare shells and agents start afterward. Current resume_plan chooses the first declared pane per host/checkout and schedules the reviewer without takeover proof. Future integration needs one delivery path, preserved pre-start evidence, and post-readiness identity/profile validation with safe reviewer sequencing.
- Prove whether saved pane UUIDs and TUIOS session identity survive restoration. If they change, resolve the lifecycle and review any needed contract amendment before implementation. Neither guessed replacement nor a blanket restored-session skip satisfies the recorded human qualification.

Assess cross-document consistency in docs/v0.14.0/draft.v0.14.0.resume-paused.md and docs/v0.14.0/feature-request.v0.14.0.resume-paused.md as well as the exact reviewed design. Source-only references for the tuitp claims are C:/Users/[redacted]/home_senv/bin/tuitp.py and tuitp_resume.py; do not inspect unrelated private tuitp.list. No senv code change or runtime compatibility test is claimed.

The round 3 covered wording suggestions about Claude version evidence and result channels were applied, along with the optional note placement. No implementation, live delivery, hook installation, staging, commit or consolidation is authorized by this request.

### Change summary for design-specification resume-paused (round 4)

Since round 3, all design questions Q01-Q14 received explicit dated human decisions. The document preserves every question, option, recommendation and answer. Covered round 3 wording edits and note placement were applied.

The design now records JSON-only routing with a separate legacy-conversion study; durable consent/ownership binding and all-readers rollout; exact-reviewer leave-alone ordering; separate action and observation deadlines; pane-bound host/version profile requirements; the checkout execution guard and human-origin checks; the read-only snapshot and receiving validator boundaries; conversation-independent pane identity; mutation-time revalidation; accepted/in-progress observation outcomes; and the selected Codex session-file/pane-prefix acceptance channel.

The draft, requirement and design were amended to retain the deferred senv trigger and tuitp compatibility condition, including full selected-layout coverage, once-only resumption, lifecycle evidence across restoration/restarts/clears, startup ordering, opt-out, native-conversation mode and explicit review before any identity-contract amendment. The migration study protects consumed prompts and receipts. No runtime implementation or converter was added.

### Human guidance and writer response for design-specification resume-paused (round 4)

Human guidance:

$llm-shared:pause-session and, on resume, do a review of all decisions, migration notes and tuitp compatibility requirements, using $llm-shared:spec-review-requestor on docs/v0.14.0/design.v0.14.0.resume-paused.md: a spec reviewer will be standing by waiting for your request

Writer response:

I accepted and applied round 3's two covered wording corrections and optional note placement. The subsequent human discussion selected all fourteen design answers and qualified migration and deferred tuitp compatibility. This replacement review is expressly authorized on resume and asks for a fresh independent assessment of that changed specification.

There is no outstanding disagreement with round 3. Its convergence recommendation predates the recorded decisions and additions. Please assess the complete current document and related context, including impacts on earlier choices and whether any new human questions are required. Keep proof still needed before release explicit; source observations are not completed profile or integration validation.

Preserve confirmed human decisions and question blocks. Necessary substantive repairs may be recommended for the requestor to assess; a recommendation that conflicts with a confirmed choice must identify that conflict. Consolidation remains a separate human gate.

### Reviewer focus for design-specification resume-paused (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-10T07:51:13+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 4

Line numbers refer to the round 4 design (SHA-256 `1ebdee33...e2b`), unless
another document is named.

I assessed the full current design against this request, the requirement's 29
decisions, the draft, and the two named `tuitp` sources (`tuitp_resume.py` in
full, `tuitp.py` lines 189-307). The fourteen design questions now carry
explicit dated user decisions, and I agree with each one. They are coherent
with each other and with the requirement decision table, and the coverage table
at lines 588-596 accounts for all 29 requirement choices. No confirmed design
choice conflicts with a requirement decision.

The amended document is not ready for consolidation yet. The new decisions
interact in three ways that the current text does not settle, and two of those
need a human choice.

#### Receipt schema 3 against the installed tuitp for design-specification resume-paused (round 4)

This concerns Q03=B, the Q10=C qualification and requirement Q05=A. In
`tuitp_resume.py`, `waiting_prompt` (lines 106-115) reads the receipt's
`- Prompt:`, `- SHA-256:` and `- Project root:` lines through the pattern
`^- <name>: *(.*?) *$`. It never reads `Schema`. It raises `ValueError` when
those lines are missing, malformed or name another checkout, and `resume_plan`
then prints "its resume prompt cannot be read" and resumes nothing for that
checkout (lines 139-146).

A receipt stays in place after the next pause. So a receipt whose lines `tuitp`
cannot parse blocks default startup resumption of every later prompt in that
checkout until another resume rewrites it. That would break the user's "make
sure `tuitp` keeps working" qualification in the whole interval before the
deferred senv effort.

The all-readers rule (lines 464-468) makes it circular. Read literally,
`tuitp_resume.py` is a receipt reader outside this delivery, so the marked
route could not be turned on before the senv effort, and that effort only
starts after this delivery is validated.

Both problems go away if schema 3 keeps those three lines in the schema 2
grammar and only adds lines. That is a constraint on this delivery, testable
here with fixtures, not deferred integration work. The design (line 216), the
requirement (lines 503-505) and the draft (lines 236-238) also understate what
the launcher reads: it checks the receipt's `Prompt` basename and
`Project root`, not only its digest.

#### Codex pane proof at later protected writes for design-specification resume-paused (round 4)

This concerns Q11=A, Q13=A and Q14=B. Q13 has the validator prove "the current
pane/input" immediately before each protected write or claim (lines 327-334).
For Codex the pane tie is Q14's displayed command prefix holding the launch id,
followed by `Working` (lines 291-295).

That screen evidence does not last. As the receiver runs its tool calls, the
submitted command scrolls off the visible screen and into older scrollback,
which line 302 excludes. A requestor's claim usually comes many tool calls
after its first validation, so the claim-time check would either fail or
quietly drop the pane tie. The session-file half lasts: the latest typed user
message equals the marked command until new input arrives. The design has to
say what a later validator call re-proves. I propose this as a new question,
Q15.

#### Evidence that a reviewer is already waiting for design-specification resume-paused (round 4)

This concerns requirement Q22=A and design Q04=B. The leave-alone check runs
first (lines 493-495 and 510-514). It applies to "a reviewer already serving or
waiting on that exact exchange ... when current pane and protocol evidence
agree".

A reviewer in `wait-any-request`, its normal state after every answer, is bound
to no single exchange, and the watcher keeps no durable waiter record by
contract. A Claude reviewer shows an idle pane with a background-shell
indicator, which line 514 correctly says is not proof by itself. A Codex
reviewer shows an active turn and gets the Q02 busy skip. A reviewer whose
watcher started before the pause has no counted input after the pause either.

As written, nothing can prove that an idle Claude reviewer is already waiting.
The tool would then type a marked reviewer resume into it. Q22 forbids that
input, and it risks a second watcher in the same session. The design needs to
say what proves this state and what happens when the proof is unavailable. I
propose this as a new question, Q16.

#### Clarifications that need no new choice for design-specification resume-paused (round 4)

1. Codex version evidence before input (Q06=A with Q14=B). The design rightly
   says Q14's `cli_version` comes too late (lines 389-391). It still offers
   "validated hooks under Q14 option C" as a source before delivery (lines
   391-393, and Q06 at lines 763-767). Hooks were the rejected Q14 option, and
   the user chose B partly to avoid mandatory hook setup. Requiring hooks for
   version evidence would bring that setup back for every Codex pane, so it
   needs the user to reopen Q14, not a design sentence. Within the confirmed
   choices the candidate sources are the Codex banner in that pane's
   attributable scrollback and process metadata tied to that pane's own
   process. The requirement says "Support at least Claude and Codex" (line 55),
   and design lines 583-584 forbid shipping one host. So Codex version evidence
   is a release gate. The design should state it as one, with a rule for what
   happens if no candidate source validates. I treat this as an implementation
   validation obligation, not a new question, because the user accepted the
   Q06 consequence explicitly.
2. Exit semantics for Q12=A. Lines 500-502 report a receiver still processing
   at the deadline as accepted with completion unconfirmed, without failing.
   The success row of the exit table (line 542) lists only "reviewer pending
   takeover". Without that entry, an implementer could map the Q12 outcome to
   exit 1.
3. Live pane name against the saved label (Q10=C). `tuitp` renames the panes of
   a restored session to names built from its new id (`tuitp.py` lines
   278-283), and people rename panes as well. The routing target includes a
   pane label (line 125), and delivery selects `session:S name:N` (line 411).
   The design does not say whether `N` is the saved label or the live name of
   the validated UUID, or whether a changed label alone is a conflict. It also
   does not name the `list-agents` field saved as the TUIOS session identity
   (session name or internal id). Lines 156-158 and 249-253 depend on whether
   that field survives restoration.
4. All-readers rollout. Lines 464-468 should name the readers. Current
   `resume-session` (lines 21-38 of that instruction) accepts receipt schemas 1
   and 2 only, and stops on any other receipt. So an older llm-shared install
   used by either host stops instead of resuming a new prompt after a schema 3
   receipt. That is acceptable fail-closed behavior, but the design should
   state it, and state how the marked route is turned on (the same release, no
   separate switch), so the plan does not invent a flag.
5. Platform. Q08's qualification makes Windows the caller-detection platform
   (line 357), while Q07 option A mentions "each supported operating system"
   (line 806). Say whether `resume_paused` supports only Windows in this
   delivery. If it does not, say which caller checks and lock provider apply
   elsewhere.
6. Draft acceptance rules. Draft lines 191-192 still give the original
   acceptance rules, the agent-log `prompt` line for Claude and the command
   then `Working` for Codex, without marking them superseded. The draft already
   marks Q25's supersession at line 150, so the same kind of note fits here.

#### Migration study and deferred integration for design-specification resume-paused (round 4)

The migration study (lines 173-208) stays within Q01=B and requirement Q25. It
is read-only, refuses consumed prompts and rewrites no receipt. One consequence
is missing: a conversion that changes the digest of a consumed prompt would
also make the installed `tuitp` resume it at startup, because `waiting_prompt`
returns the prompt whenever the digests differ. That is a second, concrete
reason for study item 4's refusal.

The deferred `tuitp` coverage text (lines 236-263) matches requirement
checklist lines 526-542 and the draft (lines 244-253). Beyond the receipt
grammar, reader list and draft wording points above, I found no contradiction
among the three documents.

### Question verdicts for design-specification resume-paused round 4

All fourteen questions carry explicit user decisions dated 2026-11-09. I agree
with every decision and would choose the same options. Two new questions are
missing; they come from how the decisions combine, not from disagreement with
any one of them.

| Question | User decision | Verdict in round 4 |
| --- | --- | --- |
| Q01 | B | Agree; the migration study stays outside bulk execution |
| Q02 | C | Agree; complete-input proof stays mandatory |
| Q03 | B | Agree; schema 3 must keep the receipt lines `tuitp` reads |
| Q04 | B | Agree; its leave-alone check needs Q16 |
| Q05 | A | Agree |
| Q06 | A | Agree; Codex version evidence is a stated release gate |
| Q07 | A | Agree; state the platform |
| Q08 | A | Agree; state the platform |
| Q09 | A | Agree |
| Q10 | C | Agree; selector uses the live name of the validated UUID |
| Q11 | A | Agree; later Codex rechecks need Q15 |
| Q12 | A | Agree; add its outcome to the exit success row |
| Q13 | A | Agree; later Codex rechecks need Q15 |
| Q14 | B | Agree; hooks for version would reopen it |

No proposed answer for Q15 or Q16 is a user decision. Both await the user.

#### Proposed Q15: Codex receiving-pane proof at later protected writes for design-specification resume-paused (round 4)

Q13 makes the receiving validator prove the current pane and input before each
protected write or claim. Q14 ties a Codex session file to its pane through the
displayed command prefix holding the launch id, followed by `Working`. That
screen evidence lasts only while the submitted command is still on screen,
while the session file's latest typed user message lasts until new input
arrives. What must later validator calls in the same receiving turn prove?

BBQ: a depot checks a courier at the gate, then checks the same parcel number
at each later door. In this picture: the gate check is the first validation
with the displayed prefix, the parcel number is the matched session file and
launch id, and the later doors are the receipt and claim writes.

- Option A: The first validation proves the full Q14 tie and returns the
  matched session identity and launch id as non-secret evidence. The receiver
  passes them to later calls. Each later call requires the same unique session
  file, its latest typed user message still exactly equal to the marked
  command, the same checkout, and the same live pane UUID, host and TUIOS
  session. It also recomputes the bindings and the exchange snapshot. Any
  change, new typed input or ambiguity stops before the write.
  - Pro: The pane tie is proved once from fresh evidence, and every later check
    uses evidence that lasts through the turn.
  - Con: Later calls depend on values the receiver supplies from its own
    context. A wrong or missing value has to fail closed, and tests must cover
    it.
- Option B: Every call re-proves the displayed prefix and `Working`, accepting
  attributable scrollback that holds this launch id under a tested profile
  rule.
  - Pro: Each call stands alone on screen evidence.
  - Con: It depends on scrollback depth and layout, it needs an exception to
    the rule that older scrollback grants nothing, and a long turn can still
    lose the line.
- Option C: Only the first validation proves pane and input. Later calls
  recheck digest, routing and exchange bindings only.
  - Pro: Simplest validator contract.
  - Con: It drops the pane and input proof at the claim, the write that Q11
    protects most, and leaves Codex weaker than Claude, whose transcript lasts.

Recommended option: A. It keeps Q13's pane and input proof at every protected
write, using evidence that lasts through the turn. It needs no screen
re-reading and no hooks. The pane tie still comes from the fresh launch-id
prefix that Q14 selected, and the carried values hold no capability or
conversation content.

Answer to Q15: option A, proposed and awaiting a user decision.

#### Proposed Q16: Proof that a reviewer is already waiting for design-specification resume-paused (round 4)

Requirement Q22=A leaves a reviewer that is already serving or waiting on the
exact exchange untouched, and design Q04=B runs that check first. A reviewer in
`wait-any-request` waits for any request and leaves no durable protocol record.
In Claude it shows an idle pane with a background watcher. What positive
evidence proves that a reviewer pane is already waiting, and what does the tool
do when that proof is unavailable?

BBQ: a dispatcher must not call a driver who is already parked at the depot
waiting for loads. In this picture: the parked driver is a reviewer in a global
wait, the depot is the artifact home, and the call is the marked reviewer
resume.

- Option A: Prove waiting from that pane's host complete-input channel. The
  latest typed input must be a reviewer `review-resume` in this checkout, with
  no later typed input. The host's waiting evidence must also hold: for Claude,
  a background task from that turn still running; for Codex, an active turn,
  which the Q02 busy skip already protects. When the proof holds, leave the
  reviewer alone. When it is incomplete, send no input and report the reviewer
  as pending, with the reason.
  - Pro: Respects Q22 without a new artifact, and an uncertain reviewer never
    receives input.
  - Con: When the evidence is ambiguous, for example after the watcher stopped
    or other input arrived, the reviewer stays pending until a person resumes
    it. The Claude profile must also define which transcript fields show a
    running background task.
- Option B: Deliver the marked reviewer resume whenever exact-exchange protocol
  evidence shows no current reviewer claim, and rely on the receiving workflow
  to reuse an existing watcher.
  - Pro: Activates the reviewer in more cases.
  - Con: It types into a reviewer that is already waiting, which Q22 forbids,
    and it relies on model behavior to avoid a second watcher.
- Option C: Have `wait-any-request` keep a non-secret waiter record in the
  artifact home while it runs.
  - Pro: Gives protocol evidence for the leave-alone check.
  - Con: It breaks the rule that the watcher keeps no durable waiter record,
    and a hard kill leaves a stale record that can block activation.

Recommended option: A. It follows Q22 and the design's existing rule that
uncertain evidence never permits input, and it adds no durable state. The
pending report keeps the case visible to the person.

Answer to Q16: option A, proposed and awaiting a user decision.

### Requested changes for design-specification resume-paused round 4

Requested changes:

Line numbers refer to the round 4 design unless another document is named.

1. Receipt line grammar, lines 454-456. After "A schema 3 receipt retains
   root/digest/host and adds launch id, pane and assignment binding", add:
   "Schema 3 keeps the schema 2 `- Prompt:`, `- SHA-256:` and `- Project root:`
   lines, with the same `- Name: value` grammar and values, and only adds
   lines. The installed `tuitp` reads those three lines and ignores `Schema`,
   so it keeps reading schema 3 receipts without a senv change." In the
   validation paragraph (lines 571-586), add a fixture test that a schema 3
   receipt satisfies that grammar and that the prompt keeps its first-line
   heading and `- Session role:` line.
2. Launcher source row, line 216. Replace the first sentence with: "Reads the
   prompt heading, the `Session role` line, the exact prompt bytes, and the
   receipt's `Prompt`, `SHA-256` and `Project root` lines. It ignores `Schema`;
   a missing or malformed line stops startup resumption for that checkout."
   Make the same correction in requirement lines 503-505 and draft lines
   236-238.
3. Two meanings of "keeps working", lines 236-243 and the Q10 qualification
   (lines 912-916). Split the qualification. This delivery owns non-regression
   of the installed `tuitp`: prompts keep the heading and `Session role` line,
   receipts keep the three lines, and fixtures validate both. The deferred senv
   effort owns the completion condition "resume all eligible sessions through
   the shared interface". In requirement checklist lines 521-522, keep
   additive-format and receipt validation for the integration, and note that
   the installed launcher's receipt compatibility is a constraint of the
   current delivery.
4. Reader list, lines 464-468. Name the readers that must run the compatible
   version: in every llm-shared install used by either host, the
   `resume-session`, `pause-session`, `status-session` and `list-session`
   instructions, the review exchange tools, the receiving validator and
   `resume_paused`. Add `tuitp_resume.py`, compatible under change 1. State
   that an older `resume-session` stops on a schema 3 receipt, as expected
   fail-closed behavior in a mixed install. State that the marked route ships
   with its readers in one release, with no separate switch.
5. New questions. Add proposed Q15 and Q16 after Q14, in the document's
   question format (BBQ, options, recommended option, answer), using the
   question-verdict text, with no user decision recorded. Reference Q15 from
   the validator paragraph (lines 327-334) and the Codex proof sentences (lines
   291-295). Reference Q16 from the leave-alone paragraph (lines 510-514) and
   Q04's lead-in (lines 703-704).
6. Codex version source, lines 389-398 and Q06 lines 763-767. Remove "for
   example through validated hooks under Q14 option C", or say that using hooks
   for version evidence requires the user to reopen Q14=B. Add: "Within the
   confirmed choices, the candidate Codex sources before input are the version
   banner in that pane's attributable scrollback and process metadata tied to
   that pane's own process. The first implementation step validates one of
   them read-only. If neither validates, the work returns to design review; it
   does not ship one host or add hooks silently." Keep the Q06 decision and
   options unchanged.
7. Exit table, line 542. In the success row, after "reviewer pending takeover",
   add "accepted with completion unconfirmed for any receiver (Q12)".
8. Pane name and session identity, lines 125, 149-153 and 411-415. Add: "The
   saved pane label is supplementary. The delivery selector uses the live name
   observed for the validated UUID right before delivery. A changed label alone
   is reported, not a conflict." Name the `list-agents` field stored as the
   TUIOS session identity, and say whether restoration is expected to keep it.
9. Platform, lines 357-361. Add one sentence: either "`resume_paused` supports
   Windows only in this delivery", or the caller checks and lock provider that
   apply on other platforms.
10. Draft acceptance wording, draft lines 187-192. Add: "The design's
    complete-input proof under Q02 and Q14 replaces the original acceptance
    rules below."
11. Migration study item 4, lines 193-197. After "could make a consumed pause
    look unused", add: "The installed `tuitp` would then also resume it at
    startup."

### Human guidance response for design-specification resume-paused round 4

Human guidance:

$llm-shared:pause-session and, on resume, do a review of all decisions,
migration notes and tuitp compatibility requirements, using
$llm-shared:spec-review-requestor on
docs/v0.14.0/design.v0.14.0.resume-paused.md: a spec reviewer will be standing
by waiting for your request

Guidance response:

The guidance asked for a review of all decisions, the migration notes and the
`tuitp` compatibility requirements. This round covers all three.

- Decisions: all fourteen user decisions are checked against each other, the
  requirement's 29 decisions and the draft. I agree with each one. Their
  combinations leave two choices open, proposed as Q15 and Q16.
- Migration notes: the study stays read-only and outside bulk execution, as
  Q01=B and requirement Q25 require. It needs one added consequence: a digest
  change to a consumed prompt would also make the installed `tuitp` resume it
  at startup.
- `tuitp` compatibility: I checked the two named sources directly. The deferred
  coverage list is consistent across the three documents. One gap belongs to
  the current delivery, not the deferred effort: schema 3 receipts must keep
  the three receipt lines `tuitp` parses, or default startup resumption stops
  in any checkout that used the marked route. Restored panes also get new
  names, so the delivery selector must use the live name of the validated
  UUID.

The guidance grants no consolidation, and I treated it as review focus only.

### Writer instructions for design-specification resume-paused round 4

Apply the eleven requested changes to the design, plus the matching
corrections in the requirement (lines 503-505 and 521-522) and in the draft
(lines 187-192 and 236-238). Keep every Q01-Q14 block, its options,
recommendation, answer and recorded user decision unchanged.

Add Q15 and Q16 as proposed questions. Record their recommendations and answer
text as proposals only, with no user decision. They follow from the confirmed
Q11, Q13, Q14 and requirement Q22 decisions and replace none of them.

None of the requested changes overrides a confirmed choice. Change 6 removes a
sentence that would have brought back the hook setup Q14=B rejected. Using
hooks would need the user to reopen Q14.

Do not claim a validated host profile, live delivery or `tuitp` runtime test.
Change 1's fixture test checks the line grammar `tuitp` reads in this
repository; it does not import or change senv code.

Then publish a replacement request for round 5 that names Q15 and Q16 as new
questions for the user. Consolidation stays a separate human gate.

### Final reviewer decision for design-specification resume-paused round 4

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-4 -->

## Round 5 by requestor

- Recorded: 2026-11-10T07:59:31+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 5)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 5

### Requestor assessment for design-specification resume-paused (round 5)

All fourteen confirmed decisions are preserved. Q15 and Q16 are now appended with options, analogies, recommendations and explicitly proposed answers; both user decisions are pending. They address later Codex pane/input revalidation and positive evidence of an existing reviewer wait. No new answer has been selected for the human. Please assess their completeness, sufficiency and interactions with the confirmed choices, and identify any other missing question.

I accepted all eleven round 4 findings and applied the requested document revisions. The installed tuitp prompt/receipt grammar compatibility is a current-delivery constraint with planned fixture checks, while complete shared-interface integration remains deferred under requirement Q05=A. The current source reader ignores Schema and reads Prompt, SHA-256 and Project root. Schema 3 preserves those lines and their values and adds fields. Older llm-shared readers fail closed as described; compatible readers ship in the same release without a new switch.

The design now states Windows-only delivery, identifies the list-agents session string as the session-name identity, and uses the live pane name for the validated UUID rather than the saved label. Read-only discovery confirmed that field is a string. Expected restoration of a declared session name is not proof; session/UUID survival remains a validation gate and changed identity still requires reviewed integration-contract resolution.

The Codex pre-input version source remains unvalidated. Candidate banner/process evidence must be validated read-only in the first implementation step, with return to design review if neither works; mandatory hooks would require reopening Q14=B. No one-host release is permitted. Exact unsubmitted-input reconstruction remains required for recovery. No runtime profile, fixture execution, live delivery, hook installation or senv integration is claimed by these documentation changes.

Please review the complete design and the matching draft/requirement corrections. Consolidation remains a separate human decision, and Q15/Q16 remain undecided even if their formulation converges.

### Change summary for design-specification resume-paused (round 5)

Applied all eleven round 4 requests:

1. Specified additive schema 3 preservation of the installed launcher's three receipt lines and prompt heading/Session role, with current-delivery fixture validation obligations.
2. Corrected the launcher parsing facts in design, requirement and draft.
3. Separated installed-launcher non-regression now from deferred complete shared-interface integration.
4. Named compatible readers, same-release rollout without a switch, and older resume-session fail-closed behavior.
5. Added proposed Q15/Q16, both pending, and linked their unresolved contracts from the body and Q04.
6. Removed hooks as an assumed pre-input Codex version source; retained read-only candidate validation, the release gate, and explicit return to design review on failure.
7. Added any receiver's accepted/completion-unconfirmed Q12 outcome to the exit-success row.
8. Named the session string identity, live pane-name selector and non-conflicting label changes; retained restoration survival validation.
9. Stated Windows-only delivery.
10. Marked the draft's earlier acceptance rules superseded by Q02/Q14 complete-input proof.
11. Added installed tuitp startup replay as another consumed-digest conversion hazard.

Preserved all Q01-Q14 options, recommendations, answers and human decisions, while amending explanatory lead-ins and the Q10 qualification to clarify the requested constraints. No question was consolidated or removed. The private question companion mirrors the revised question section.

### Writer response for design-specification resume-paused (round 5)

Writer response:

I agree with the round 4 assessment and accepted all eleven requested changes. No disagreement signal applies. Q15 and Q16 are proposed questions for the human, not selected answers; their body references expose the unresolved contracts without silently implementing their recommendations.

The three effort documents now distinguish preserved installed-launcher parsing from deferred shared-interface integration, including receipt grammar and digest replay hazards. The design states compatible reader rollout, Windows scope, live selector naming, the session identity field, Q12 exit semantics and the pre-input version validation gate.

Please assess whether this revised formulation is ready for the human gate with two pending choices. The original Q01-Q14 discussion batch remains intact. No consolidation or implementation is authorized.

### Reviewer focus for design-specification resume-paused (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-11-10T08:06:31+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 5

Line numbers refer to the round 5 design (SHA-256 `83068262...dde34`), unless
another document is named.

I reread the full design and checked the requirement and draft changes. All
eleven round 4 requests are applied as asked:

- receipt grammar and fixtures (lines 478-483 and 614-618);
- launcher facts (line 224, requirement lines 503-511, and the draft);
- the split between current non-regression and the deferred completion
  condition (lines 244-250 and the Q10 qualification at lines 959-965);
- the named readers and same-release rollout (lines 492-502);
- Q15 and Q16, with body references at lines 306-308, 349-351, 549-551 and
  747-748;
- the Codex version-source gate (lines 409-415 and 808-814);
- the Q12 exit row (line 579);
- the session identity field, live selector name and label rule (lines
  129-133, 158 and 436-437);
- Windows-only scope (line 375);
- the draft's supersession note (draft lines 187-188);
- the `tuitp` replay hazard (line 204).

Q01-Q14 keep their options, recommendations, answers and recorded decisions.
The amended lead-ins (Q04, Q06 and the Q10 qualification) clarify and do not
change any choice.

No new question is missing. Q15 and Q16 cover the two gaps from round 4. Their
options are distinct and state their consequences, and the recommendations
follow from confirmed Q11, Q13, Q14 and requirement Q22. One proposed option
needs a precise correction before the user sees it. Q16 option A requires, for
Claude, "a background task from that turn still running". A reviewer restarts
its watcher after every answer, and that restart happens in a turn opened by a
task notification, not in the turn of the typed `review-resume`. A reviewer
that has answered even once would therefore never pass the condition as
written. The condition should name a watcher started after that typed input
and still running in the same session. This is an exact phrase replacement,
given in the covered wording.

The other remaining edits are wording only:

- Several sentences still describe Q14 and Q06 as undecided (lines 54, 303,
  312-313, 407-408 and 416-418).
- Q03's explanatory lead-in (lines 730-731) still says all older readers
  reject the receipt schema, and uses "Enable", while the body now says the
  installed `tuitp` stays compatible.
- "Restoration profile" (lines 131-133) and "its profile" (lines 163-165) name
  no profile the design defines. The covered wording states what the
  restoration text already implies: the bulk command has no separate
  restoration mode, a non-matching saved id is an absent target, and proof that
  ids survive restoration is owed by the deferred integration.
- One requirement checklist item (requirement lines 525-530) reads as if
  pane identities were part of the fixture checks; a parenthesis fixes it.

None of these edits changes a decision, an option or a rule. The design is
consistent with the requirement's 29 decisions and with the draft. It keeps
proof still owed before release explicit: Codex version evidence before input,
both host profiles, the complete-input channels, and `tuitp` integration
coverage.

### Question verdicts for design-specification resume-paused round 5

No question is missing. I agree with all sixteen questions and would choose
the recorded or proposed option for each.

| Question | Status | Verdict in round 5 |
| --- | --- | --- |
| Q01 | Confirmed B | Agree |
| Q02 | Confirmed C | Agree |
| Q03 | Confirmed B | Agree; its lead-in needs the `tuitp` exception |
| Q04 | Confirmed B | Agree |
| Q05 | Confirmed A | Agree |
| Q06 | Confirmed A | Agree; release gate stated |
| Q07 | Confirmed A | Agree |
| Q08 | Confirmed A | Agree |
| Q09 | Confirmed A | Agree |
| Q10 | Confirmed C | Agree |
| Q11 | Confirmed A | Agree |
| Q12 | Confirmed A | Agree |
| Q13 | Confirmed A | Agree |
| Q14 | Confirmed B | Agree; body text still calls it proposed |
| Q15 | Pending, proposed A | Agree; I would choose A |
| Q16 | Pending, proposed A | Agree with A after the watcher-turn correction |

Q15 and Q16 are not user decisions. They are the outstanding human choices for
this formulation.

For Q15, option A keeps the pane and input proof at the receipt and claim
writes, using the session file and live pane identity that last through the
receiving turn. Option C would drop that proof at the claim.

For Q16, option A keeps Q22's leave-alone rule and sends no input to a reviewer
whose state is uncertain. The option text must accept a watcher restarted
after an answer: without that correction, every reviewer that has already
answered once would be reported pending instead of left alone. Option B types
into a waiting reviewer, and option C adds the durable waiter record the
protocol excludes.

### Convergence evidence for design-specification resume-paused round 5

Covered wording:

Line numbers refer to the round 5 design unless another document is named.

1. Q16 option A, line 1165. Replace "for Claude, a background task from that
   turn still running;" with "for Claude, a background watcher started after
   that typed input and still running in the same session, including one
   restarted after an answer;". In the Q16 answer (lines 1183-1186), replace
   "plus current host waiting evidence" with "plus current host waiting
   evidence, such as a watcher restarted after an answer,".
2. Line 54. Replace "Q14 proposes validation of the user-input record channel."
   with "Q14=B selects this user-input record channel; its profile is still to
   be validated."
3. Line 303. Replace "Codex uses Q14's proposed session-file channel:" with
   "Codex uses Q14's selected session-file channel:".
4. Lines 312-313. Replace "Screen reconstruction and mandatory hooks remain
   Q14 alternatives." with "Screen reconstruction and mandatory hooks were the
   Q14 options not selected."
5. Lines 407-408. Replace "Q14's proposed session-file lookup" with "Q14's
   selected session-file lookup".
6. Lines 416-418. Replace "a classification failure under this proposal,
   without input; Q06 exposes this consequence for human decision." with "a
   classification failure under confirmed Q06=A, without input."
7. Q03 lead-in, lines 730-731. Replace both sentences with "Older llm-shared
   readers reject the new coordination fields or receipt schema; the installed
   `tuitp` stays compatible through the preserved receipt lines. The marked
   route ships only with every affected llm-shared reader updated."
8. Lines 131-133. Replace "Restoration is expected to retain the declared
   session name; its actual survival, together with the pane UUID, must be
   proved before that restoration profile is supported." with "The bulk
   command has no separate restoration mode. A saved pane UUID or session name
   that no longer matches a live pane is an absent target and skips; a
   matching one still needs the host and checkout checks. Proving that
   restoration keeps session names and pane UUIDs attached to the same panes
   is evidence the deferred integration owes before it relies on restored
   targets."
9. Lines 163-165. Replace "Whether a restored TUIOS session preserves UUID
   uniqueness must be verified before its profile is supported." with "The
   deferred integration verifies whether restored sessions keep pane UUIDs
   unique and attached to the same panes."
10. Requirement checklist, lines 525-530. Rewrite the first sentence as: "In
    the separate senv effort, validate additive-format and receipt
    compatibility (building on the current delivery's installed-launcher
    grammar constraint and fixture checks), startup and restored pane
    identities, preserved default behavior and resume opt-out, and a single
    delivery path that enforces saved routing and requestor takeover before
    reviewer activation." Wrap it to the file's usual line length.

Convergence rationale:

Every round 4 finding is resolved in the design, the requirement and the
draft. Q01-Q14 are confirmed user decisions, consistent with each other and
with the requirement's 29 decisions, and no confirmed choice was changed. Q15
and Q16 are complete questions with distinct options, stated consequences and
recommendations that follow from confirmed choices. No other question is
missing.

The remaining edits are the ten covered replacements. Nine are wording only.
The Q16 correction is one exact phrase that fixes which watcher counts as
waiting evidence. It changes no option's direction and no decision, and its
text is fully given, so it needs no further automated round.

The reviewed formulation is ready for the human gate. Two choices remain
outstanding for the user: Q15 and Q16, both with proposed option A and no
recorded decision. Convergence is advisory; it does not record those decisions
or authorize consolidation. Proof still owed before release remains explicit
in the design and is not claimed as done.

### Writer instructions for design-specification resume-paused round 5

Apply the ten covered replacements exactly, nine in the design and one in the
requirement checklist. Keep every Q01-Q14 option, recommendation, answer and
recorded user decision unchanged. Keep Q15 and Q16 as pending, with no user
decision recorded. The Q16 correction changes only the Claude watcher
condition in option A and the matching answer phrase.

Then present the convergence gate to the person. Name Q15 and Q16 as the two
outstanding choices, each with proposed option A. If the person wants them
explained first, use the undecided-question explanation flow; any later
decision on them needs a follow-up review of the amended document.
Consolidation stays a separate human choice and is not authorized by this
answer.

### Final reviewer decision for design-specification resume-paused round 5

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-5 -->

## Round 5 by human - human-confirmation

- Recorded: 2026-11-10T09:26:07+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-5 -->

## Round 6 by requestor

- Recorded: 2026-11-10T09:27:44+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 6)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 6

### Requestor assessment for design-specification resume-paused (round 6)

#### Assessment of the confirmed resume-paused decisions for design-specification resume-paused (round 6)

The human discussion is complete. A successful whole-document decision scan
reports 16 questions, all explicitly confirmed, zero undecided and no
diagnostics. Q15=A and Q16=A were explicitly selected on 2026-11-10.

The existing questions, options and answers appear sufficient. No additional
question has been identified by the writer. Independent review must examine
the full specification for missing questions and inconsistencies; the human
choices cannot be overwritten by a reviewer recommendation.

Q15=A retains the initial Q14=B pane/session-file tie and carries only matched
non-secret session identity and launch id. Every later validator call must
independently check the unique file, latest complete typed command, checkout,
live pane UUID/host/TUIOS session and current assignment/exchange bindings.
Missing or wrong carried values, new typed input, changes or ambiguity stop
the protected write. This preserves Q11=A and Q13=A.

Q16=A requires latest reviewer resume input for this checkout, no later typed
input and current host waiting evidence. Claude's running same-session watcher
may have restarted after an answer. Codex active turns remain protected by the
busy skip. Incomplete proof permits no input and produces reviewer-pending
with a reason. This preserves requirement Q22=A and design Q04=B.

All ten precisely covered round 5 wording corrections were applied before
this human discussion: nine in the design and one in the requirement. No
consolidation or implementation has occurred. Runtime host profiles, Codex
pre-input version proof and complete restored-session coverage remain
unvalidated. Deferred shared `tuitp` integration remains a separate effort;
installed heading, Session role and receipt parsing must remain compatible.

### Change summary for design-specification resume-paused (round 6)

#### Changes after resume-paused design convergence for design-specification resume-paused (round 6)

Since round 5 convergence, applied its ten precisely covered wording fixes
(nine design replacements and one requirement replacement), as previously
assessed at that gate. These include permission to recognize Claude's watcher
restarted after an answer. No published transcript was edited by hand.

During the subsequent human discussion, changed only the Q15 and Q16 answer
records in the design. Each now records explicit option A, the decision date,
the complete agreed behavior and rationale. Q15 clarifies rejection of wrong
or missing carried values and retains the independent Q06 pre-input version
gate. Q16 states both host evidence rules and the no-input/pending outcome,
with watcher-profile validation still required.

Preserved Q01-Q14 decisions and every question ID, option, recommendation and
explanation. No new notion introduction was requested in this batch. The
private question mirror and continuation note were refreshed; they are not
protocol coordination. No runtime or senv source changes, consolidation,
staging, commits or pushes occurred.

Current design SHA-256:
`05814d53dac968f30810a198aa7b14b4814d0296461fd3a90c571d64d0c8c7af`.

### Human guidance and writer response for design-specification resume-paused (round 6)

Human guidance:

#### Human choices for the remaining resume-paused questions for design-specification resume-paused (round 6)

For Q15, the user's verbatim reply was:

> A

For Q16, the user's verbatim reply was:

> A

The user's earlier selection of Explain undecided questions authorizes
recording those choices and an independent follow-up review. It does not
authorize consolidation.

Writer response:

#### Writer response on the resume-paused human decisions for design-specification resume-paused (round 6)

Accepted the round 5 convergence assessment and its exactly covered wording
corrections, which are present in the design and requirement. The writer and
reviewer previously agreed on proposed Q15=A and Q16=A; the user has now
explicitly confirmed both after separate explanations.

The replacement round is required by the question-discussion workflow to
review those recorded human decisions, rationale and effects across the full
specification. Please assess all earlier decisions and related draft and
requirement sections, including whether any further question is needed.
Surface conflicts with a human decision explicitly rather than replacing it.

Please check that Q15's later checks retain live input/pane proof and the
original fresh Q14 tie without granting new authorization, and that Q16's
leave-alone proof includes a current watcher restarted after an answer while
uncertainty never permits input. Preserve Q06's independent unvalidated
pre-delivery version gate, the exact requestor takeover requirement, existing
`tuitp` parser compatibility and the separately deferred shared integration.

No independent convergence after these human decisions is claimed yet. No
consolidation has been authorized. The entire question section remains.

### Reviewer focus for design-specification resume-paused (round 6)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-6 -->

## Round 6 by reviewer

- Recorded: 2026-11-10T09:41:50+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 6

Line numbers refer to the round 6 design (SHA-256 `05814d53...c8c7af`),
unless another document is named.

I reread the full design and checked the requirement and draft. The ten
round 5 replacements are applied as covered: nine in the design and the
checklist parenthesis in the requirement (requirement lines 527-533). Q01-Q14
keep their options, recommendations, answers and recorded decisions.

The Q15=A and Q16=A records match the user's choices:

- Q15 (lines 1140-1154) keeps Q14's fresh launch-id prefix for the first pane
  tie. It carries only the matched session identity and launch id, as
  non-secret evidence, and re-proves the unique file, the unchanged latest
  typed command, the checkout and the live pane identity before each
  protected write. A missing or wrong carried value stops the write, so the
  carried values grant no authority. Q06's pre-input version gate stays
  separate.
- Q16 (lines 1189-1205) accepts a Claude watcher restarted after an answer
  and never permits input on incomplete evidence.

One conflict follows from the Q16 decision and needs a new question. Q16=A
has two outcomes: a proved wait leaves the reviewer alone, and incomplete
proof sends no input and reports the reviewer pending. The body (lines
545-549) and requirement Q22=A add a third: a reviewer that is neither serving
nor waiting receives the marked reviewer resume. No evidence is defined for
that branch. A reviewer that is not waiting never passes Q16's proof, so, read
literally, the tool would never activate one: not a fresh or restarted
conversation, not an idle Codex reviewer, and not the former requestor in the
swap example at line 595. That contradicts requirement Q01=D and Q22=A. Q16
option A's con also lists a stopped watcher as a pending case, so the rule
must be chosen explicitly rather than inferred. I propose Q17 with three
options and recommend treating a wait as excluded when the host's own wait
mechanism is proved absent.

The other edits follow from the recorded decisions:

- Four passages still call Q15 or Q16 proposed or pending (lines 308-310,
  351-353, 550-552 and 749-750).
- The exit table's success row (line 580), the acceptance examples (lines
  592-607) and the validation paragraph (lines 620-627) do not yet cover the
  Q15 and Q16 outcomes. Q15 option A's con itself says wrong or missing
  carried values need tests.
- Small leftovers: line 55 still presents hooks as a Q14 alternative, line
  104 calls schema 3 proposed, line 808 calls Q06's consequence proposed,
  Q16 option A's "Q02 busy skip" means requirement Q02 rather than design
  Q02, and lines 131 and 166 exceed the file's usual line length.

The requirement and draft agree with Q15 and Q16. The draft's Q15 and Q16
references are the requirement's own decisions, and the requirement's
leave-alone text (requirement lines 238-244) matches. Proof still owed before
release stays explicit: Codex version evidence before input, both host
profiles, the complete-input channels, the Claude background-task fields and
`tuitp` integration coverage. Because Q17 needs a human decision, this round
requests changes rather than convergence.

### Question verdicts for design-specification resume-paused round 6

Q17 is missing. I agree with Q01-Q16 as recorded and would make the same
choices.

| Question | Status | Verdict in round 6 |
| --- | --- | --- |
| Q01 | Confirmed B | Agree |
| Q02 | Confirmed C | Agree |
| Q03 | Confirmed B | Agree |
| Q04 | Confirmed B | Agree; lead-in still calls Q16 proposed |
| Q05 | Confirmed A | Agree |
| Q06 | Confirmed A | Agree; version gate kept separate from Q15 |
| Q07 | Confirmed A | Agree |
| Q08 | Confirmed A | Agree |
| Q09 | Confirmed A | Agree |
| Q10 | Confirmed C | Agree |
| Q11 | Confirmed A | Agree |
| Q12 | Confirmed A | Agree |
| Q13 | Confirmed A | Agree |
| Q14 | Confirmed B | Agree |
| Q15 | Confirmed A | Agree; body still calls it pending |
| Q16 | Confirmed A | Agree; activation outcome missing, see Q17 |
| Q17 | Missing | Add as proposed; I would choose A |

Q15 keeps live input and pane proof at every protected write. The first tie
still comes from Q14's fresh launch-id prefix followed by `Working`. The
carried session identity and launch id are evidence only: a missing or wrong
value stops the write. This preserves Q11=A, Q13=A and Q06's separate gate.

Q16 keeps requirement Q22's leave-alone rule, accepts a watcher restarted
after an answer, and never permits input on uncertain evidence. It defines
only two outcomes, which is why Q17 is needed. One narrowing is safe and needs
no change: the proof recognizes only a typed `review-resume`. A reviewer
started through the `spec-reviewer` or `code-reviewer` route that later waits
globally is therefore reported pending, or skipped as busy, and never typed
into. If the person wants such a reviewer reported as waiting, Q16 must be
reopened.

Q17 asks when the tool delivers the marked reviewer resume after Q16's proof
fails. I would choose A. A reviewer waits only through its host's own
mechanism: a Claude background watcher, or a Codex attached wait inside an
active turn. Proof that the mechanism is absent excludes a wait whatever the
typed history, so a reviewer that is not waiting is activated as requirement
Q22=A requires, and every uncertain case stays pending under Q16. Option B
would never activate a Codex reviewer, because Q14 ties no session file to a
Codex pane before a marked delivery. Option C contradicts requirement Q01=D
and Q22=A.

### Requested changes for design-specification resume-paused round 6

Requested changes:

Line numbers refer to the round 6 design unless another document is named.

1. New question Q17, after Q16, in the document's question format (lead-in,
   BBQ, options, recommended option, answer), ending with "User decision:
   pending." Use this content:
   - Title: "Q17: Reviewer activation when no wait is running".
   - Lead-in: "Requirement Q22=A leaves a reviewer already serving or waiting
     untouched and otherwise sends its marked reviewer resume. Confirmed
     Q16=A has two outcomes: a proved wait leaves the reviewer alone, and
     incomplete proof sends no input and reports the reviewer pending. A
     reviewer that is not waiting never passes Q16's proof, so without a third
     outcome the tool would never activate a reviewer, including a fresh
     conversation and the swapped pair in the acceptance examples. What
     evidence shows that no wait is running, so that the reviewer receives the
     marked resume?" Add a second paragraph: "A reviewer waits only through
     its host's own mechanism: a Claude background watcher, or a Codex
     attached wait inside an active turn. An active turn is already skipped
     as busy under requirement Q02=A."
   - BBQ: "A dispatcher may call a driver whose bay is empty, but not one who
     might be parked there. In this picture: the parked driver is a waiting
     reviewer, the empty bay is proof that no wait is running, and the call
     is the marked reviewer resume."
   - Option A: "Treat a wait as excluded when current evidence shows that the
     host's wait mechanism is absent. For Claude, the transcript tied to the
     pane's session id shows no background task still running in that
     session, under a validated profile. For Codex, a fresh supported capture
     shows an idle pane with empty input and no active turn. Then deliver the
     marked reviewer resume after takeover proof and the normal eligibility
     checks. A case that is neither Q16's proved wait nor this exclusion is
     incomplete evidence: send no input and report the reviewer pending with
     the reason." Pro: "Activates a reviewer that is not waiting on both
     hosts, as requirement Q22=A and Q01=D require, while any possible wait
     still prevents input." Con: "Q16 option A's con lists a stopped watcher
     as a pending case; under this option an idle Claude pane whose profile
     proves no running task is activated instead. The Claude profile must
     prove that no background task is running, including after a host
     restart."
   - Option B: "Require the option A exclusion and, in addition, proof from
     the pane's complete-input channel that no reviewer entry command was
     typed in its current conversation." Pro: "Keeps Q16 option A's pending
     examples pending: a stopped watcher and input after a reviewer resume."
     Con: "Before a marked delivery, Q14 ties no Codex session file to a
     pane, so the tool would never activate a Codex reviewer. A Claude
     reviewer would be activated only in a fresh or cleared conversation."
   - Option C: "Never deliver after a failed waiting proof. Report the
     reviewer pending and leave its resume to the person." Pro: "The tool
     never types into a reviewer pane." Con: "Contradicts requirement Q22=A,
     which sends the reviewer resume otherwise, and Q01=D's counterpart
     activation. The user would have to reopen those requirement decisions."
   - Recommended option: "Option A: The round 6 reviewer proposes A. A
     reviewer can wait only through its host's own mechanism, so proof that
     the mechanism is absent excludes a wait whatever the typed history. This
     activates a reviewer that is not waiting, as requirement Q22=A requires,
     and Q16's no-input rule still covers every uncertain case. This
     recommendation is not a user decision."
   - Answer: "Option A: Deliver the marked reviewer resume only when current
     evidence excludes a wait: for Claude, no background task still running
     in the pane's session under a validated profile; for Codex, a fresh
     supported idle, empty-input capture with no active turn. Takeover proof
     and the normal eligibility checks still apply. Otherwise follow Q16:
     leave a proved waiting reviewer alone, and report every other case
     pending, with no input."
2. Leave-alone paragraph, lines 545-552. Replace the text from "Before
   activation, leave a reviewer" through "into an uncertain watcher." with:
   "Before activation, apply the leave-alone check. Leave a reviewer already
   serving the exact exchange untouched when current pane and protocol
   evidence agree. Confirmed Q16=A proves a global reviewer wait, which is not
   bound to one exchange, from the pane's complete-input channel and current
   host waiting evidence, and leaves a proved waiting reviewer alone. Q17
   defines the evidence that no wait is running; only then deliver the target
   host's marked `review-resume as reviewer` for the exact selection,
   preserving its conversation and normal claim workflow. Any other case is
   incomplete evidence: send no input and report the reviewer pending with
   the reason. A shell is never a counterpart. A background-shell indicator
   alone is not reviewer proof."
3. Q15 in the body. At lines 308-310, replace "Q15 proposes how later
   protected writes retain this initial pane tie after it scrolls away; that
   answer is not yet a user decision." with "Under confirmed Q15=A, later
   protected writes keep this initial pane tie after the prefix scrolls away:
   they re-prove the same unique session file, its unchanged latest typed
   command and the live pane identity, using the carried session identity and
   launch id." At lines 351-353, replace "Q15 asks what later Codex calls must
   re-prove after the initial displayed prefix is no longer visible. Its
   proposed answer remains pending; do not silently weaken Q11 or Q13 to omit
   later pane/input proof." with "For Codex, confirmed Q15=A defines what
   later calls re-prove after the initial displayed prefix is no longer
   visible. The receiver passes the session identity and launch id from the
   first call; a missing or wrong value stops before the write. Later calls
   keep Q11's and Q13's pane and input proof."
4. Q04 lead-in, lines 749-750. Replace both lines with "Confirmed Q16=A
   separately defines how the leave-alone check proves a global reviewer
   wait, and proposed Q17 when a wait is excluded; neither changes the
   confirmed generation rule."
5. Exit table, line 580. In the success row, after "reviewer pending
   takeover,", add "reviewer pending on incomplete waiting evidence (Q16),".
6. Acceptance examples, after line 600. Add three rows:
   - "A Claude reviewer's watcher, restarted after an answer, still runs after
     its typed `review-resume`" with "Leave it untouched (Q16)."
   - "Reviewer evidence neither proves a wait nor shows that none is running"
     with "Send no input; report the reviewer pending with the reason (Q16)."
   - "Reviewer evidence shows that no wait is running (Q17)" with "Deliver the
     marked reviewer resume after takeover proof and eligibility checks."
7. Validation paragraph, lines 620-627. Add to the listed cases: "a missing or
   wrong carried Codex session identity or launch id, and new typed input
   between protected writes (Q15); a Claude watcher restarted after an
   answer, later typed input after a reviewer resume, a stopped watcher, and
   each leave-alone, pending and activation outcome (Q16, Q17)".
8. Wording only:
   - Line 55: replace "Q14 exposes that alternative." with "hooks were Q14's
     option C, which was not selected."
   - Line 104: replace "the proposed schema 3 marked receipt" with "the new
     schema 3 marked receipt".
   - Line 808: replace "This consequence is proposed explicitly" with "This
     consequence is stated explicitly".
   - Line 1173, Q16 option A: replace "which the Q02 busy skip already
     protects" with "which requirement Q02's busy skip already protects". This
     qualifies a cross-reference and changes no choice.
   - Lines 131 and 166: rewrap to the file's usual line length.

### Human guidance response for design-specification resume-paused round 6

Human guidance:

For Q15, the user's verbatim reply was:

> A

For Q16, the user's verbatim reply was:

> A

The user's earlier selection of Explain undecided questions authorizes
recording those choices and an independent follow-up review. It does not
authorize consolidation.

Guidance response:

The guidance records the user's choices Q15=A and Q16=A and authorizes a
follow-up review, not consolidation. I treated both as explicit decisions and
did not change them.

- Q15: the recorded answer keeps live input and pane proof at every protected
  write and the original fresh Q14 tie for the first proof. The carried values
  are evidence, not authorization: a missing or wrong value stops the write.
- Q16: the recorded answer accepts a current watcher restarted after an
  answer, and uncertainty never permits input.
- The decision leaves one consequence open, which I report as a conflict
  rather than resolving it myself. With only "proved waiting" and
  "incomplete" outcomes, no reviewer would ever be activated, against
  requirement Q22=A's instruction to send the reviewer resume otherwise.
  Proposed Q17 asks the person to choose the activation rule.
- Q06's separate pre-delivery version gate, the exact requestor takeover
  requirement, the installed `tuitp` parser compatibility and the deferred
  shared integration are all preserved.

### Writer instructions for design-specification resume-paused round 6

Apply the eight requested changes. Add Q17 with "User decision: pending." and
keep every Q01-Q16 option, recommendation, answer and recorded user decision
unchanged. The only edit inside a confirmed question is the requirement Q02
qualifier in Q16 option A, which changes no choice.

Q17 needs the person's decision. Present it through the undecided-question
explanation flow, stating that it follows from their Q16=A choice and
requirement Q22=A. Say that option A changes one example in Q16 option A's
con: an idle Claude pane whose profile proves no running task would be
activated instead of reported pending. Then request another review round of
the amended document. No consolidation is authorized.

### Final reviewer decision for design-specification resume-paused round 6

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-6 -->

## Round 7 by requestor

- Recorded: 2026-11-10T09:50:15+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 7)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 7

### Requestor assessment for design-specification resume-paused (round 7)

#### Assessment of the revised reviewer activation design for design-specification resume-paused (round 7)

Round 6 agrees with every recorded Q01-Q16 choice. The writer accepts all
eight requested changes. The full scan now reports 17 questions, Q01-Q16
confirmed, exactly Q17 undecided and no diagnostics. The previously missing
activation question is present, with sufficient options and an explicitly
proposed answer. No further missing question has been identified by the
writer; independent review must assess the entire specification and affected
requirement and draft again.

Q15=A retains the initial Q14=B session-file/pane tie and requires independent
file, latest complete input, live pane and current binding proof before every
protected write. The body now describes this as confirmed. Q16=A leaves a
proved waiting reviewer alone, recognizes a Claude watcher restarted after an
answer and sends no input on incomplete evidence.

Proposed Q17=A defines the separate evidence excluding a wait. For Claude,
the validated session profile must prove no background task remains running,
including after restart. For Codex, supported fresh evidence must prove an
idle pane, empty input and no active turn. Requestor takeover proof and all
normal eligibility checks still precede delivery. This proposal changes the
stopped-watcher example in Q16 option A and requires a human decision.

All round 6 wording suggestions were applied. Existing Q01-Q16 options,
recommendations and decisions are preserved, with only the requested
requirement Q02 cross-reference qualifier changed inside Q16 option A.
Q17 remains pending and outside the fixed Q15-Q16 explanation batch.

No consolidation or implementation has occurred. Codex pre-input version
evidence, host profiles, complete-input channels, Claude background-task
fields and full restored-session coverage remain unvalidated. Installed
`tuitp` parsing compatibility and the separately deferred shared integration
remain required. A convergence recommendation reviews the proposed question
and answer; it does not select Q17 for the person.

### Change summary for design-specification resume-paused (round 7)

#### Changes addressing the eight round 6 requests for design-specification resume-paused (round 7)

1. Appended full Q17 with three options, analogy, recommendation and proposed
   answer ending in `User decision: pending.`
2. Updated reviewer classification to distinguish proved waiting, proposed
   proof of no wait and incomplete evidence, marking Q17 pending.
3. Replaced stale proposed Q15 prose with the confirmed carried-evidence
   behavior and missing/wrong-value protection.
4. Updated Q04 to cite confirmed Q16 and proposed Q17 without changing its
   generation rule.
5. Added reviewer pending on incomplete waiting evidence to the success row.
6. Added restarted-watcher, uncertain-evidence and proposed activation
   acceptance cases, clearly qualifying the pending Q17 case.
7. Added missing/wrong carried values and intervening typed input for Q15,
   plus watcher restart, later input, stopped watcher and all classification
   outcomes for Q16/Q17 to validation coverage.
8. Corrected hook/schema/Q06 status wording, qualified requirement Q02 in
   Q16 option A and rewrapped the two requested passages.

The question companion was refreshed. Requirement, draft and runtime files
were not changed by these round 6 revisions. All earlier question history
and confirmed choices remain present.

### Human guidance and writer response for design-specification resume-paused (round 7)

Human guidance:

#### Human choices for the remaining resume-paused questions for design-specification resume-paused (round 7)

For Q15, the user's verbatim reply was:

> A

For Q16, the user's verbatim reply was:

> A

The user's earlier selection of Explain undecided questions authorizes
recording those choices and an independent follow-up review. It does not
authorize consolidation.

Writer response:

#### Writer response to the round 6 activation finding for design-specification resume-paused (round 7)

All eight findings are accepted; there is no disagreement. Q16 defines proof
of waiting and the no-input rule for uncertainty, but did not define the
separate activation outcome required by requirement Q22=A and Q01=D. Q17 now
asks for that decision explicitly rather than silently changing Q16.

The writer agrees with proposed A. Proof that the host waiting mechanism is
absent supports activation while any remaining uncertainty prevents input.
The changed stopped-watcher example is stated in option A's con. This is
only a recommendation: Q17 remains pending.

The existing explanation batch is fixed at Q15-Q16, both explicitly answered
A. The canonical explanation workflow requires finishing its automated
follow-up review before a new discussion batch is selected at convergence.
Accordingly, please assess the complete revised design, all existing choices,
the proposed Q17 options and answer, related effort documents and any missing
questions. Any convergence will retain Q17 pending and offer the person the
explanation flow; it will not authorize consolidation or infer a choice.

Runtime evidence limitations remain explicit. No validated host profile,
pre-input Codex version proof or complete integration coverage is claimed.

### Reviewer focus for design-specification resume-paused (round 7)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-7 -->

## Round 7 by reviewer

- Recorded: 2026-11-10T09:59:08+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 7

Line numbers refer to the round 7 design (SHA-256 `9586c508...bbe902`),
unless another document is named.

I reread the full design. The requirement and draft are unchanged since
round 6, as the request states. All eight round 6 requests are applied as
asked:

- Q17 follows Q16 (lines 1224-1277), with its lead-in, analogy, three
  options, recommendation, proposed answer and "User decision: pending."
- The leave-alone paragraph now has three outcomes (lines 551-561).
- The confirmed Q15 behavior replaces the stale text (lines 311-315 and
  356-359).
- The Q04 lead-in (lines 765-767), the exit success row (line 589), three
  acceptance rows (lines 610-612) and the Q15, Q16 and Q17 validation cases
  (lines 638-642) are updated.
- The wording fixes at lines 55, 104 and 825 and in Q16 option A are applied,
  and lines 131-137 and 167-170 are rewrapped.

Q01-Q16 keep their options, recommendations, answers and recorded decisions.
The only edit inside a confirmed question is the requirement Q02 qualifier in
Q16 option A, which changes no choice.

Q17 is complete and consistent. Its options are distinct and state their
consequences, including option A's effect on the stopped-watcher example in
Q16 option A's con. The recommendation follows from requirement Q01=D and
Q22=A and from confirmed Q16=A. Option A also keeps Q04's rule: activation
still needs the marked requestor claim generation to be current, so after
later protocol progress a later run does not activate the reviewer again.
The proposed answer is not recorded as a decision.

I checked Q17 against the later-continuation paragraph (lines 563-569),
which never resends an uncertain prior reviewer delivery. Q17 option A's
stopped-watcher case can follow the tool's own earlier delivery, so the
option and its answer should name that rule next to the eligibility checks.
This is a one-phrase clarification of a rule the body already states, not a
new behavior.

The remaining edits are wording only: the target flow (line 77) still shows
two reviewer outcomes, one acceptance row (line 609) still speaks of waiting
on the selected exchange, and two passages exceed the file's usual line
length. No question is missing. Proof still owed before release stays
explicit: Codex version evidence before input, both host profiles, the
complete-input channels, the Claude background-task fields and `tuitp`
integration coverage.

### Question verdicts for design-specification resume-paused round 7

No question is missing. I agree with all seventeen questions and would
choose the recorded or proposed option for each.

| Question | Status | Verdict in round 7 |
| --- | --- | --- |
| Q01 | Confirmed B | Agree |
| Q02 | Confirmed C | Agree |
| Q03 | Confirmed B | Agree |
| Q04 | Confirmed B | Agree |
| Q05 | Confirmed A | Agree |
| Q06 | Confirmed A | Agree |
| Q07 | Confirmed A | Agree |
| Q08 | Confirmed A | Agree |
| Q09 | Confirmed A | Agree |
| Q10 | Confirmed C | Agree |
| Q11 | Confirmed A | Agree |
| Q12 | Confirmed A | Agree |
| Q13 | Confirmed A | Agree |
| Q14 | Confirmed B | Agree |
| Q15 | Confirmed A | Agree |
| Q16 | Confirmed A | Agree |
| Q17 | Pending, proposed A | Agree; I would choose A |

Q17 is the only outstanding human choice. I would choose A: a reviewer waits
only through its host's own mechanism, so proof that the mechanism is absent
excludes a wait, and requirement Q22=A then requires the reviewer resume.
Every uncertain case stays pending under Q16. Option B would never activate
a Codex reviewer, and option C contradicts requirement Q01=D and Q22=A. The
covered wording adds the later-continuation rule to option A and its answer;
it does not change the option's direction.

### Convergence evidence for design-specification resume-paused round 7

Covered wording:

Line numbers refer to the round 7 design.

1. Target flow, line 77. Replace "-> leave active reviewer alone, or deliver
   marked reviewer resume" with "-> leave a serving or waiting reviewer alone,
   deliver marked reviewer resume when no wait is running, or report the
   reviewer pending", keeping the line's indentation.
2. Acceptance examples, line 609. Replace "Reviewer is already waiting on the
   selected exchange" with "Reviewer already serves the selected exchange".
   Row 610 covers the global wait.
3. Q17 option A, line 1248. Replace "Then deliver the marked reviewer resume
   after takeover proof and the normal eligibility checks." with "Then
   deliver the marked reviewer resume after takeover proof, the normal
   eligibility checks and the later-continuation rules, which never resend an
   uncertain prior reviewer delivery." In the Q17 answer (line 1273), replace
   "Takeover proof and the normal eligibility checks still apply." with
   "Takeover proof, the normal eligibility checks and the later-continuation
   rules still apply; an uncertain prior reviewer delivery is diagnosed, not
   resent."
4. Rewrap lines 423-427 and 513-516 to the file's usual line length.

Convergence rationale:

Every round 6 finding is resolved in the design; the requirement and draft
needed no change. Q01-Q16 are confirmed user decisions, consistent with each
other and with the requirement's 29 decisions, and none was changed. Q17 is a
complete question with distinct options, stated consequences and a
recommendation that follows from confirmed choices. No other question is
missing.

The remaining edits are the four covered replacements. Three are wording
only. The Q17 clarification places a rule the body already states, that an
uncertain prior reviewer delivery is never resent, next to the activation
step. It changes no option's direction and no decision, and its text is fully
given, so it needs no further automated round.

The reviewed formulation is ready for the human gate. One choice remains
outstanding for the user: Q17, with proposed option A and no recorded
decision. Convergence is advisory; it does not record that decision or
authorize consolidation. Proof still owed before release remains explicit in
the design and is not claimed as done.

### Human guidance response for design-specification resume-paused round 7

Human guidance:

For Q15, the user's verbatim reply was:

> A

For Q16, the user's verbatim reply was:

> A

The user's earlier selection of Explain undecided questions authorizes
recording those choices and an independent follow-up review. It does not
authorize consolidation.

Guidance response:

The guidance is unchanged from round 6. It records Q15=A and Q16=A and
authorizes a follow-up review, not consolidation. Both decisions are
preserved, and the body now describes them as confirmed.

The Q16 consequence reported in round 6 is now asked as Q17, rather than
resolved by the writer or the reviewer. Q17 stays pending for the person, and
this round's convergence does not select it. I treated the guidance as review
focus only.

### Writer instructions for design-specification resume-paused round 7

Apply the four covered replacements exactly, all in the design. Keep every
Q01-Q16 option, recommendation, answer and recorded user decision unchanged.
Keep Q17 pending, with no user decision recorded; the Q17 edit changes only
one sentence in option A and the matching answer sentence.

Then present the convergence gate to the person. Name Q17 as the one
outstanding choice, with proposed option A, and offer the undecided-question
explanation flow; a later decision on it needs a follow-up review of the
amended document. Consolidation stays a separate human choice and is not
authorized by this answer.

### Final reviewer decision for design-specification resume-paused round 7

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-7 -->

## Round 7 by human - human-confirmation

- Recorded: 2026-11-10T10:25:27+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: # Human guidance for the Q17 follow-up review

At the round 7 human gate, the user selected Explain undecided questions by
replying:

> 1

After the full Q17 explanation, the native picker returned this exact choice:

> A: Prove no wait (Recommended)

The explanation explicitly stated that A changes Q16's stopped-watcher
example: an idle Claude pane whose validated evidence proves no running
background task can be activated. Uncertain evidence still permits no input;
all takeover, eligibility and no-resend rules still apply.

The explanation workflow selection authorizes recording that decision and a
follow-up independent review. It does not authorize consolidation.

<!-- review-entry-id: human-confirmation-round-7 -->

## Round 8 by requestor

- Recorded: 2026-11-10T10:25:45+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification resume-paused (round 8)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/design.v0.14.0.resume-paused.md
Review round: 8

### Requestor assessment for design-specification resume-paused (round 8)

#### Assessment of the confirmed Q17 activation rule for design-specification resume-paused (round 8)

The whole-document scan reports 17 questions, all explicitly confirmed,
zero undecided and no diagnostics. The user selected Q17=A in the native
picker after the full explanation, including the changed stopped-watcher
example, on 2026-11-10. All question blocks, options and historical
recommendations remain present. No further missing question has been
identified by the writer; independent review must assess the full design and
affected requirement and draft for consistency and new questions.

Q17=A permits activation only when current evidence excludes the host wait
mechanism: a validated Claude session transcript proves no background task
remains running, including after restart; a fresh supported Codex capture
proves idle, empty input and no active turn. Takeover proof, normal eligibility
and later-continuation rules remain required. An uncertain prior reviewer
delivery is diagnosed and never resent. A proved wait stays untouched;
uncertain evidence sends no input and reports reviewer pending.

The recorded rationale explicitly changes Q16 option A's stopped-watcher
example: a validated proof of no running task allows activation rather than
pending. It does not treat a missing indicator as absence proof. Q16's
historical options and confirmed answer are preserved. Q04's current marked
requestor claim generation and all input protections still apply.

All four covered round 7 wording changes were applied before the discussion.
The body, acceptance row and Q04 status reference now identify Q17 as
confirmed. Host profiles, Claude absence evidence after restart, complete-input
channels, Codex pre-input version evidence and full restored-session coverage
remain unvalidated. This is a design decision, not implementation evidence.
Installed `tuitp` compatibility and its separate deferred integration remain
required. Consolidation is not authorized.

### Change summary for design-specification resume-paused (round 8)

#### Changes since the round 7 convergence recommendation for design-specification resume-paused (round 8)

Applied the four exactly covered round 7 wording corrections: the target
flow's three reviewer outcomes, serving-exact-exchange acceptance wording,
the no-resend rule next to Q17 option A and its proposed answer, and the two
requested paragraph rewraps. Covered-edits SHA-256 was
`90d136178511709e6f946b01956097d5e136591ff7c6d86dc71acc2df5b55518`.

After the user selected Explain undecided questions, explained Q17 in a new
fixed batch and recorded the explicit Q17=A choice. Its answer now contains
the confirmed rule, decision date, exact native selection, rationale,
changed stopped-watcher example and unvalidated-profile qualification.

Updated the activation body, acceptance row and Q04 status cross-reference
to confirmed Q17=A. Preserved all question IDs, options, recommendations and
earlier decisions. Refreshed the question companion and private continuation.
No notion introduction was requested; requirement, draft and runtime files
were unchanged during this discussion.

Post-decision design SHA-256:
`4bfd994af5a7e285876cab5b6f1b505bea73c5f67c7f42f9f96d826da3f90df2`.

### Human guidance and writer response for design-specification resume-paused (round 8)

Human guidance:

#### Human guidance for the Q17 follow-up review for design-specification resume-paused (round 8)

At the round 7 human gate, the user selected Explain undecided questions by
replying:

> 1

After the full Q17 explanation, the native picker returned this exact choice:

> A: Prove no wait (Recommended)

The explanation explicitly stated that A changes Q16's stopped-watcher
example: an idle Claude pane whose validated evidence proves no running
background task can be activated. Uncertain evidence still permits no input;
all takeover, eligibility and no-resend rules still apply.

The explanation workflow selection authorizes recording that decision and a
follow-up independent review. It does not authorize consolidation.

Writer response:

#### Writer request for review of the Q17 human decision for design-specification resume-paused (round 8)

The user explicitly selected A after the explanation and its warning that
validated no-task evidence changes the stopped-watcher example from Q16.
The writer recorded that choice without changing the earlier questions'
options, recommendations or decisions. There is no disagreement with round 7.

Please review the entire design, related requirement and draft, effects on
earlier decisions and any missing or new question. In particular, check the
three-way reviewer classification, Q04's current takeover generation,
requirement Q22=A/Q01=D activation, Q16 uncertainty protection and the ban on
resending uncertain prior reviewer delivery. The previous convergence did
not review the subsequent human decision and its rationale.

The discussion selection authorizes this follow-up independent review, not
consolidation. Keep Q01-Q17 options and explicit human choices intact. Surface
any conflict rather than replacing a choice. Runtime evidence limitations
remain explicit; no host profile or integration validation is claimed.

### Reviewer focus for design-specification resume-paused (round 8)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-8 -->

## Round 8 by reviewer

- Recorded: 2026-11-10T10:31:31+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification resume-paused round 8

Line numbers refer to the round 8 design (SHA-256 `4bfd994a...3f90df2`),
unless another document is named.

I reread the design. The requirement and draft are unchanged since round 6,
as the request states. The four round 7 replacements are applied as covered:
the target flow's three reviewer outcomes (line 77), the serving-exchange
acceptance row (line 611), the no-resend rule in Q17 option A and its answer
(lines 1250 and 1275-1277), and the two rewrapped passages (lines 423-427 and
513-520).

The Q17=A record (lines 1269-1290) matches the user's choice and the option
they were shown. It keeps option A's three conditions: proof that the host's
wait mechanism is absent, takeover proof with the normal eligibility checks,
and the later-continuation rules that never resend an uncertain prior
reviewer delivery. Its rationale states the changed stopped-watcher example
and says that missing or ambiguous evidence still sends no input.

I checked the decision against the rest of the design and found no conflict:

- Three-way classification: the activation paragraph (lines 552-563), the
  target flow and acceptance rows 611-614 give the same three outcomes. A
  proved wait is left alone, proved absence of a wait is activated, and every
  other case is pending with no input.
- Q04=B: activation still needs the marked requestor claim generation to be
  current (lines 535-537), and the Q04 lead-in (lines 767-769) cites Q17 as
  confirmed without changing the generation rule.
- Requirement Q22=A and Q01=D: a reviewer that is not waiting now receives
  the marked resume, as both require.
- Q16=A: its options, answer and decision are unchanged. Q17 changes only
  the stopped-watcher example, and only when validated evidence proves that
  no task is running.
- No resend: the continuation paragraph (line 571), Q17's answer and
  acceptance row 614 agree.

All seventeen questions carry explicit user decisions, and no question is
missing. The only remaining edits are three short lines left by earlier
rewraps. Proof still owed before release stays explicit: both host profiles,
the Claude evidence that no task is running (including after restart), the
complete-input channels, Codex version evidence before input and `tuitp`
integration coverage.

### Question verdicts for design-specification resume-paused round 8

No question is missing. All seventeen questions carry explicit user
decisions, and I agree with each one.

| Question | Status | Verdict in round 8 |
| --- | --- | --- |
| Q01 | Confirmed B | Agree |
| Q02 | Confirmed C | Agree |
| Q03 | Confirmed B | Agree |
| Q04 | Confirmed B | Agree |
| Q05 | Confirmed A | Agree |
| Q06 | Confirmed A | Agree |
| Q07 | Confirmed A | Agree |
| Q08 | Confirmed A | Agree |
| Q09 | Confirmed A | Agree |
| Q10 | Confirmed C | Agree |
| Q11 | Confirmed A | Agree |
| Q12 | Confirmed A | Agree |
| Q13 | Confirmed A | Agree |
| Q14 | Confirmed B | Agree |
| Q15 | Confirmed A | Agree |
| Q16 | Confirmed A | Agree |
| Q17 | Confirmed A | Agree |

Q17=A is the choice I would make. It activates a reviewer only when
validated evidence shows that the host's wait mechanism is absent, keeps
Q16's no-input rule for every uncertain case, keeps Q04's current-generation
rule, and never resends an uncertain prior reviewer delivery.

### Convergence evidence for design-specification resume-paused round 8

Covered wording:

Line numbers refer to the round 8 design.

1. Lines 131-137. Rewrap the paragraph so that "restoration mode. A saved pane
   UUID or" no longer ends a short line. The text stays unchanged.
2. Lines 516-520. Rewrap the sentence so that "from the Q14-matched" no
   longer stands as a short line. The text stays unchanged.
3. Lines 1271-1272. Rewrap the Q17 answer's first sentence so that "Option A,
   confirmed by the user: deliver the marked reviewer" fills the line. The
   text stays unchanged.

Convergence rationale:

Every round 7 replacement is applied, and the requirement and draft needed no
change. Q01-Q17 are explicit user decisions, consistent with each other and
with the requirement's 29 decisions. The recorded Q17=A matches the option
the user selected. It changes only the stopped-watcher example of Q16, as its
explanation stated, and keeps Q04's generation rule, Q16's no-input rule and
the no-resend rule. No question is missing.

The remaining edits are three rewraps that change no text. The reviewed
formulation is ready for the human gate, with no outstanding question
decision. Convergence is advisory; consolidation stays a separate human
choice that this answer does not authorize. Proof still owed before release
remains explicit in the design and is not claimed as done.

### Human guidance response for design-specification resume-paused round 8

Human guidance:

At the round 7 human gate, the user selected Explain undecided questions by
replying:

> 1

After the full Q17 explanation, the native picker returned this exact choice:

> A: Prove no wait (Recommended)

The explanation explicitly stated that A changes Q16's stopped-watcher
example: an idle Claude pane whose validated evidence proves no running
background task can be activated. Uncertain evidence still permits no input;
all takeover, eligibility and no-resend rules still apply.

The explanation workflow selection authorizes recording that decision and a
follow-up independent review. It does not authorize consolidation.

Guidance response:

The guidance records the user's explicit Q17=A choice and authorizes a
follow-up review, not consolidation. I treated Q17=A as a user decision and
did not change it.

The recorded answer matches what the explanation told the user. It changes
Q16's stopped-watcher example only when validated evidence proves that no
background task is running. Uncertain evidence still sends no input, and the
takeover, eligibility and no-resend rules still apply. I found no conflict
between this decision and the rest of the design, the requirement or the
draft.

### Writer instructions for design-specification resume-paused round 8

Apply the three rewraps without changing any text. Keep every Q01-Q17
option, recommendation, answer and recorded user decision unchanged.

Then present the convergence gate to the person. No question decision
remains outstanding. Consolidation stays a separate human choice and is not
authorized by this answer.

### Final reviewer decision for design-specification resume-paused round 8

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-8 -->

## Round 8 by human - human-confirmation

- Recorded: 2026-11-10T10:46:41+01:00
- Exchange: specification/design-specification/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/design.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-8 -->
