# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/commit-plan-check
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-25T13:25:15+02:00
- Exchange: specification/feature-request/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
- Outcome: request

### Review identity for feature-request commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
Review round: 1

### Requestor assessment for feature-request commit-plan-check (round 1)

The feature request now defines the existing public validation API, the missing
read-only entry point, the exact no-commit behavior, stable evidence needs,
acceptance criteria, scope exclusions, and direct code references.

Seven genuine feature-level questions remain. They cover the public command
surface, human and structured output, exit-status semantics, mandatory
requestor-side validation, the breadth of the no-write guarantee, missing or
empty input behavior, and exact staged-inventory parity. Each question includes
distinct options, tradeoffs, a recommendation, and a proposed answer. No known
design or implementation-plan question has been placed in this requirement.

### Change summary for feature-request commit-plan-check (round 1)

- Created the v0.11.0 `commit-plan-check` feature request beside its approved
  umbrella-derived child draft.
- Defined the current batch-validation behavior and the missing read-only user
  capability.
- Added behavioral acceptance criteria, mutation boundaries, and code anchors.
- Added seven open questions for the remaining feature-level decisions.

### Writer response for feature-request commit-plan-check (round 1)

Writer response: This is the initial review round, so no reviewer feedback has been applied yet.
Please verify that the seven questions cover every unresolved feature behavior,
that their options do not drift into design or implementation planning, and
that the recommended answers produce a coherent read-only validation contract.

### Reviewer focus for feature-request commit-plan-check (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-25T15:16:33+02:00
- Exchange: specification/feature-request/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
- Outcome: answer

### Reviewer assessment for feature-request commit-plan-check round 1

The feature request is well scoped and sits squarely inside its umbrella
boundary. It adds a read-only entry point over an existing validator rather than
a second validator, keeps commit authority where it is, and states its no-write
guarantee, evidence needs, and exclusions clearly. The seven questions are all
genuinely feature-level.

The reviewer verified every claim in the current-behavior section against the
code rather than accepting it, and each one holds.

### Verified code claims for commit-plan-check (round 1)

| Claim | Evidence |
| --- | --- |
| `validate_commit_plan(blocks, staged_paths)` is public | `tools/git_batch_commit_validation.py` line 82, sole entry in its `__all__` |
| The validator is side-effect-free | Its body performs no I/O and no Git call; it folds group results and membership diagnostics into a returned value |
| `--root-a-commit` with `--dry-run` is rejected | `tools/git_batch_commit_workflow.py` line 410 |
| Root-plan mode means validate then commit | `_run_root_a_commit_workflow` runs a validation phase and then a commit phase |
| The parser is reachable with `interactive=False` | `_read_and_parse_content` is exported |

That last row matters for feasibility: the parser the read-only command needs is
already part of the module's export surface. The staged-path inventory is not,
which is the first finding below.

### The inventory helper Q07 depends on is not reachable (round 1)

Q07 answers G1, reuse the exact staged-path inventory helper from batch
execution, and its only stated cost is that batch limitations are inherited. The
real cost is larger. That helper is `_staged_paths(root)` at
`tools/git_batch_commit_workflow.py` line 192, and it is absent from the module's
`__all__` even though nine other underscore-prefixed functions in the same
module are listed there, including `_read_and_parse_content` and
`_run_root_a_commit_workflow`.

So G1 cannot be implemented by importing the named helper as the option
describes. It requires either adding the helper to the export surface or
extracting it into a module both callers share. That is a real decision with a
regression surface, and the requirement should put it in front of the design
rather than leave it to be discovered during implementation.

The inherited semantics are also worth recording while G1 is being stated,
because parity is the whole point of the answer. The helper runs
`git diff --cached --name-only --no-renames -z` and its docstring says it counts
both sides of a rename. A renamed file therefore appears in the inventory as two
paths, and any plan validated against it must list both. A reviewer quoting the
command's output as readiness-floor evidence needs that stated, and Q07's option
G2 gestures at renames and deletions without ever saying what G1 actually does
with them.

### The command has no name (round 1)

Q01 answers A1, a focused read-only launcher, and the requirement separately
states that the code-reviewer instruction must name the resulting command where
it currently asks for a prose assessment. A name that an instruction must carry
is a public contract, and the requirement never fixes one.

This is the same shape as the baseline-file gap in the markdown-check plan, which
was accepted and closed: an artifact that maintainers and instructions reference
by name cannot be left unnamed at the requirement level. The repository also just
settled a matching precedent worth reusing, a repository-root launcher paired
with a platform-neutral module entry point.

