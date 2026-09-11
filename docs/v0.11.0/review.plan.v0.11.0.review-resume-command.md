# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/review-resume-command
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-01T19:32:30+02:00
- Exchange: specification/plan/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for plan review-resume-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
Review round: 1

### Requestor assessment for plan review-resume-command (round 1)

The plan implements the settled design in seven dependency-ordered slices and
keeps the ownership capability change separate from artifact migration, as the
design reviewer requested. It names production and test files, tests-first
work, command gates, line baselines, risk-band extraction, acceptance rollout,
and a matching empty validation skeleton for Steps 0 through 6.

Six implementation questions remain open. They cover ownership-secret transport,
the notification dependency, provider-hint metadata, journal encoding, support
operation names, and shared test builders. Each question has distinct options
and a recommended answer. I found no missing design or requirement question and
no step mismatch between the plan and validation skeleton. There are no earlier
plan-review wording suggestions in round 1.

### Change summary for plan review-resume-command (round 1)

Round 1 introduces the implementation plan and validation skeleton for review
resumption. The plan sequences performance guards, artifact placement and
migration, LLM nature, uniform ownership fencing, status schema 2, role-specific
resume behavior, and final cross-workflow acceptance.

It records current file sizes, mandatory extraction from risk-band store and CLI
modules, focused unit and property tests, final acceptance fixtures, file-based
IO bounds, and six open implementation questions. Matching IO clarifications
were added to the active requirement and settled design without changing their
scope or choices.

### Writer response for plan review-resume-command (round 1)

Writer response: Please independently assess whether the seven steps can implement the settled
requirement and design without inventing a later structural choice. Check the
file lists, step ordering, tests-first coverage, line-budget splits, validation
skeleton alignment, and six implementation questions. Please focus especially
on whether standard-input token transport and explicit shared support operations
are practical through the existing batch launcher.

### Reviewer focus for plan review-resume-command (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-01T19:37:31+02:00
- Exchange: specification/plan/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for plan review-resume-command round 1

Round 1 assesses the implementation plan and its validation skeleton against the
consolidated design. The plan sequences seven steps that match the design's
services, keeps the ownership fence in its own step as the design review asked,
names production and test files per step, records line baselines with mandatory
extraction for the two risk-band modules, and pairs each step with a validation
section. Steps 0 through 6 appear in both documents with the same titles, so the
skeleton alignment the requestor claims holds.

The six questions are well formed and each carries three distinct options with a
reasoned recommendation. I agree with five of them: Q02, Q03, Q04, Q05, and Q06.

Both points the writer asked me to focus on were checked against the shipped
code rather than reasoned about abstractly.

Explicit shared operations are practical. `bin/review_exchange.bat` ends with
`"%PYTHON_EXE%" "...\review_exchange_cli.py" %*`, and the CLI dispatches from a
name-to-handler mapping, so five added operations need a parser entry and a
handler each, with no launcher change. Q05's option A is the right call, and the
plan already protects the risk-band file by extracting ownership dispatch in
Step 3 and resume dispatch in Step 5.

Standard-input transport is where the plan has a real problem, and it is the one
finding that blocks this round. Q01 chooses standard input for the secret on the
grounds that it "stays out of process arguments, environment snapshots,
coordination, and files". The launcher passes standard input through, so the
mechanism works at the process level. The difficulty is the caller. The session
holding the secret is an LLM that drives these launchers by composing one
command string per invocation, so it can reach standard input only by embedding
the secret in that string, which places it in the shell process arguments, or by
redirecting from a file, which creates the durable copy the design forbids.
Neither path delivers option A's stated benefit, and the option's own con
mentions only the two-stage call, not this.

Underneath that is an unstated threat model, and naming it resolves the question
quickly. The design fences a displaced session: another LLM session on the same
machine with repository access. That adversary can read any file in the
repository, which is why a file transport is genuinely unsafe, and why the
plaintext coordination token was rejected in the design round. It cannot read
another session's process arguments after the fact, nor that session's context.
Under that model command-line transport is adequate and file transport is not,
which inverts part of Q01's current ranking.

The second finding is bookkeeping rather than behavior. Several steps repeat the
original baseline line counts for files that an earlier step already mandates
changing, so a later step's "before" value is stale by construction.

