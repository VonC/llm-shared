# Specification review transcript for v0.14.0

- Exchange: specification/plan/v0.14.0/resume-paused
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-10T15:14:55+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan resume-paused (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Review round: 1

### Requestor assessment for plan resume-paused (round 1)

The eight-step plan follows the consolidated requirement and design. It starts with both-host evidence feasibility, then shared read-only artifacts, pause/reader contracts, fresh receiving validation and atomic marked claims, planning, delivery, takeover and process acceptance. Physical-line baselines and 650-line policy, whole-suite scope resolution, fake-clock deadline tests, installed launcher grammar fixtures and the unchecked deferred senv obligation are explicit. Three implementation questions remain proposed and undecided: Q01 shared synthetic evidence fixture ownership, Q02 executed receipt/journal boundary harness and proof limits, Q03 acceptance scenario grouping. Assess the entire plan for missing implementation questions, incorrect source/file assumptions, sequencing gaps, test gaps and line-budget issues. Do not reopen settled feature or design decisions. The validation skeleton has eight matching steps and contains no implementation evidence.

### Change summary for plan resume-paused (round 1)

Initial implementation plan and matching empty validation skeleton created. Added the same short file-based IO clarification to requirement, design, plan and validation without changing settled decisions. The plan names real existing mutation points and new responsibility modules/tests, preserves legacy manual behavior, and carries the deferred integration checklist. Writer review added Q01-Q03 with proposed answers, all User decision: pending. No runtime implementation was performed.

### Writer response for plan resume-paused (round 1)

Writer response:

This is the first independent review round for the implementation plan. There is no prior reviewer feedback to apply and no disagreement. Please assess source viability and the proposed implementation-only questions, including whether the fixture and protected-write test approach supplies meaningful coverage without claiming live-agent compliance. Human decisions and independent convergence remain separate; no consolidation or implementation is authorized by this request.

### Reviewer focus for plan resume-paused (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.14.0.resume-paused.md`
- `.reviews/a.review-requested.plan.v0.14.0.resume-paused.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-10T15:40:51+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan resume-paused round 1

I assessed the current plan: 605 lines, SHA-256
`f946a7d308c76e343ce6dfb8e92ce98a63b5b33d68df6238edcdba2c0a64e6aa`. The
writer removed a duplicated open-questions section at 15:21:56, after the
request was published; this review covers the version without the duplicate.
The validation skeleton has eight matching steps and no evidence.

The plan follows the consolidated design closely. The both-host evidence gate
comes first, the bulk reader stays read-only, readers ship with the marked
route, and the deferred senv checklist is carried into completion. I checked
its source assumptions against the tree at `f182d418`:

- all twenty physical-line baselines match HEAD exactly;
- `ReviewArtifactConfiguration.load`, `derive_artifact_paths`,
  `ReviewExchangeObserver`, `observe_transition`, `claim_selected`,
  `CoordinationRecord` and `OwnershipService` exist in the named modules;
- `observe_transition` opens the lock file read-only and creates nothing, so
  the zero-write snapshot test is achievable;
- the write-plans bands (550 and 650), the `check_big_files.bat` default of
  700, `ghog single` and `pw scope day` are quoted correctly;
- `CoordinationRecord.from_dict` already admits optional keys such as
  `bound_scope_fingerprint` under `strict_fields`, so the marked binding can
  follow that pattern, and older readers will reject it as the design expects.

The plan is not ready to converge. One implementation decision is missing:
where the durable marked-claim binding comes from. Step 4 threads a
"validated binding" through the parser and CLI, which reads as the receiver
passing binding values as claim arguments. Step 7 later treats that record as
takeover proof. Whether `claim` records values it derives itself or values a
caller copied is a safety choice for the user (proposed Q04).

Q01's recommended path does not match the repository convention. No
`tests/support` tree exists. Builders shared by unit and acceptance tests live
in `tests/unit/tools/<area>_test_support.py`, and `tests/acceptance/review_resume`
already imports `tests.unit.tools.review_exchange_test_support`. The option as
written also omits the `tests/support/__init__.py` that package imports would
need. Q02 places its harness inside the Step 4 leaf, so Step 8 acceptance would
have to import it from another test leaf, the cross-import that Q01 sets out to
avoid. Q03 matches the `test_review_resume_acceptance` precedent, but its three
modules do not yet give the five listed areas a home.

Three cross-step inconsistencies need correction:

- Step 3's completion criterion (line 253) requires all four session workflows
  to describe compatible readers, but `instructions/resume-session.md` changes
  only in Step 4.
- The `Qxx` citations in step framings do not say whether they mean design or
  requirement decisions; the design itself carries both numberings. Several
  point at the wrong step: Step 4 cites Q07 (the OS guard, owned by Step 6) and
  Q12 (owned by Step 7) but omits Q11, which is its core. Step 3 cites Q09 and
  Q11, which belong to Steps 2 and 4.
- Step 4 (line 307) says only failures emit the compact result. The design
  requires a result for every outcome, as the first line of a stopping Claude
  turn, and Step 7 observes it.

Several design rules have no test in any step: the pane-label scope of
`--except`; the three absent-target classes (missing UUID, UUID without an
agent such as a CMD shell, UUID now on another host); unknown routing fields
causing an unresolved-target skip; ambiguous multiple live exchanges; the pause
replacement guard from requirement Q29=A and acceptance criterion 14; and the
five-second backoff cap on post-acceptance reads. Step 1 does not define the
Codex session-file candidate set, which decides both the uniqueness proof and
the `B` term of the cost model. The agent-callable validator launcher has no
smoke test, and the plan does not state how `bin/resume_paused.bat` is verified
when no agent may run it.

Two smaller corrections: the baseline table (lines 60-61) lists the requirement
and design as files to update, but no step changes them (the IO clarification
already landed, taking them from 597 to 601 and 721 to 725 lines); and Step 8
(line 474) cites "Command contract" as a design section, but it is a
requirement section.

No settled requirement or design decision needs reopening. All findings are
plan-level.

### Question verdicts for plan resume-paused round 1

Q01, shared synthetic evidence fixtures. The question is needed and its two
options are distinct. I agree that builders should be shared, but not with the
proposed location. I would choose Option A amended to the existing convention:
create `tests/unit/tools/resume_paused_test_support.py` in Step 1 (baseline 0,
ceiling 650) and split it by responsibility later, for example into
`resume_paused_receiver_test_support.py`. `tests/acceptance/review_resume`
already imports `tests.unit.tools.review_exchange_test_support`, so no new
top-level test tree is needed. The proposed answer is not a user decision;
User decision: pending.

Q02, receiver write-boundary harness. The question is needed, the options are
distinct and the live-agent proof limit is stated honestly. I would choose
Option A with one change: put the harness in the shared support layer from Q01
(`tests/unit/tools/resume_paused_receiver_test_support.py`) instead of the
Step 4 leaf, because Step 8 acceptance must drive the same receiver validation
and claim code. The harness should call the real validator module and the real
locked claim, and change evidence between each protected step. Optional
refinement: have the validator JSON include the exact schema-3 receipt binding
lines, so the receiving instruction copies values instead of composing them.
User decision: pending.

Q03, acceptance scenario grouping. The question is needed and the options are
distinct. I would choose Option A, which matches the nine-module
`tests/acceptance/review_resume/test_review_resume_acceptance` leaf. The answer
should name the modules so that all five listed areas have a home (see
requested change 4). User decision: pending.

Missing Q04, source of the durable marked-claim binding. Step 7 trusts this
record as takeover proof, and the plan does not decide whether `claim` derives
it or copies it from the caller. I would choose the option where `claim`
derives the binding from the raw marker under the transition lock (see
requested change 1). User decision: needed.

### Requested changes for plan resume-paused round 1

Requested changes:

Line numbers refer to the round 1 plan (605 lines).

1. Add a question after Q03, using the same structure as Q01-Q03:

   - Title: `Q04: Source of the durable marked-claim binding`.
   - Question description: Step 4 records launch id, pane, host, assignment
     binding, round, occurrence and issued generation in the coordination
     record, and Step 7 treats that record as takeover proof. Should `claim`
     record values it derives from the marker, or values the receiver copies
     from an earlier validator result?
   - BBQ: A grill cook writes the order ticket from the customer's own order
     card, not from a waiter's retelling. In this picture: the card is the
     marker, the retelling is validator output copied into claim arguments,
     and the ticket is the durable marked claim that the bulk tool later
     trusts.
   - Option A: `claim` accepts the raw marker and, for Codex, the carried
     session identity and launch id. Under the transition lock it parses the
     marker, recomputes the assignment digest from the current prompt, routing
     and the locked exchange, and records only those derived nonsecret values.
     Pane and complete-input proof come from the validator call made
     immediately before, as the design requires.
     - pro: The durable record never holds hand-copied values; the digest check
       happens under the same lock as the round and occurrence recheck; `claim`
       gains no TUIOS or host session-file dependency.
     - con: `claim` needs marker parsing and assignment reconstruction from the
       Step 2 and Step 4 modules; pane and input proof still rest on the
       preceding separate call.
   - Option B: The receiver passes the validator's returned binding fields as
     claim arguments; `claim` checks their syntax and the locked round and
     occurrence only.
     - pro: Keeps `claim` generic and smallest.
     - con: A stale or mistyped field becomes the takeover proof that Step 7
       trusts, and nothing ties the recorded values to the prompt and exchange
       at claim time.
   - Option C: `claim` runs the full validator in process, including live pane
     and complete-input proof, then records its result.
     - pro: The narrowest window between proof and record.
     - con: Adds TUIOS calls and host session-file reads to a review exchange
       operation, slows the claim path and couples every claim test to host
       evidence adapters.
   - Recommended option: Option A. It removes hand-copied takeover evidence
     without moving host evidence into the review exchange core; the design's
     separate pre-claim validator call remains.
   - Answer to Q04: option A, with the same rationale. If accepted, replace
     "Thread optional validated binding through parser, CLI, `claim_selected`,
     store and `OwnershipService`" (line 305) with "Thread an optional raw
     marker and carried Codex identity through parser, CLI, `claim_selected`,
     store and `OwnershipService`; under the transition lock, recompute and
     compare the assignment digest and record only derived nonsecret fields",
     and add Step 4 tests for a marker whose digest no longer matches the
     current prompt, routing or exchange.
   - User decision: pending.

2. Q01 (line 536): replace Option A with "Create
   `tests/unit/tools/resume_paused_test_support.py` in Step 1, new, with pure
   synthetic host, pane and session builders imported by the unit leaves and
   by `tests/acceptance/resume_paused`, following the existing
   `review_exchange_test_support.py` convention; split it by responsibility
   before it reaches 650 lines." In the answer (line 549), name that file and
   its Step 1 line budget (baseline 0, ceiling 650). Keep User decision:
   pending.

3. Q02 (lines 563 and 576): place the harness at
   `tests/unit/tools/resume_paused_receiver_test_support.py` instead of the
   Step 4 validation leaf, so Step 8 acceptance imports it without importing
   another test leaf. State that the harness calls the real validator module
   and the real locked claim and changes evidence between each protected step.
   Keep User decision: pending.

4. Q03 (line 603): name the three modules under
   `tests/acceptance/resume_paused/test_resume_paused_acceptance/` and assign
   all five areas:
   `test_resume_paused_cli_safety_tdd.py` (caller rejection, dry run,
   exclusion and switch validation, reporting and exit codes, `tuitp` grammar
   and legacy manual resumes); `test_resume_paused_delivery_tdd.py` (clear,
   transport, guard race, recovery Enter, protected-write failures of the
   resumed receiver); `test_resume_paused_continuation_tdd.py` (takeover,
   reviewer leave-alone, pending and activation, later and switched
   continuation). Keep User decision: pending.

5. Step 3 sequencing: replace "make all shipped receipt readers schema-3
   aware" (line 229) with "make the status and list receipt readers schema-3
   aware", and replace "all four shipped session workflows describe
   compatible readers" (line 253) with "`pause-session`, `status-session` and
   `list-session` describe schema-3 compatible readers; `resume-session` gains
   its schema-3 reader and writer together in Step 4".

6. Step 3 tests (line 249): add contract tests for the pause replacement guard
   (requirement Q29=A, acceptance criterion 14): a different recorded pausing
   pane or saved role guards replacement of an unused or new prompt at pause
   time, even for the same host; unknown values alone establish no
   difference; legacy prompts keep the agent-id comparison; declining keeps
   the old checkpoint. Also check that capture never contacts the counterpart
   or launches `resume_paused`.

7. Decision citations: add one sentence before the numbered steps stating that
   a bare `Qxx` in a framing line means the design decision table, and that
   requirement decisions are written as `requirement Qxx`. Then correct the
   framings: Step 2 adds Q01 and Q09; Step 3 becomes Q01, Q03 and Q10;
   Step 4 becomes Q02-Q04, Q11 and Q13-Q15; Step 5 adds Q08 and Q10.

8. Step 4 result emission (line 307): replace "Failure emits the profile's
   compact result before stopping" with "Every receiving outcome emits the
   profile's compact result of at most 100 characters (launch id, outcome,
   optional claim generation, never a token or digest); on a stopping Claude
   turn it is the first line of the final response, and a failure emits it
   before stopping or asking." Add grammar and length tests for success and
   failure results.

9. Launchers: in Step 4 add a smoke test that runs `bin/resume_paused_validate.bat`
   against temporary fixtures (argument forwarding, UTF-8 JSON output, exit
   code), following `test_review_resume_launcher_smoke_tdd.py`. In Step 8 state
   how `bin/resume_paused.bat` is verified without an agent running it, for
   example a static check that it only forwards arguments to
   `tools/resume_paused.py`, plus human live validation, and carry that limit
   into the validation plan.

10. Step 5 tests (line 357): add the pane-label scope of `--except` (a label
    excludes only its panes) and that `--switch-roles` never matches pane
    labels; the three absent-target classes (saved UUID missing, listed
    without an agent such as a CMD shell, now a different host), giving skip,
    skip and classification error, with no reviewer input to a shell; and
    multiple live exchanges without a saved exact identity, giving ambiguous
    pairing and no counterpart action.

11. Step 2 tests (line 199): add unknown routing fields, which keep the rest of
    the pause and cause an unresolved-target skip rather than a parse error,
    and a JSON and table contradiction, which is an error.

12. Step 1 (line 153): define the Codex session-file candidate set, for
    example every file modified at or after delivery within the date
    partitions from delivery to observation, reading only `session_meta` and
    the latest user-input record, with uniqueness judged over that whole set.
    Record the rule in the profile evidence document and test both a second
    matching file and the bytes read.

13. Step 7 tests (line 445): add the observation cadence, event-driven where
    available and otherwise bounded reads with backoff capped at five seconds,
    under the fake clock.

14. Wording: mark the requirement and design rows of the baseline table
    (lines 60-61) as plan-writing edits already applied, not implementation
    targets, or remove them; and cite "Command contract" in Step 8 (line 474)
    as a requirement section.

15. Realign the validation skeleton with these changes, including the support
    files, the launcher verification limit and any Q04 outcome, without
    adding implementation evidence.

### Writer instructions for plan resume-paused round 1

Apply requested changes 1 to 15 to the plan and its validation skeleton. Add
Q04 with User decision: pending, and keep Q01-Q03 pending; the reviewer's
choices are proposals, not user decisions. Do not reopen any requirement or
design decision, and do not edit the requirement or design for this round.

Then publish a replacement request for another automated review round. No
consolidation or implementation is authorized by this answer.

### Final reviewer decision for plan resume-paused round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-10T17:03:05+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan resume-paused (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Review round: 2

### Requestor assessment for plan resume-paused (round 2)

The plan and validation skeleton retain eight matching steps and no implementation evidence. Q01-Q03 remain pending and now follow existing test-support conventions with exact conditional files and coverage owners. Added pending Q04 for the durable marked-claim binding source; no reviewer proposal has been adopted as a human decision. No additional missing implementation question was found after this pass.

Applied all round-1 sequencing, result grammar, routing, target classification, pause replacement, launcher verification, cadence, citation and baseline corrections. The Codex candidate-set rule includes older date partitions with still-running conversations, so delivery-date partitioning cannot omit an active session. Count all scanned bytes and fail closed on incomplete enumeration.

Question placement encountered an instruction/tool mismatch: the current oqm --append appends without replacing. The accidental duplicate was removed with exact-copy preservation, and this round kept the complete companion and document question set synchronized without --strip or changing recorded decisions. No protocol artifact was edited manually.

### Change summary for plan resume-paused (round 2)

Applied requested changes 1-15 from round 1. Added Q04 with three options and pending decision; amended Q01-Q03 proposals to existing shared-support paths and named acceptance ownership. Corrected Step 3 reader sequencing, requirement/design citations and plan-writing baseline labels. Added explicit pause replacement, unknown routing, JSON/table contradiction, pane-label scope, absent targets, ambiguous exchanges, compact-result grammar and validator launcher smoke coverage. Defined exhaustive Codex candidate enumeration including older partitions and byte accounting. Added five-second observation backoff tests and static-only bulk launcher verification with human evidence limits. Aligned validation expectations, preserving eight not-started steps and all 48 empty evidence placeholders. Requirement and design were unchanged in this review round.

### Writer response for plan resume-paused (round 2)

Writer response:

Accepted all round-1 findings. Q04 now exposes claim-binding derivation as a pending user choice; the Step 4 text no longer implies that copied validator fields are selected. Q01-Q03 remain conditional proposals in the questions and validation expectations, so the baseline step file lists do not silently adopt them. Proposed support files carry baseline 0 and the 650-line ceiling; Q03 names all three scenario modules and their responsibilities.

The candidate-set refinement intentionally enumerates all session-root date partitions, because a conversation started before delivery can still receive the new input. Modification-time selection accounts for documented timestamp resolution, scans enough records to establish complete latest input and charges all bytes read. No design or requirement decision is reopened.

No consolidation, implementation or commit has occurred. Please review the corrected plan and pending Q01-Q04.

### Reviewer focus for plan resume-paused (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-10T17:07:13+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan resume-paused round 2

I assessed the current plan: 655 lines, SHA-256
`5f6fba0c906f21ec7150d953b3c898b68033945b830650b83e87cc02ae47b75d`. The
requirement and design are unchanged since round 1, and the validation
skeleton keeps eight not-started steps with empty evidence placeholders.

All fifteen round 1 changes are applied:

- Q04 asks where the durable marked-claim binding comes from, with three
  distinct options and a pending user decision. Step 4 no longer implies that
  copied validator fields were chosen; it threads a marked-claim context whose
  exact input waits for Q04.
- Q01 and Q02 now use the existing `tests/unit/tools/<area>_test_support.py`
  convention, and the Q02 harness is shared with Step 8 acceptance. Q03 names
  the three modules and gives all five scenario areas an owner. The step file
  lists keep the conditional files out until the user decides, which is the
  right way to avoid silently adopting a proposal.
- Step 3 now completes with the pause, status and list readers, and hands the
  `resume-session` reader and writer to Step 4.
- Line 128 fixes the citation namespace, and the step framings cite the right
  design decisions (Step 4: Q02-Q04, Q11, Q13-Q15). Step 8 cites "Command
  contract" as a requirement section.
- Step 4 requires the compact result for every outcome, tests its grammar and
  100-character bound, and adds a smoke test for the read-only validator
  launcher. Step 8 states that `bin/resume_paused.bat` is checked statically
  only, with live behavior left to human evidence.
- Steps 2, 3, 5 and 7 add the missing tests: unknown routing fields, JSON and
  table contradiction, the pause replacement guard, pane-label scope, the
  three absent-target classes, ambiguous exchanges, and the five-second
  backoff cap.
- The baseline table marks the requirement and design rows as plan-writing
  edits already applied.

The Codex candidate set in Step 1 (line 157) improves on my round 1 example.
It enumerates every date partition, because a conversation started before
delivery can still receive the new input, and it selects files by
modification time, judges uniqueness over that whole set and charges every
byte scanned. That closes the false-uniqueness risk that a delivery-date
window would have left open.

Only wording remains. Step 3 now says `resume-session` gains its schema-3
reader in Step 4, but Step 4 names only the receipt writer (line 316) and has
no test line for schema-3 reuse detection. Step 4 also states the pending-Q04
caveat twice (lines 316 and 318). Neither changes the plan's structure,
sequencing or file set.

Q01-Q04 all still carry User decision: pending. They are the outstanding human
choices; my agreement with the recommended options does not decide them.

### Question verdicts for plan resume-paused round 2

Q01, shared synthetic evidence fixtures. The question is needed, the options
are distinct and Option A now follows the repository convention
(`tests/unit/tools/resume_paused_test_support.py`, as with
`review_exchange_test_support.py`). I would choose Option A: the host profiles
are one contract across the receiver, planner, transport and acceptance tests,
and local copies would drift. User decision: pending.

Q02, receiver write-boundary harness. The question is needed and the options
are distinct. Option A places the harness in shared support, calls the real
validator and locked claim, and states its live-agent proof limit. I would
choose Option A, because Option B cannot show that a receipt or journal write
stops when evidence changes. User decision: pending.

Q03, acceptance scenario grouping. The question is needed and the options are
distinct. The answer names three modules that give all five areas an owner and
matches the `test_review_resume_acceptance` precedent. I would choose Option A.
User decision: pending.

Q04, source of the durable marked-claim binding. The question is needed and
the three options differ in what the takeover proof can contain. I would choose
Option A: `claim` records only values it derives from the raw marker and the
locked exchange, so the record that Step 7 trusts cannot hold a stale or
mistyped copy, and the review exchange core gains no TUIOS or host session-file
dependency. The design's separate pre-claim validator call still proves the
pane and the complete input. User decision: pending.

No further implementation question is missing.

### Convergence evidence for plan resume-paused round 2

Covered wording:

Line numbers refer to the round 2 plan (655 lines).

1. Step 4, line 316: after "Persist schema-3 nonsecret receipt bindings only
   in the receiver.", add "`resume-session` reads schema 1, 2 and 3 receipts
   for reuse detection and writes the schema-3 variant only on a marked
   resume." In the Step 4 tests (line 312), add "schema-3 receipt reuse
   detection in `resume-session`" to the instruction-contract coverage. This
   restates the Step 3 hand-off (line 261) in the step that owns it.
2. Step 4, lines 316 and 318: state the pending-Q04 caveat once. Keep line
   318's paragraph and shorten line 316's clause to "Thread optional
   marked-claim context through parser, CLI, `claim_selected`, store and
   `OwnershipService` (input and derivation per plan Q04)".
3. Step 7 framing, line 449: optionally write "design Q04" so that it is not
   read as plan Q04. Line 128 already defines the namespace, so this is polish
   only.

Convergence rationale:

Every round 1 requested change is applied, in the plan and in the validation
skeleton. Steps 1-8 keep a consistent order: the both-host evidence gate first,
the read-only parsers and pause readers next, then receiver fencing, before any
planner, delivery or takeover work. The source facts and line baselines match
the tree, each design rule I traced has an owning step and test, and the
citations now say which decision table they use.

The open questions are complete and consistent. Q01-Q03 follow existing test
conventions, and Q04 covers the one safety choice that round 1 found missing.
Each question has distinct options, a recommendation that follows from the
design, and a conditional answer that does not slip into the step file lists.
The remaining edits are three wording clarifications.

Outstanding human decisions: Q01, Q02, Q03 and Q04, all User decision:
pending. Convergence is advisory. Consolidation and implementation stay
separate human choices that this answer does not authorize.

### Writer instructions for plan resume-paused round 2

Apply the three wording clarifications without changing the steps, file
lists, baselines or any question's options, recommendations or answers. Keep
Q01-Q04 at User decision: pending.

Then present the convergence gate to the person, naming Q01-Q04 as the
outstanding decisions. Consolidation stays a separate human choice and is not
authorized by this answer.

### Final reviewer decision for plan resume-paused round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-10T17:41:51+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-10T17:42:58+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan resume-paused (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Review round: 3

### Requestor assessment for plan resume-paused (round 3)

#### Writer assessment of the resume-paused decisions for plan resume-paused (round 3)

The user has now explicitly selected Option A for each of Q01, Q02, Q03 and Q04. A successful full question-decisions scan confirms four explicit decisions and zero undecided questions. Their IDs, options, recommendations, explanations and original conditional implementation details remain intact.

The choices are consistent with the existing plan: shared pure evidence builders in Step 1; a shared receiver sequencing harness in Step 4 with real validator and locked-claim calls, changing evidence before protected writes and an explicit live-agent proof limit; three responsibility-based acceptance modules in Step 8; and durable marked-claim fields derived from the raw marker and current assignment under the transition lock, following separate fresh live validation.

I see no missing implementation question from these decisions. The existing alternatives and recorded answers appear sufficient. Independently assess full-specification consistency, interactions with confirmed requirement/design decisions, related validation expectations, and any missing or newly raised question. Recommendations must not overwrite explicit human choices; surface any conflict.

The covered wording from round 2 was applied before the discussion: schema-3 receipt reuse detection and reader ownership are explicit in Step 4; the claim-context wording points to plan Q04; and the Step 7 reference says design Q04. The round-2 recommendation predates these human answers, so it cannot substitute for this follow-up review.

This round reviews recorded decisions before separate human-authorized consolidation. No question block has been removed, no implementation has started, and no implementation evidence has been claimed.

### Change summary for plan resume-paused (round 3)

#### Changes to the resume-paused plan after convergence for plan resume-paused (round 3)

Since round 2, the covered wording was applied and the user completed a one-question-at-a-time explanation of Q01-Q04, choosing A each time. Each answer now contains an explicit confirmed decision, date, scope and rationale. No additional qualifications or conflicting comments were supplied.

Q01 approves shared pure synthetic host/pane/session builders with scenario assertions kept local. Q02 approves a shared test-only receiver harness plus instruction checks, retaining the inability to prove arbitrary live-agent compliance. Q03 approves three acceptance modules for CLI/safety, delivery and continuation without changing the eight steps or 650-line ceiling. Q04 approves binding derivation from the raw marker and current assignment under the transition lock, with required Codex identity and separate fresh pre-claim live validation.

Only the reviewed plan changed during the discussion. The requirement, design and validation skeleton have no new discussion edits. Conditional file-list integration and decision-table consolidation await the separate consolidation workflow; the full question blocks and options remain available for review.

The validation skeleton still contains eight Not started analyses and 48 empty evidence placeholders. No code was implemented and no new commit was created.

### Writer response for plan resume-paused (round 3)

Writer response:

#### Writer response for the resume-paused decision review for plan resume-paused (round 3)

Round 2 recommended convergence with three covered wording clarifications. Those clarifications are applied. The user then selected Explain, which authorized recording explicit decisions and a follow-up independent review, without authorizing consolidation.

The user selected A for Q01, A for Q02, A for Q03 and A for Q04. These human decisions replace the active pending markers in their answer sections. The preceding recommendations remain historical proposals rather than the source of authorization. There is no disagreement with the round-2 assessment.

Review the complete plan and related requirement/design/validation contracts in light of the recorded decisions. Check effects on earlier decisions, safety boundaries, test-support responsibilities and validation limits; identify inconsistencies or new questions. Keep all existing question blocks. Explicitly distinguish any remaining conditional implementation wording awaiting consolidation from an unresolved human choice.

This review must finish before the human is offered the ordinary consolidation gate. Neither the user's answers nor reviewer convergence authorize consolidation or implementation.

### Reviewer focus for plan resume-paused (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-10T17:47:58+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan resume-paused round 3

I assessed the current plan: 663 lines, SHA-256
`8065757a9faa45c1b8444c1039117bfae559920f9636fab7ff6212af8e9370e7`. The
requirement, design and validation skeleton are unchanged since round 2.

The three round 2 wording clarifications are applied. Step 4 now gives
`resume-session` its schema 1, 2 and 3 reuse reader (line 316) and an
instruction-contract test for schema-3 reuse detection (line 312). The claim
context points to plan Q04, and the Step 7 framing says design Q04 (line 449).

The user chose Option A for Q01, Q02, Q03 and Q04. Each answer records the
choice, the date and a rationale, and the options, recommendations and
original conditional details are unchanged. I treated all four as user
decisions and did not change them. They agree with each other and with the
rest of the plan:

- Q01's shared builders (Step 1) feed the Q02 receiver harness (Step 4) and
  the Q03 acceptance modules (Step 8). The Q03 decision explicitly uses the
  approved shared support.
- Q02's harness calls the real locked claim. Under Q04 it can therefore show
  that a prompt, routing or exchange change between the validator call and
  the claim makes the claim reject atomically, which is the test the Q04
  answer adds.
- Q04 agrees with the design. The separate fresh validator call still proves
  the pane and the complete input before the claim (design Q11 and Q13); the
  validator still never claims; the issued generation follows design Q04; and
  the claim now also rechecks the assignment digest under the same lock as the
  round and occurrence. That is stricter than the design's minimum and
  weakens none of its rules. The review exchange core gains no TUIOS or host
  session-file dependency.
- No requirement decision is affected. The bulk tool still never claims
  (acceptance criterion 9), and Step 8 keeps the live-agent proof limit.

One detail of the Q04 decision needs precise wording. The decision says the
claim carries "the required Codex identity", and the answer threads the
carried Codex identity through to `OwnershipService`. But under Option A the
claim reads no host session file, and the design's binding fields do not
include a Codex session identity. The plan should state what the claim does
with it: require it for a Codex host, check that its launch id equals the
marker's, and record nothing beyond the derived binding fields. This only
makes the chosen option precise; it does not reopen it.

The remaining "pending" wording in the body is conditional text that the
consolidation workflow replaces, not an unresolved human choice. It is in
plan lines 128, 318 and 514, the three file lists that do not yet name the
approved support and acceptance files, and validation lines 32, 153, 154 and 314.
No human decision is outstanding, and no new question arises from these
decisions.

### Question verdicts for plan resume-paused round 3

Q01, shared synthetic evidence fixtures. User decision: confirmed, Option A, on
2026-11-10. The recorded choice matches the option and its answer. It agrees
with the repository's `tests/unit/tools/<area>_test_support.py` convention
and with Q02 and Q03, which reuse it. I would have chosen the same. No
conflict.

Q02, receiver write-boundary harness. User decision: confirmed, Option A, on
2026-11-10. The decision keeps the explicit limit that the harness cannot prove
arbitrary live-agent compliance, as Step 8 and the validation plan already
state. Because the harness calls the real locked claim, it also covers the
Q04 rejection path. I would have chosen the same. No conflict.

Q03, acceptance scenario grouping. User decision: confirmed, Option A, on
2026-11-10. The three named modules give all five scenario areas an owner and
keep the eight steps and the 650-line ceiling. I would have chosen the same.
No conflict.

Q04, source of the durable marked-claim binding. User decision: confirmed,
Option A, on 2026-11-10. It agrees with design Q04, Q11 and Q13 and keeps host
observation outside the claim. I would have chosen the same. One wording
point, covered below: state what the claim does with the carried Codex
identity, since Option A reads no host session file.

No question is missing, and none of the four decisions is outstanding.

### Convergence evidence for plan resume-paused round 3

Covered wording:

Line numbers refer to the round 3 plan (663 lines). Item 1 states a
confirmed decision precisely; items 2 to 4 list the conditional wording that
consolidation must replace.

1. Q04's carried Codex identity. Where the plan body describes the marked claim
   (Step 4, line 316, on consolidation), add: "For a Codex host, `claim`
   requires the carried session identity and launch id, rejects a carried
   launch id that differs from the marker's, and records only the derived
   binding fields (launch id, pane, host, assignment binding, round,
   occurrence and issued generation). It reads no host session file; the
   preceding validator call supplies the pane and complete-input proof." Add
   a Step 4 test for a missing or mismatched carried launch id. Leave the
   recorded Q04 answer and decision text unchanged.
2. Plan body: replace the pending wording at line 128 ("Plan questions below
   are separate pending implementation choices"), line 318 ("remains pending
   plan Q04 ... apply the user's selected option") and line 514 ("remain
   pending Q01–Q03 ... rather than silently adopted") with the confirmed
   decisions.
3. File lists and line budgets: add `tests/unit/tools/resume_paused_test_support.py`
   to Step 1 and `tests/unit/tools/resume_paused_receiver_test_support.py` to
   Step 4, each new with baseline 0 and ceiling 650. In Step 8, replace
   `test_resume_paused_acceptance_tdd.py` with
   `test_resume_paused_cli_safety_tdd.py`, `test_resume_paused_delivery_tdd.py`
   and `test_resume_paused_continuation_tdd.py`, each new with baseline 0 and
   ceiling 650. Record the shared support as a read dependency of the later
   steps that use it.
4. Validation: replace the conditional "remains pending: if Option A is
   selected" expectations at lines 32, 153, 154 and 314 with the confirmed
   Q01-Q04 expectations, keeping eight not-started steps and empty evidence
   placeholders.

Convergence rationale:

The round 2 clarifications are applied, and the four recorded user decisions
(Q01-Q04, Option A each) agree with each other, with the eight steps, with the
design's receiver-validation and generation rules and with the requirement's
acceptance criteria. No decision conflicts with earlier ones, and none raises
a new question.

What remains is one sentence that states the confirmed Q04 choice precisely,
plus the conditional wording that consolidation routinely turns into
confirmed text: the pending sentences, the three file lists and the four
validation expectations. None of it changes a step, a decision or a safety
rule.

No question decision is outstanding. Convergence is advisory. Consolidation
and implementation stay separate human choices that this answer does not
authorize.

### Writer instructions for plan resume-paused round 3

No edit is required before the gate. Keep every Q01-Q04 option,
recommendation, answer and recorded user decision unchanged.

Present the convergence gate to the person. No question decision is
outstanding. If the person chooses Consolidate, cover items 1 to 4 of the
covered wording during that workflow. This answer does not authorize
consolidation or implementation.

### Final reviewer decision for plan resume-paused round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-10T19:15:26+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 1 by requestor (exchange 2)

- Recorded: 2026-11-17T14:57:43+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan resume-paused (Q05 to Q07 review) (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Review round: 1

### Requestor assessment for plan resume-paused (Q05 to Q07 review) (round 1)

This exchange reviews the implementation plan's three open questions, Q05, Q06 and Q07, which Step 1 raised and the user answered on 2026-11-15 (Q05=A, Q06=A with two dated corrections, Q07=A). None has had an independent review, and none is consolidated. On 2026-11-17 the user asked for this review with the questions kept; consolidation is not authorized and would come only from the `Consolidate` choice at convergence. The same review should cover the plan text that changed on 2026-11-17 when design Q27 and Q28 were consolidated.

Writer assessment of the questions:

- Q05 (order of Step 1 adapters and the live validation matrix): option A, code now with an empty registry, is what Step 1 delivered. The adapters, the shared builders and their tests are committed after code review exchange 1 converged at round 6; the validation plan reports the code deliverable complete and every live checklist row open; Steps 6 through 8 stay blocked until both hosts have a pinned profile. The block's context still says "design Q27 and Q28 are open", which was true when it was written and is historical now.
- Q06 (check gate failing on the review transcripts): its recorded answer, option A (baseline rows), proved inapplicable, as its two dated corrections record: `MD024` is mandatory, and an existing acceptance test authorizes no new baseline row. The effective outcome is a whitespace-only `MD032` repair under the user's extended Q07 exception. Consolidation must record that effective outcome, not the original option A text.
- Q07 (duplicate `MD024` headings in the design transcript): option A, a one-time repair, was applied on 2026-11-15. Its predicted downside recurred on 2026-11-17: design exchange 8 again produced ten repeated headings (nine reviewer answer headings without an exchange qualifier and one core confirmation heading), repaired under a new explicit user exception. The renderer fix the block names as option C remains a separate effort.

Plan text changed on 2026-11-17 by the design consolidation, for the reviewer to check: Step 1's Claude contract now applies design Q27=B (a local shell command running before its input is recorded is the fifth disclosed limit; every live Claude pane, the proved requestor included, needs fresh validated idle evidence) and carries a new bullet for design Q28=A (cases recorded as not reproduced keep tested conservative handling; an activation that needs one stays pending). The `limits=claude-wait-scope` mentions in Steps 7 and 8 now name the fifth limit.

A possible missing implementation-detail question: the plan aligns Step 1's validation obligations with Q27=B and Q28=A, but does not say which step and file implement them at runtime. Step 7, which activates the reviewer, does not yet name the all-pane idle guard, and nothing assigns the conservative boot-boundary handling that the Step 1 ledger needs before any profile is pinned (today it uses the boot boundary to skip older transcripts' task starts). The reviewer may judge whether wording in Steps 1 and 7 suffices or a new question is needed.

No other missing question is known to the writer.

### Change summary for plan resume-paused (Q05 to Q07 review) (round 1)

Since the plan's last review exchange, the plan changed in two commits:

- `ffba391a` (`docs(resume-paused): record Step 1 decisions`, 2026-11-15) added the `## Open questions for the v0.14.0 resume-paused implementation plan` section with Q05, Q06 and Q07, each with its context, analogy, options, recommendation, answer, the user's dated decision and, for Q06 and Q07, the dated application records.
- `5e3fbefb` (`docs(resume-paused): consolidate Q27 and Q28`, 2026-11-17) aligned Step 1 with design Q27=B and Q28=A: the local-command and all-pane guard sentences, the fifth limit in the disclosed limits, a new Q28=A bullet, and the fifth limit in the `limits=claude-wait-scope` lines of Steps 7 and 8.

No decision-table row changed, and no step was added or renumbered.

### Writer response for plan resume-paused (Q05 to Q07 review) (round 1)

Writer response:

This is the first round of a new plan exchange; there is no earlier feedback to accept or dispute. The questions and the user's recorded answers are presented unchanged. The writer flags in the assessment the historical wording of Q05's context, the effective outcome of Q06 and the open placement of the Q27=B guard and the Q28=A boot-boundary handling, and proposes no edit before the reviewer's judgment.

### Reviewer focus for plan resume-paused (Q05 to Q07 review) (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1-exchange-2 -->

### LLM nature completion for reviewer (exchange 2)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.14.0.resume-paused.md`
- `.reviews/a.review-requested.plan.v0.14.0.resume-paused.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-2 -->

## Round 1 by reviewer (exchange 2)

- Recorded: 2026-11-17T15:09:16+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan resume-paused (Q05 to Q07 review) round 1

#### Independent assessment for plan resume-paused exchange 2 round 1 for plan resume-paused (round 1)

Changes requested. The recorded human choices remain usable: Q05=A, Q06's later explicitly authorized whitespace repair, and Q07=A's bounded heading repair. No new human design decision is needed to assign implementation work already required by consolidated design Q27=B and Q28=A. Keep Q05–Q07 open and preserve their dated decisions; this answer does not authorize consolidation.

Two substantive planning gaps remain. Step 1 describes conservative boot handling without assigning the follow-up to its existing profile/ledger implementation and tests. Step 7 describes activation without explicitly assigning the all-pane idle guard or its final refresh. Reporting the fifth limit does not implement that guard. The validation companion must track these new obligations separately from the historically reviewed Step 1 code deliverable.

This is a static specification review, informed by the current plan, consolidated design, validation plan and relevant existing implementation. No tests or live experiments were rerun. The empty registry still prevents delivery; these findings concern the work required before pinning profiles and enabling the later steps, not a claim that current live delivery is possible.

### Question verdicts for plan resume-paused (Q05 to Q07 review) round 1

#### Question verdicts for plan resume-paused exchange 2 round 1 for plan resume-paused (round 1)

- **Q05: relevant and answered; choose A.** The options distinguish code-first, feasibility-first and renumbering. An empty supported-profile registry permits useful adapter and parser work while preserving the explicitly chosen two-host gate on Steps 6–8. Keep eight steps and separate code completion from live validation. Date the original context as historical: design Q27/Q28 are now consolidated and the adapters exist. Replace the absolute claim that live findings cannot change code with: “Synthetic tests verify the current design contracts. Live validation may require changes to adapter code, tests or profile data; no profile is pinned until its required evidence and conservative handling are satisfied.” The current claim contradicts option A's own rework downside. Do not interpret code-first as completion of the new Q28 follow-up.

- **Q06: relevant historical decision, with a superseded proposal; choose the effective human-authorized repair.** Preserve the original A decision and both dated corrections, but label the later whitespace repair as the current effective answer. This follows original option B's direction; it is not approval to restore baseline allowances. Suggested clarification: “Effective outcome after the second 2026-11-15 decision: retain the committed baseline and apply only the explicitly authorized whitespace repair. The initial baseline proposal was superseded.” Option C is not an available ordinary policy change because MD024 is mandatory, and excluding checks would suppress findings rather than fix their generation. Mark the original recommendation of C as superseded too. The baseline acceptance test restricts MD rules to MD033 and the authorized file-specific MD038; it does not itself prohibit every possible LS003 row. The LS003 row became unnecessary after heading repair. No new user choice is needed to honor the recorded correction.

- **Q07: relevant, sufficiently distinct alternatives; choose A within its recorded one-time scope.** It preserves the entry footers and Round prefix while removing actual findings. B would leave a failed gate and downstream incompatibilities; C is a separate renderer effort. Keep the original 26-heading repair and its evidence unchanged. Add a dated note that the requestor reports a separately authorized 2026-11-17 recurrence repair, including reviewer-rendered answer headings as well as a core confirmation heading. Do not imply that the first exception authorizes later repairs or that only confirmation/escalation headings can recur. No renderer implementation belongs in this plan review.

**Missing questions:** none requiring a new human design choice. The missing runtime owners, regression cases and dependency wording are implementation details of already confirmed Q27/Q28. Resolve them in the existing eight steps. If a proposed solution needs a new evidence source or relaxes a confirmed gate, return that actual design change for human review instead.

### Requested changes for plan resume-paused (Q05 to Q07 review) round 1

Requested changes:

#### Required changes for plan resume-paused exchange 2 round 1 for plan resume-paused (round 1)

1. **R1 — Assign and track the Step 1 conservative-policy follow-up.** Name the existing profile and Claude ledger modules, their test leaves and any necessary extraction in Step 1's files, tests and completion criteria. `tools/resume_paused_profiles.py:256` currently returns the stored boot instant after a timestamp consistency check. `tools/resume_paused_claude_ledger.py:418` treats a file as recent when bound or modified since that boundary, and only processes ordinary lifecycle records when recent. The new plan must explicitly prevent an unproved boundary from excluding earlier ordinary work; merely labeling an experiment “not reproduced” cannot authorize that filter. Assign the validated-versus-unresolved predicate handling, complete older-history evaluation or pending outcome, and required-history failure handling. Name tests for an older unmatched task with an unproved boundary, an independently proved true-boot control, complete older history with matched ends, missing/incomplete required history, and durable schedules without a validated termination. A firing, assumed expiry or host restart must not become schedule termination. Keep Codex's independent process/image/path/manifest rechecks mandatory. Identify which existing modules/tests cover each remaining unresolved Q28 predicate. The ledger is already near the 650-line ceiling; apply the plan's split rule if extending it exceeds the limit.

2. **R2 — Assign and test Q27's runtime guard across activation and continuation.** Make `tools/resume_paused_takeover.py` in Step 7 own the guard composition, with explicit evidence dependencies on Steps 1/5 and final-send integration with Step 6, or name equally concrete owners within the existing steps. Require fresh validated idle evidence for every live Claude pane discovered by TUIOS for the checkout, including the proved requestor after its background wait and turn closure. Q23 binding and requestor-operation exclusions grant no screen exemption. Busy, unreadable or unknown-layout evidence keeps activation pending. Refresh this guard under the checkout guard immediately before delivery, for initial activation and later continuation. Add named unit and Step 8 continuation acceptance cases for a busy non-target/requestor pane, a local command running while persisted transcript evidence appears closed, unreadable/unknown screens, a pane state change before send, a successful all-idle control, and later continuation. Acceptance must exercise composition, not only the limits-report string.

3. **R3 — Make dependencies and validation status match the new obligations.** Update the validation companion with R1/R2 code and test ownership, explicit unfinished follow-up rows, and completion evidence requirements. Preserve the historical Step 1 round-6 code-review result and Q05 decision, while making clear that it does not certify later Q27/Q28 additions. Keep the live rows open and both hosts unpinned. Distinguish Step 1's profile-signature/conservative-policy validation from Step 7's full runtime guard and Step 8's integrated scenarios: requiring completed Step 7 orchestration to pin a Step 1 profile would conflict with the gate blocking Steps 6–8 until both profiles are pinned. Keep Steps 2–5 permitted and Steps 6–8 blocked as explicitly chosen.

4. **R4 — Clarify the unconsolidated decision record.** Apply the Q05 historical/code-rework clarification, Q06 effective-outcome and unavailable-policy clarification, and Q07 bounded-recurrence note described in the question verdicts. Preserve the original decisions and corrections. Where the earlier step body still describes feasibility-first sequencing, add a clear current applicability note referring to confirmed Q05=A so implementers cannot mistake historical wording for an active gate. Do not remove questions, consolidate decision tables, edit protocol transcripts, change baseline policy or repair the renderer in this round.

### Writer instructions for plan resume-paused (Q05 to Q07 review) round 1

#### Writer instructions for plan resume-paused exchange 2 round 1 for plan resume-paused (round 1)

Revise the implementation plan and its validation companion for R1–R4, keeping the eight steps and explicit human choices intact. Choose concrete module and test ownership using the current split Step 1 tree; use the existing line-budget rules rather than treating historical new-file counts as today's inventory. Add a response mapping each requested change to the revised section and explain any disagreement with evidence. Publish another review round. No new human question is required merely to allocate already confirmed behavior to files and steps, and no consolidation is authorized by this answer.

### Final reviewer decision for plan resume-paused (Q05 to Q07 review) round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1-exchange-2 -->

## Round 2 by requestor (exchange 2)

- Recorded: 2026-11-17T15:17:22+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan resume-paused (Q05 to Q07 review) (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Review round: 2

### Requestor assessment for plan resume-paused (Q05 to Q07 review) (round 2)

The plan and its validation companion now carry the round 1 changes; Q05 to Q07 stay unconsolidated, and the three dated user decisions and the Q06 and Q07 application records are unchanged.

- R1: Step 1 has an "Open follow-up for confirmed design Q28=A" naming the current code it changes (`boot_boundary` and `BootDecision` in `tools/resume_paused_profiles.py`, `ClaudeLedger._read` in `tools/resume_paused_claude_ledger.py`), the extraction of the ledger's generation and continuation checks into a new `tools/resume_paused_claude_generation.py` before the ledger grows past its 642 of 650 lines, the unchanged Codex rechecks, the five named regression cases in a new `test_resume_paused_claude_ledger_boot_tdd.py`, the profile and generation test leaves, and its completion evidence. Pinning a profile needs this follow-up and Step 1's idle signature, not Step 7's runtime guard. The Step 1 line-budget checkpoint records the current sizes and the split guidance names the extraction.
- R2: Step 7 owns design Q27=B's all-pane idle guard in `tools/resume_paused_takeover.py`, with discovery from the Step 5 planner, screen classification from Step 1's pinned profile, no exemption from Q23=A or Q24=A, and pending on busy, unreadable or unknown-layout panes. Step 6's delivery gains injected pre-send checks run under the checkout OS guard, so the guard is refreshed immediately before every send on initial activation and later continuation. Step 7 names seven unit cases; Step 8's continuation acceptance exercises the composition. Step 7's split guidance allows extracting `tools/resume_paused_pane_guard.py`.
- R3: the validation plan's Step 1 analysis states that the round 6 verdict certifies the code deliverable only, a new "Open code follow-up for Step 1" section holds four rows with their tests and closing evidence (the earlier live-checklist row for conservative handling moved there), and Step 7's expectations carry the guard composition and its tests. The live rows stay open and both hosts stay unpinned; Steps 2 through 5 stay permitted and Steps 6 through 8 blocked.
- R4: Q05's context now states that live validation may change code, tests or profile data, with a dated note that the context is historical and that code-first does not complete the Q27/Q28 follow-ups; Step 1 opens with a current-applicability note for the feasibility-first wording. Q06 records its effective outcome and marks options A and C as superseded. Q07 records the bounded 2026-11-17 recurrence.

No new question is raised: the changes allocate already confirmed behavior to files and steps. Markdown lint, spelling and whitespace checks of both documents pass, and both keep their line endings.

### Change summary for plan resume-paused (Q05 to Q07 review) (round 2)

Changed since round 1, all uncommitted:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.md`: Step 1 framing, current-applicability note, Q28=A follow-up with files, tests and completion evidence, line-budget sizes and split guidance; Step 6 pre-send checks; Step 7 framing, Q27=B guard with its unit cases and split guidance; Step 8 continuation acceptance coverage; Q05 context sentence and dated note; Q06 effective-outcome note; Q07 recurrence note.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: Step 1 analysis paragraph on what the round 6 verdict certifies, the new open code follow-up section (one live-checklist row moved into it), and the Q27=B guard expectation in Step 7.

No step was added or renumbered, and no decision-table row changed.

### Writer response for plan resume-paused (Q05 to Q07 review) (round 2)

Writer response:

All four requested changes, R1 through R4, are accepted and applied; there is no disagreement. The assessment maps each one to its revised sections.

Choices made inside the instructions, disclosed for assessment:

- R1: the extracted module is named `tools/resume_paused_claude_generation.py`, after the generation checks it receives; its test leaf follows the plan's `test_resume_paused_<area>` layout. The boot cases go into a new ledger leaf, `test_resume_paused_claude_ledger_boot_tdd.py`, as rounds 3 and 4 of the code review added the ordering and evidence leaves.
- R2: Step 6 receives the guard as an injected pre-send check rather than importing Step 7, so the step order stays dependency-free; Step 7 supplies the check. The optional extraction target is `tools/resume_paused_pane_guard.py`.
- R3: the live-checklist row added on 2026-11-17 for conservative handling moved into the new code follow-up section, since it is code work rather than a live experiment.

### Reviewer focus for plan resume-paused (Q05 to Q07 review) (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2-exchange-2 -->

## Round 2 by reviewer (exchange 2)

- Recorded: 2026-11-17T15:22:20+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan resume-paused (Q05 to Q07 review) round 2

#### Independent assessment for plan resume-paused exchange 2 round 2 for plan resume-paused (round 2)

Convergence recommended. The current plan and validation companion resolve R1–R4 without changing the confirmed human decisions, renumbering steps, introducing evidence sources or treating unperformed experiments as validation. No substantive disagreement or missing human design decision remains in this review's scope.

R1 now assigns resolved/unresolved boot policy to the profiles module, older-history and schedule handling to the ledger, the necessary generation extraction, and named regression leaves and completion evidence. Codex rechecks remain mandatory. R2 assigns guard composition to takeover, classification to the profile, discovery to the planner and a fresh pre-send invocation to delivery under the checkout guard; unit and continuation acceptance scenarios exercise the composition. R3 records the follow-up as unfinished and preserves the historical round-6 result without extending its certification. Step 1 pinning does not depend on completing the blocked Step 7 orchestration. R4 records current applicability and effective outcomes while preserving the dated decisions and bounded repair exceptions.

This is a static review of the current specification and related validation changes, not an implementation approval. No tests or live experiments were rerun. Both hosts remain unpinned, and the code follow-up and live validation still need their specified evidence.

### Question verdicts for plan resume-paused (Q05 to Q07 review) round 2

#### Question verdicts for plan resume-paused exchange 2 round 2 for plan resume-paused (round 2)

- **Q05: agree; choose A.** Code-first with an empty registry permits Steps 2–5 while retaining the two-host gate on Steps 6–8. The dated clarification distinguishes historical context from current implementation and acknowledges possible adapter/test changes. The options remain materially distinct; neither waiting for all live evidence before writing code nor renumbering Step 1 is necessary. The recorded human answer is confirmed, not a new reviewer decision.
- **Q06: agree with the effective corrected outcome.** Retain the committed baseline and only the explicitly authorized whitespace repair, following the later human choice in the direction of original option B. The new clarification expressly supersedes the original baseline proposal and policy-exclusion recommendation. Mandatory MD024 and the actual MD-rule baseline restriction are accurately distinguished from the unnecessary LS003 row. The original decisions and corrections remain auditable; no further user choice is missing.
- **Q07: agree; choose A within each separately authorized repair's scope.** The original bounded heading repair preserves entry identity and achieves a real passing gate. The dated recurrence correctly includes renderer answer headings, records the separate exception and grants no standing authority. A disclosed failed gate is not equivalent, and the renderer fix remains a separate effort.

No new question is required. Q27/Q28 behavior is already human-confirmed, and this revision supplies its implementation allocation. Consolidation of Q05–Q07 remains the outstanding human workflow choice; agreement in this review does not authorize it.

### Convergence evidence for plan resume-paused (Q05 to Q07 review) round 2

Covered wording:

#### Covered formulation for plan resume-paused exchange 2 round 2 for plan resume-paused (round 2)

This recommendation covers the current plan's Q05–Q07 with their dated clarifications, Step 1's Q28 follow-up and profile-pinning dependency, Step 6's injected checks, Step 7's Q27 all-pane guard and Step 8's composed continuation scenarios, together with the validation companion's matching open follow-up and guard expectations. Preserve eight steps, an empty registry until evidence permits pinning, Steps 2–5 permitted, and Steps 6–8 blocked until both hosts are pinned.

The accepted decisions are Q05=A, Q06's later expressly authorized whitespace repair with the baseline unchanged, and Q07=A's individually bounded repairs. The later notes qualify historical proposals; they do not erase the original human record. No new source, relaxed closure rule, assumed schedule termination or general transcript-edit authority is covered.

Convergence rationale:

#### Convergence rationale for plan resume-paused exchange 2 round 2 for plan resume-paused (round 2)

The four prior findings are resolved with concrete file/test ownership, dependencies and evidence requirements. The revised formulation distinguishes the completed historical code deliverable from unfinished conservative-policy work and separates profile validation from later runtime orchestration, avoiding a circular gate. The recorded decisions are internally interpretable through their explicit effective-outcome notes and agree with the consolidated design. Only optional wording polish remains. Recommend convergence of this formulation; consolidation is a separate human choice and implementation readiness still depends on the documented gates.

### Writer instructions for plan resume-paused (Q05 to Q07 review) round 2

#### Writer instructions for plan resume-paused exchange 2 round 2 for plan resume-paused (round 2)

No substantive revision or further automated round is required for this formulation. Preserve Q05–Q07 and their dated decisions until the human selects the convergence action. Keep every code follow-up and live-validation row open until its required implementation evidence exists.

Optional wording polish only: change Q05 option A's surviving pro, “A live finding changes pinned data or one rule, not the structure,” to “Live findings can be incorporated through adapter, test or profile changes while the empty registry prevents delivery.” This aligns the short option summary with its corrected context. In the Step 7 pre-send paragraph, “refresh discovery and captures” would make explicit that refreshed all-pane evidence includes current membership as well as current screens; the existing all-pane and fresh-evidence requirements already establish this behavior. Neither polish changes a human choice or adds a new obligation.

### Final reviewer decision for plan resume-paused (Q05 to Q07 review) round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2-exchange-2 -->

## Round 2 by human - human-confirmation (exchange 2)

- Recorded: 2026-11-17T16:39:13+01:00
- Exchange: specification/plan/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