### Requestor-side validation is required but unenforced (round 1)

Q04 answers D1, requiring the requestor to run the command before publishing
every code-review request, and claims that invalid plans are therefore caught
before publication. That benefit only holds if something enforces the obligation.

As written, D1 is a documented duty in an instruction, and D1 itself says the
reviewer reruns the check against received state. Nothing verifies the requestor
ran it, so a requestor that skips it still publishes and the reviewer catches the
invalid plan exactly as it would under D2. The distinction between an obligation
that is written down and one that publication refuses to proceed without is a
feature-level decision, and the option set does not currently contain it.

### Question verdicts for feature-request commit-plan-check round 1

### Q01 verdict for commit-plan-check: agree with A1, but name the command (round 1)

A focused launcher is right. The feature exists to make the safe boundary
obvious, and a command whose entire public surface is validation carries a
stronger guarantee than a flag combination inside the committing interface. A2
would make safety depend on remembering two flags on a command whose root mode
means commit, and A3 doubles the surface for no user benefit.

The answer is incomplete in one respect: it never names the command, while the
requirement elsewhere obliges the code-reviewer instruction to name it. Fix the
name here.

The markdown-check effort settled a precedent worth reusing rather than
reinventing: a repository-root launcher for the local Windows workflow plus a
documented platform-neutral module entry point over the same function, so both
forms share one policy authority. Adopting the same shape keeps the two review
commands consistent for the people who run them back to back.

That precedent raises a question this requirement does not ask, which is whether
the command needs a platform-neutral entry point at all. markdown-check needed
one for a POSIX continuous-integration host. This command's consumers are the
requestor and reviewer roles, so the answer may well be no. It should be decided
rather than left implicit.

### Q02 verdict for commit-plan-check: agree with B3 (round 1)

Human-readable output by default with a stable structured mode is correct, and
the requirement is right that both must render one validation result rather than
run validation twice. B1 forces automation to scrape prose or import internals,
which is exactly the ad hoc coupling this feature exists to remove. No change
requested.

### Q03 verdict for commit-plan-check: agree with C3, align it with the repository (round 1)

Distinct statuses for an invalid plan and an operational failure are right. A
readiness floor must fail closed, and a caller has to know whether to repair
`a.commit` or repair the invocation.

One addition. The repository already has an exit-status convention for exactly
this distinction: `bin/review_exchange.bat` uses zero for a completed operation,
three for an expected protocol stop, and two for invalid input or an unexpected
fatal error. C3 currently says only that statuses must be stable and distinct.
Naming the convention it follows costs a sentence and prevents a third scheme
from appearing in the same workflow.

### Q04 verdict for commit-plan-check: D1 is right but underspecified (round 1)

Requiring validation before publication is the correct direction. The command is
read-only and reuses the exact staged inventory, so the cost is small and both
roles start from the same floor.

D1 does not say what required means, and the two readings produce different
features. As a documented obligation in `group-commits-msg` or the requestor
instruction, nothing verifies compliance, and a requestor that skips the step
publishes anyway, leaving the reviewer's rerun as the only real gate, which is
D2's behavior. As an enforced precondition, request publication refuses to
proceed while the plan is invalid, and D1's stated benefit actually holds.

Reviewer answer: keep D1 and state which. The reviewer would choose the enforced
reading, because the option's entire justification is that invalid plans are
caught before publication, and only enforcement delivers that. If the writer
prefers the documented reading, D1's pro should be softened to match, since it
would then describe an intention rather than a guarantee.

### Q05 verdict for commit-plan-check: agree with E2, with one clarification (round 1)

Forbidding every repository-root write is the strongest and simplest promise,
and rejecting E3 is right because a no-write claim conditional on flags is not
much of a claim.

One clarification prevents a misreading. This repository's review protocol
requires caller-owned evidence to live in ignored root files following the `a.*`
convention, and a reviewer feeding commit-plan evidence into a code-review answer
must produce such a file. E2 does not prevent that, because the caller performs
the redirection and the command still writes nothing itself. Saying so explicitly
keeps an implementer from concluding that evidence cannot be persisted in the
repository at all.

### Q06 verdict for commit-plan-check: agree with F3 (round 1)

Distinguishing a missing plan, an empty plan, an empty staged set, and a
membership mismatch, with none commit-ready, is correct. F1 would let literal set
equality report readiness with nothing to commit, and F2 collapses states that
need different recovery actions.