Everything else in the plan reads as implementable: the tests-first lists name
concrete boundary cases including crash points and the proof that no rendering
or transcript ever carries the secret, the extraction targets for the store and
CLI are mandatory rather than advisory, and Q02's premise that `watchdog` is
already represented in the repository lock is correct, at `uv.lock:561`.

### Question verdicts for plan review-resume-command round 1

**Q01, ownership secret transport.** I do not accept option A as written, and my
answer differs from the plan's. The question is right to ask, and its three
options are the right three, but it decides between them without stating what
the secret is being protected from, and the winner it picks cannot be reached by
the caller that actually runs these commands.

- The mechanism works; the caller cannot use it. `bin/review_exchange.bat`
  forwards `%*` to the CLI and inherits standard input, so a piped secret would
  reach Python. The session holding the secret is an LLM that composes one
  command string per invocation. To feed standard input it must either put the
  secret in that string, which lands it in the shell's process arguments and in
  its own tool log, or redirect from a file, which is the durable copy the
  design forbids. Option A's pro therefore does not hold in the environment this
  plan ships into, and its con lists only the two-stage call.
- The threat model settles it. The design fences a displaced LLM session with
  repository access. That adversary reads any repository file, which is exactly
  why the design rejected a plaintext token in coordination and why a token file
  would be no better. It does not read another session's process arguments after
  that process exits, and it cannot read the winning session's context. Under
  that model, option C is adequate and a file is not.
- My answer is option C, a generation flag and a token flag, with the threat
  model stated in the question so the choice is legible: the fence protects
  against a displaced session with repository access, not against a hostile
  local user enumerating live process arguments. If the writer wants to defend
  against local process inspection too, then option A stays, but the plan must
  then name the exact caller-side shape that reaches standard input without a
  command string or a file, and I do not believe one exists with the current
  launcher and tooling.

**Q02, directory notifications.** Option A, and I would answer the same. The
premise is verifiable: `watchdog` is already in `uv.lock` at line 561, so
declaring it direct adds no new supply-chain surface. Wrapping it behind a
narrow adapter with polling retained as the correctness fallback matches the
design, which already treats events as hints and the rescan as truth.

**Q03, provider hint metadata.** Option A, and I would answer the same. The
adapter rule permits discovery metadata while forbidding copied workflow
content, so a validated enum in metadata is the one place a trusted hint can
live without thickening the adapter. It also gives Gemini a hint without
inventing an environment variable that no host actually sets.

**Q04, migration journal format.** Option A, and I would answer the same. The
artifact count is bounded, so one atomically replaced strict JSON snapshot gives
recovery a single validated state instead of a replay log to reconcile, and it
matches the all-or-none property the design already requires.

**Q05, shared support operations.** Option A, and I would answer the same. I
checked the practicality the writer asked about: the launcher forwards `%*` and
the CLI dispatches from a name-to-handler mapping, so each new operation is a
parser entry plus a handler and inherits the existing JSON, exit-code, root, and
locking conventions. Option C would create a second protocol surface next to the
resume command the requirement forbids, and option B would hide five contracts
behind one action string.

**Q06, shared test builders.** Option A, and I would answer the same. The
cross-cutting schema and path defaults need one maintained source, and the con
of option C is concrete in this repository, where several test modules already
sit near the ceiling.

**No missing question.** The six cover transport, the notification dependency,
the hint carrier, the journal, the command surface, and test setup, which are
the implementation choices the design deliberately left open. The amendments I
request do not open a seventh.

### Requested changes for plan review-resume-command round 1

Requested changes: apply two changes to
`docs/v0.11.0/plan.v0.11.0.review-resume-command.md`.

1. State the threat model in Q01 and revisit its answer. Add to the question
   description:

   > The fence protects against a displaced LLM session with repository access,
   > which is the adversary the design's ownership generation exists to reject.
   > That session reads any repository file but not another session's process
   > arguments or context. Transport must therefore avoid a durable copy; it
   > need not defend against a local user inspecting live process arguments.

   Then either replace the answer with option C:

   > Option C: Accept generation and token flags. Under the stated threat model
   > a displaced session cannot recover a secret from another session's process
   > arguments, while any file or environment copy is reachable. Flags keep the
   > mutating commands single-call, replayable in tests, and free of a second
   > durable copy.

   or keep option A and add the caller-side shape that makes it reachable, since
   the LLM session composes one command string per invocation and can otherwise
   reach standard input only through that string or a file. Correct option A's
   con either way: it currently lists the two-stage call but not the exposure
   the caller reintroduces.

   Step 3's tests-first list should follow the chosen transport. It currently
   says "missing capability" without naming the transport-specific cases, and
   whichever option wins needs its own malformed-input case.

2. Reference each earlier step's recorded final count instead of repeating the
   original baseline, which is the convention this repository's plans already
   use ("before the recorded Step 1 final count"). Step 5 states "CLI: before
   558" although Step 3 makes 540 or less mandatory for the same file, "CLI
   parser: before 132" although Step 3 expects 190 or less, and "Wait module:
   before 209" although Step 3 expects 290 or less. The shared checklist asks
   for a line count before edits compared against the recorded baseline, so a
   stale baseline produces a false variance reading at exactly the step where
   the risk-band file matters most. Check Steps 2, 4, and 6 for the same
   pattern while making this pass.

Nothing else is requested. Q02 through Q06 need no change, the seven steps match
the validation skeleton, and the extraction targets for the two risk-band
modules are correctly marked mandatory rather than advisory.

### Writer instructions for plan review-resume-command round 1

Apply the two requested changes and publish round 2. Do not consolidate: Q01's
answer may change, which is more than a wording pass.

Order of work:

1. Write the threat model into Q01 first. The answer follows from it almost
   mechanically, and without it the three options cannot be compared, because
   each protects against a different adversary.
2. Choose the transport. If you keep option A, the plan must name the exact
   caller-side shape an LLM session uses to reach standard input without putting
   the secret in a command string or a file. I could not construct one with the
   current launcher and tool surfaces, so if you can, name it in the answer; if
   you cannot, option C is the honest choice and the threat model justifies it.
3. Align Step 3's tests-first list with the chosen transport, including its
   malformed-input case.
4. Sweep the line-budget baselines across Steps 2 through 6 so each "before"
   value references the previous step's recorded final count.

If you disagree with the threat model I stated, say so in the next request with
the adversary you intend instead. That is the one input that decides Q01, and it
is a legitimate choice rather than a settled fact: a plan that means to defend
against local process inspection is a different plan, and it would need to
justify how an LLM caller feeds standard input at all.

Leave the rest alone. The seven steps, their file lists, the tests-first
coverage, the mandatory extraction targets, the validation skeleton, and Q02
through Q06 were assessed this round and need no change.

### Final reviewer decision for plan review-resume-command round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-01T19:44:54+02:00
- Exchange: specification/plan/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for plan review-resume-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
Review round: 2

### Requestor assessment for plan review-resume-command (round 2)

The plan retains its seven dependency-ordered slices and matching validation
skeleton. Both round-1 findings are applied. Q01 now states that the fence
protects against a displaced LLM with repository access, not a hostile local
process inspector, and recommends generation and token flags as the practical
single-call transport with no second durable copy.

Step 3 now tests required-pair, omitted, empty, malformed, duplicate, mismatched,
and redacted flag behavior. Later steps refer to the preceding step's recorded
final line count for every repeatedly touched file. Q02 through Q06 remain
unchanged. I found no additional implementation question and no mismatch between
the plan and validation skeleton. Every round-1 wording change was applied.

### Change summary for plan review-resume-command (round 2)

Since round 1, Q01's threat model and answer changed from standard input to
generation and token flags because the actual LLM caller cannot feed standard
input without putting the secret in a command string or file. Step 3's tests
now cover the complete flag boundary and secret redaction.

Step 3 uses the recorded Step 1 and Step 2 final counts for core, store, and
coordination; Step 5 uses Step 3 final counts for CLI, parser, and wait; Step 6
uses the Step 4 final count for status acceptance. Q02 through Q06, the step
list, file lists, extraction targets, and validation skeleton are unchanged.

### Writer response for plan review-resume-command (round 2)

Writer response: I accept both round-1 findings and the reviewer's Q01 answer. The plan now uses
generation and token flags under the stated displaced-session threat model, and
the transport-specific tests and redaction checks are explicit. Repeatedly
touched files now use prior-step recorded final counts. Please assess the amended
six-question plan for convergence; no disagreement remains.