This also stays consistent with batch behavior, which refuses to replay a root
plan when the working tree is clean rather than treating emptiness as success.
The requirement's own constraint that preconditions run around the validator
rather than inside it keeps G1's parity intact. No change requested.

### Q07 verdict for commit-plan-check: agree with G1, state its real cost (round 1)

Absolute inventory parity is the right answer, and the reasoning is sound: one
staged state must produce one commit-plan result whichever role asks. G2 would
let the three paths disagree about membership, which defeats the feature.

The option understates what G1 requires and what it inherits. Both points are in
the assessment: the named helper is private and unexported, so reuse means
exporting or extracting it, and the inherited semantics are a `--no-renames`
inventory that counts both sides of a rename as separate paths.

### Questions missing from the commit-plan-check feature request (round 1)

- Whether D1's requirement is a documented obligation or an enforced
  precondition, as set out in the Q04 verdict. This is the one missing decision
  the reviewer considers blocking.
- Whether the command needs a platform-neutral entry point alongside the
  repository-root launcher, following the markdown-check precedent, or whether a
  single local launcher is sufficient for its two consumer roles.

No question in the current set is redundant, unclear, or outside scope, and the
writer's specific concern is answered: none of the seven drifts into design or
implementation planning. Each settles an externally observable contract, which is
where a feature request belongs.

### Requested changes for feature-request commit-plan-check round 1

Requested changes: Five changes are requested and the first three block consolidation. This summary
opens with prose because the renderer inlines it behind a label, per the
authoring contract the markdown-check design documents.

- Blocking. Q01 never names the command, while the requirement separately
  obliges the code-reviewer instruction to name it. Fix the name in the answer
  and in the read-only command contract, reusing the markdown-check precedent of
  a repository-root launcher plus a platform-neutral module entry point.
- Blocking. Q04's D1 does not say whether the requirement is a documented
  obligation or an enforced publication precondition. Only the enforced reading
  delivers the benefit D1 claims, since an unverified duty leaves the reviewer's
  rerun as the real gate, which is D2's behavior.
- Blocking. Q07's G1 names a helper that cannot be imported. `_staged_paths` at
  `tools/git_batch_commit_workflow.py` line 192 is absent from that module's
  `__all__`, unlike nine other underscore-prefixed functions there, so reuse
  requires exporting or extracting it. Record that in G1's con, add the inherited
  semantics of a `--no-renames` inventory that counts both sides of a rename, and
  cite the helper in the code-reference section.
- Add a question on whether a platform-neutral entry point is needed alongside
  the launcher, or record in Q01 why one local launcher suffices.
- Two small answer additions: name the repository exit-status convention in Q03,
  which `bin/review_exchange.bat` already uses, and state in Q05 that a caller
  may redirect output into an ignored root `a.*` evidence file without breaching
  the no-write guarantee.
- Accepted without change: Q02 with B3 and Q06 with F3, together with the
  current-behavior section, whose five code claims the reviewer verified
  individually, and the umbrella scope, which the requirement does not exceed.

### Writer instructions for feature-request commit-plan-check round 1

Five changes. The first three block consolidation; the last two close smaller
gaps that would otherwise surface during design.

1. Name the command. Fix it in Q01's answer and in the requirement's read-only
   command contract, since the code-reviewer instruction is separately obliged to
   name it and a name an instruction carries is a public contract. The
   markdown-check effort settled a reusable precedent: a repository-root launcher
   plus a documented platform-neutral module entry point over one shared
   function.

2. State what Q04's requirement means. Decide whether requestor-side validation
   is a documented obligation in `group-commits-msg` and the requestor
   instruction, or an enforced precondition that refuses to publish a request
   while the plan is invalid. The reviewer recommends the enforced reading,
   because D1's stated benefit that invalid plans are caught before publication
   only holds under it. If the documented reading is preferred, soften D1's pro
   so it describes an intention rather than a guarantee.

3. State Q07's real cost and its inherited semantics. The helper the option names
   is `_staged_paths(root)` at `tools/git_batch_commit_workflow.py` line 192, and
   it is absent from that module's `__all__` while nine other underscore-prefixed
   functions in the same module are present. Record in G1's con that reuse
   requires exporting the helper or extracting it into a shared module, and add
   the semantics G1 inherits: the inventory is
   `git diff --cached --name-only --no-renames -z`, which lists both sides of a
   rename as separate paths, so a plan validated against it must list both. Add
   the helper to the code-reference section alongside the validator and parser.

4. Add a question on platform-neutral invocation, or record in Q01 why a single
   local launcher is sufficient. markdown-check needed a second entry point for a
   POSIX continuous-integration host; this command's consumers are the two review
   roles, so the answer may legitimately be no. It should be decided rather than
   left implicit.

5. Two small additions to existing answers. In Q03, name the repository's
   existing exit-status convention that the command follows, which
   `bin/review_exchange.bat` already uses: zero for a completed operation, three
   for an expected protocol stop, and two for invalid input or an unexpected
   fatal error. In Q05, state that a caller may still redirect the command's
   output into an ignored root `a.*` evidence file, so E2's no-write guarantee is
   not misread as forbidding evidence persistence in the repository.

Nothing else is requested. Q02 and Q06 are accepted as written with answers B3
and F3, Q01 with A1, Q03 with C3, Q04 with D1, Q05 with E2, and Q07 with G1, each
subject to the additions above. The current-behavior section is accurate in every
particular the reviewer checked, and the requirement stays inside its umbrella
boundary without reopening a settled earlier-phase choice.

### Final reviewer decision for feature-request commit-plan-check round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-25T15:26:08+02:00
- Exchange: specification/feature-request/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
- Outcome: request

### Review identity for feature-request commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
Review round: 2

### Requestor assessment for feature-request commit-plan-check (round 2)

The feature request now addresses every round-1 finding. It names the focused
repository-root command, defines the paired platform-neutral candidate, makes
requestor-side validation an enforced publication precondition, records the
private inventory helper's reuse cost and exact rename semantics, aligns exit
statuses with the existing review protocol, and distinguishes command-owned
writes from caller-owned evidence redirection.

The open-question set now contains eight feature-level decisions. Q01, Q03,
Q04, Q05, and Q07 incorporate the requested clarifications; Q02 and Q06 remain
unchanged as accepted; and new Q08 decides whether the Python module entry point
is required alongside `commit-plan-check.bat`.

### Change summary for feature-request commit-plan-check (round 2)

- Named the repository-root command `commit-plan-check.bat` in the contract,
  acceptance criteria, Q01, and its recommended answer.
- Added Q08 for the platform-neutral `python -m tools.commit_plan_check` entry
  point and recommended paired adapters over one shared function.
- Made successful requestor-side validation an enforced publication gate in
  the requirement and Q04.
- Recorded `_staged_paths(root)` as private and unexported, plus its
  `git diff --cached --name-only --no-renames -z` two-path rename semantics.
- Mapped exit statuses to zero, three, and two in Q03 and the command contract.
- Clarified in Q05 that callers may redirect output into ignored root `a.*`
  evidence files without making the command itself write repository state.

### Writer response for feature-request commit-plan-check (round 2)

Writer response: All round-1 recommendations were accepted with no disagreement. The requirement
now makes the previously implicit public names, publication enforcement,
inventory semantics, exit convention, and evidence-persistence boundary
explicit. The missing platform-neutral invocation decision is now Q08 rather
than an implementation assumption. Please verify the amended answers and the
whole-document consistency, and recommend convergence only if no substantive
feature-level decision remains missing.

### Reviewer focus for feature-request commit-plan-check (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-25T15:29:11+02:00
- Exchange: specification/feature-request/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
- Outcome: answer

### Reviewer assessment for feature-request commit-plan-check round 2

All five round 1 changes were applied, accurately and without disagreement, and
each was verified against the document rather than against the change summary.

### Verified round 2 corrections for commit-plan-check (round 2)

| Round 1 finding | Round 2 state |
| --- | --- |
| Command unnamed | `commit-plan-check.bat` named in the contract, acceptance criteria, Q01, and its answer |
| Q04 "required" ambiguous | Enforced publication precondition; publication must refuse while the plan is invalid |
| Q07 helper unreachable | G1's con records the private, unexported helper, the export-or-extract cost, and the rename semantics |
| Exit statuses unaligned | Zero for success, three for the expected invalid-plan stop, two for invalid invocation or unexpected failure |
| E2 readable as forbidding evidence | Caller-owned redirection into an ignored `a.*` file explicitly allowed |

The exit mapping deserves a note because it is the one place a reviewer
suggestion could have been applied mechanically and was instead applied with
judgment. Three is used for the expected invalid-plan stop and two for invalid
invocation or unexpected failure, which is exactly how `bin/review_exchange.bat`
separates an expected protocol stop from a fatal input error. An invalid commit
plan is a normal, expected result of validation rather than a malfunction, so it
belongs on three. The answer also states the reason: not to introduce a third
exit-status scheme into the same workflow.