### Reviewer focus for plan review-resume-command (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-01T19:48:39+02:00
- Exchange: specification/plan/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for plan review-resume-command round 2

Round 2 assesses the amended plan. Both round-1 findings are closed, and the
second one is closed more carefully than I asked.

Q01 now states the threat model in the question itself, names the displaced LLM
session with repository access as the adversary, and says plainly that transport
must avoid a durable copy while not needing to defend against a local user
inspecting live process arguments. The answer is option C, generation and token
flags. Option A's con was corrected to name the exposure the caller
reintroduces, rather than only the two-stage call, and option C's con honestly
records the local-inspection case it does not cover. That is the shape a
decision record should have: the reader can see what was traded away.

Step 3's tests-first list now covers the flag pair as one required pair with
omitted, empty, malformed, duplicated, and mismatched values, plus secret
redaction from diagnostics and transcript output. That last one matters more
than it looks: with the secret in an argument, an argparse error message is a
plausible leak path, and it is now a named test rather than an assumption.

The line-budget fix was applied with judgment rather than mechanically. Step 3
now references the recorded Step 1 and Step 2 counts for core, store, and
coordination, while keeping literal baselines for the CLI, its parser, and the
wait module. I checked why, and it is correct: Steps 1 and 2 list none of those
three files, so Step 3 is their first touch and 558, 132, and 209 are their real
baselines. Step 5 then references Step 3's recorded counts for the same three,
and Step 6 references Step 4's for the status acceptance test. A blanket
substitution would have introduced a different error, and the writer avoided it.

I also confirmed the flag transport does not contradict the settled design. The
design constrains where the secret may be stored and reported, that coordination
holds only the digest and no report prints the secret, and it never speaks about
the channel a session uses to hand the secret to its next command. So the plan
implements the design rather than amending it, and the design needs no
follow-up edit.

Six questions, five unchanged and one flipped on evidence, and I agree with all
six answers. No question is missing.

Two wording items remain, both inside Q01's neighbourhood, and neither changes
an option, an answer, a step, a file list, or a budget. They are listed in the
covered wording.

### Question verdicts for plan review-resume-command round 2

**Agreement on all six questions.** Q01-C, Q02-A, Q03-A, Q04-A, Q05-A, Q06-A.
The five unchanged answers keep their round-1 verdicts, which were checked
against the shipped code where they made checkable claims: `watchdog` sits in
`uv.lock` at line 561 for Q02, and the launcher's `%*` forwarding plus the CLI's
name-to-handler dispatch make Q05's five operations a parser entry and a handler
each.

**Q01, ownership secret transport.** Now settled, and settled on the right
grounds. My round-1 answer was option C and the plan now records it, but the
part that matters is the threat model that arrived with it. Three details are
worth naming because they are what make the answer auditable rather than merely
chosen:

- The adversary is stated in the question, not implied by the answer, so a later
  reader can disagree with the conclusion by disagreeing with the adversary.
- Option A's con was rewritten to name the caller-side reintroduction. The
  original con listed only the two-stage call, which made option A look merely
  inconvenient rather than unreachable.
- Option C's con keeps the local-inspection exposure visible instead of quietly
  dropping it once the option won.

**No missing question.** The six cover transport, the notification dependency,
the hint carrier, the journal format, the command surface, and test setup. The
Q01 flip opened nothing new: it changed which existing option wins, and Step 3
absorbed the consequence in its test list.

**Two wording items for consolidation.** Both sit in Q01 and neither changes a
decision.

- The BBQ analogy still frames the accepted answer as shouting a door code along
  a route, while the memo slot and the whisper describe the two rejected
  options. After the flip that reads as an argument against the answer the
  question reaches. Under the stated threat model the accepted transport is
  closer to saying the code at the door, heard only by whoever is present at
  that moment, while the memo stays in the tray for anyone who comes later. The
  analogy should be adjusted so it stops arguing against its own conclusion.
- Step 3's completion grep is `ownership_(generation|token|digest)`, with
  underscores only. Under the flag transport the CLI surface spells these
  `--ownership-generation` and `--ownership-token`, so the pattern matches the
  Python attribute names but not the flag declarations it is meant to prove.
  Widen it to cover both spellings. This is the same class of drift the
  code-reviewer plan hit, where a check passed through variable names while the
  command identifiers it targeted had been renamed.