The Q07 con now carries both facts the reviewer measured, that
`_staged_paths(root)` is absent from its module's `__all__` so reuse requires
exporting it or extracting a shared module, and that its `--no-renames`
inventory counts both rename sides as separate paths. The code-reference section
cites the helper alongside the validator and parser, so the design will not
rediscover the constraint.

### New question and whole-document state for commit-plan-check (round 2)

Q08 is a well-formed addition rather than a placeholder. Its three options are
materially distinct, H3 correctly notes that dropping the batch launcher would
break the repository-root convention local users rely on, and H1 follows the
precedent markdown-check settled: paired entry points over one shared function
so neither form can drift from the other's policy.

All eight questions carry exactly one recommendation and one answer. The
confirmed sections contain no clause still deferring a decision, so consolidation
has nothing conditional to resolve beyond folding the answers in.

As a consistency signal the effort has just earned the right to use, the feature
request was run through the Markdown checker this umbrella shipped one row
earlier. It reports no findings under any catalog rule.

Every feature-level decision is settled and evidenced, and no substantive work
remains. The reviewer recommends consolidation. The recommendation is advisory
and authorizes nothing; the choice belongs to the human at the convergence gate.

### Question verdicts for feature-request commit-plan-check round 2

### Q01 verdict for commit-plan-check: accepted, A1 (round 2)

The focused launcher is now named `commit-plan-check.bat` everywhere it needs to
be, including the read-only command contract and the acceptance criteria, so the
code-reviewer instruction has a concrete name to carry. Nothing further is
needed.

### Q02 verdict for commit-plan-check: accepted, B3 (round 2)

Human-readable output by default with a stable structured mode rendering the same
typed result, rather than a second validation pass, remains correct and unchanged.

### Q03 verdict for commit-plan-check: accepted, C3 (round 2)

The status mapping is right and the reasoning behind it is right. An invalid plan
is an expected outcome of a readiness check rather than a malfunction, so three
matches how the review protocol already marks an expected stop, while two stays
reserved for invalid invocation and unexpected failure. A shell gate now fails
closed on an invalid plan and can still tell that case apart from a broken
invocation.

### Q04 verdict for commit-plan-check: accepted, D1 as enforced (round 2)

The ambiguity is resolved in the direction that makes D1's justification true.
Publication is blocked until requestor-side validation succeeds, and the reviewer
still reruns the command against the state it actually receives. The answer also
names why the alternative was rejected, that a documented but unenforced duty
leaves the reviewer's rerun as the only real gate.

### Q05 verdict for commit-plan-check: accepted, E2 (round 2)

The zero-command-write contract is intact and the clarification lands where it
belongs, in the answer rather than as a footnote. The command writes nothing
under the repository root, and a caller may still redirect its output into an
ignored `a.*` evidence file, which is what a reviewer needs to feed commit-plan
evidence into a code-review answer.

### Q06 verdict for commit-plan-check: accepted, F3 (round 2)

Distinct fail-closed diagnostics for a missing plan, an empty plan, an empty
staged set, and a membership mismatch remain correct and unchanged, and the
preconditions still run around the public validator rather than inside it, so
Q07's parity is untouched.

### Q07 verdict for commit-plan-check: accepted, G1 (round 2)

Absolute inventory parity stands, and the option now states honestly what it
costs and what it inherits. An implementer reading G1 alone learns that the named
helper cannot simply be imported and that a renamed file appears as two paths, so
neither fact has to be rediscovered against the code.

### Q08 verdict for commit-plan-check: agree with H1 (round 2)

The question the reviewer asked for is present and well formed rather than
perfunctory. H1 pairs `commit-plan-check.bat` with
`python -m tools.commit_plan_check` over one shared function, which follows the
precedent markdown-check settled and keeps one policy authority behind two
adapters. H2 would leave non-Windows callers importing internals, which is the
coupling this feature exists to remove, and H3's con correctly identifies that
dropping the root launcher breaks the convention local users depend on.

The reviewer would choose H1 for the same reason the markdown-check equivalent
was accepted: the second adapter is small, and the alternative is that a future
non-Windows consumer reaches past the public surface.

### Missing decisions in the commit-plan-check question set (round 2)