### Convergence evidence for plan review-resume-command round 2

Covered wording: two items in Q01 and its step, neither of which changes a decision.

1. Adjust the BBQ analogy for Q01 so it stops arguing against the answer the
   question now reaches. Suggested replacement for the two affected sentences:

   > They can hand it to the guard on a slip, leave it in an office-wide memo
   > slot, or say it at the door where only whoever is present hears it. In this
   > picture: the worker is the LLM session, the door code is the ownership
   > token, the slip is standard input, the memo slot is an environment
   > variable, and speaking at the door is a command-line argument.

   The point of the change is that the accepted transport is momentary rather
   than careless, which is exactly what the stated threat model concluded.

2. Widen Step 3's completion grep so it proves the flag surface it now targets:

   > `rg -n "ownership[-_](generation|token|digest)|ownership-superseded" tools tests/unit/tools/test_review_exchange_ownership`

   The current pattern uses underscores only, so it matches `args.ownership_token`
   while missing the `--ownership-generation` and `--ownership-token`
   declarations the transport decision rests on.

Nothing else needs to change. The threat model, the Q01 answer, the flag
boundary and redaction tests, the prior-step line baselines, the seven steps,
the file lists, the extraction targets, and the validation skeleton are all in
order.

For consolidation itself: the plan has no implementation-decisions table yet,
and when one is created it should record Q01 as option C together with the
displaced-session threat model rather than the option label alone. The answer
reversed between rounds, so a future reader who finds only "option C" will
reasonably wonder why standard input lost, and the threat model is the reason.

Convergence rationale: both round-1 findings are closed and what remains is wording.

The substantive finding was Q01, where the recommended transport could not be
reached by the caller the plan ships into and the question decided between three
options without saying what the secret was being protected from. The amendment
states the adversary in the question, flips the answer to command-line flags on
that basis, corrects option A's con to name the caller-side reintroduction, and
keeps option C's residual exposure visible. Step 3 absorbed the consequence with
flag-pair boundary tests and an explicit redaction test, which closes the leak
path an argument-borne secret creates.

The bookkeeping finding is closed with more care than requested. Prior-step
recorded counts now appear exactly where an earlier step changes the file, and
the literal baselines that remain are correct because Steps 1 and 2 touch none
of those three modules.

I also verified that the flip does not contradict the settled design. The design
constrains storage and reporting of the secret, not the channel between a
session and its next command, so the plan implements the design rather than
amending it and no design edit follows.

What is left is an analogy that now argues against its own conclusion and a grep
pattern that misses the flag spelling it exists to prove. Neither changes an
option, an answer, a step, a file list, a budget, or the validation skeleton,
which is what separates a wording pass from another round.

This recommendation is advisory. It does not authorize consolidation, and the
choice stays with the human at the convergence gate.

### Writer instructions for plan review-resume-command round 2

Stop at the convergence gate and present the human with the identity summary,
this recommendation, the amended plan, and your own assessment. The
recommendation is advisory: only the human chooses `Consolidate` or `Revise and
review again`.

If the human selects `Consolidate`:

1. Apply the two covered-wording items, the Q01 analogy and the Step 3 grep
   pattern.
2. Create the implementation-decisions table from the six answers, and record
   Q01 as option C with the displaced-session threat model beside it. That
   answer reversed between rounds, so the label alone will not tell a later
   reader why standard input lost.
3. Keep the validation skeleton in step with the plan as you consolidate. It
   currently matches Steps 0 through 6 exactly, and that alignment is what makes
   the implementation-check workflow usable later.
4. When implementation starts, treat Step 3 as the step most likely to disturb
   the shipped suites: it changes the signature of every mutating exchange
   command and reduces two risk-band modules at the same time. Its mandatory
   extraction targets are the part to protect if the step runs long, not the
   part to defer.

If the human selects `Revise and review again`, the two wording items are the
only outstanding reviewer findings; any further change is the human's or your
own, not this round's.

Leave the rest alone. The threat model, the six answers, the seven steps, the
file lists, the tests-first coverage, the prior-step baselines, and the
validation skeleton were assessed across two rounds and need no further change.

### Final reviewer decision for plan review-resume-command round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-01T19:55:14+02:00
- Exchange: specification/plan/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-resume-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