None. The round 1 gaps were the unnamed command, the undefined meaning of
required in Q04, and an inventory option that understated its own cost. All
three are closed and verified, and the platform-neutral decision that was
previously an implicit assumption is now Q08 with a stated answer. No question in
the set is redundant, unclear, or outside scope, and none drifts into design or
implementation planning.

### Convergence evidence for feature-request commit-plan-check round 2

Covered wording: No substantive change is requested, and only ordinary consolidation work remains.
This summary opens with prose because the renderer inlines it behind a label.

- Fold the eight answered questions into the confirmed text. No confirmed clause
  still defers a decision, so nothing else needs rewording.
- Optionally carry the two entry-point names into the design's public-surface
  section verbatim, `commit-plan-check.bat` and
  `python -m tools.commit_plan_check`, since the code-reviewer instruction must
  name the first and automation will reference the second.
- Optionally record in the design that the `_staged_paths(root)` decision is
  export-or-extract rather than free reuse, so the choice is made deliberately
  with its regression surface in view rather than during implementation.

Everything else is settled: the command contract and its named launcher, the
output forms, the exit-status mapping, the enforced publication precondition, the
zero-command-write boundary with caller-owned redirection, the empty and missing
input diagnostics, absolute inventory parity with its stated cost and rename
semantics, the paired platform-neutral entry point, the acceptance criteria, the
scope exclusions, and the code references.

Convergence rationale: The feature request is ready for consolidation, and the reviewer reaches that
position by verification rather than by round count.

Every feature-level decision the umbrella left to this requirement is settled
with a stated answer and a reason: the public command surface, the output forms,
the exit-status boundary, the requestor's obligation, the breadth of the no-write
guarantee, empty and missing input behavior, staged-inventory parity, and
platform-neutral invocation. The reviewer independently agrees with A1, B3, C3,
D1, E2, F3, G1, and H1.

The three round 1 gaps are closed and confirmed against the document and the
code. The command is named `commit-plan-check.bat` wherever an instruction or an
acceptance case must reference it. Q04's requirement is now an enforced
publication precondition, which is the only reading under which its stated
benefit holds. Q07's option records that `_staged_paths(root)` is private and
absent from its module's `__all__`, that reuse therefore means exporting it or
extracting a shared module, and that its `--no-renames` inventory counts both
sides of a rename as separate paths.

Two smaller corrections landed with judgment rather than mechanically. The exit
mapping places an invalid plan on three, matching how the review protocol already
marks an expected stop, and reserves two for invalid invocation, with the answer
naming the goal of not adding a third scheme to the same workflow. The Q05
clarification sits inside the answer, so an implementer reads the no-write
guarantee and its caller-redirection boundary together.

The requirement is implementable as written. A reader can determine which command
to ship and what to call it, which entry points exist, what the output must
contain in both forms, what each exit status means, when validation must run and
what happens if it fails, what the command may never write, what every empty or
missing input reports, exactly which staged inventory defines membership and what
a rename looks like in it, and which existing functions are reused rather than
reimplemented. The five current-behavior claims the reviewer checked against the
code in round 1 all held, and none was changed in round 2.

As a final consistency signal, the document passes the Markdown checker this same
umbrella delivered one requirement earlier, with no findings under any catalog
rule.

Only consolidation remains, and the reviewer recommends it. That recommendation
is advisory and does not authorize consolidation; the decision belongs to the
human at the convergence gate, who may equally choose another round.

### Writer instructions for feature-request commit-plan-check round 2

No substantive change is requested. The feature request is complete, internally
consistent, verified against the code, and implementable as written.

At consolidation, fold the eight answered questions into the confirmed text. No
confirmed clause still defers a decision, so nothing else needs rewording.

Two items worth carrying into the design phase, neither of which blocks
consolidation.

1. Carry both entry-point names verbatim into the design's public-surface
   section. The code-reviewer instruction must name `commit-plan-check.bat`
   where it currently asks for a prose assessment, and automation will reference
   `python -m tools.commit_plan_check`.
2. Treat the `_staged_paths(root)` question as export-or-extract rather than
   free reuse. Exporting the existing helper is the smaller change; extracting a
   shared module is cleaner but touches the batch workflow. Either is defensible,
   and the design should choose deliberately with the regression surface in view.

The reviewer recommends consolidation. The recommendation is advisory; the human
at the convergence gate may choose `Consolidate` or `Revise and review again`.

### Final reviewer decision for feature-request commit-plan-check round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-25T15:36:36+02:00
- Exchange: specification/feature-request/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
