# Specification review transcript for v0.14.0

- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-03T23:29:02+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 1

### Requestor assessment for feature-request shared_lifecycle_gate (round 1)

The writer's assessment of the feature request before any independent
review.

Open questions: ten, Q01 to Q10, all with options, a recommendation and a
proposed answer, and every one still at `User decision: pending`. They cover
where an opted-in project's gate applies (Q01), the evidence for the Python
3.12 promise (Q02), the platforms promised (Q03), the process audit's window
(Q04), per-test exemptions from the audit (Q05), where a consuming project's
accepted CPU exceptions live (Q06), a report-only adoption mode (Q07), the
evidence for the consuming-project acceptance criteria (Q08), the stability
promise to opted-in projects (Q09) and the defaults a consuming project gets
(Q10).

Known tension: the recommended answer to Q01 (the gate applies only to runs
llm-shared prepares) conflicts with item 1 of the gap list as written today,
which names the plugins with `-p` in the project's `addopts`. If Q01 is
accepted as recommended, consolidation must rewrite item 1, item 8 and the
first acceptance criteria accordingly.

Considered and not raised: llm-shared's Hypothesis profile and its other suite
plugins (stated out of scope), the groundhog `speed` verdict (out of scope),
and the packaging route that makes the plugins importable (left to design in
item 8).

Points where an independent view is most useful:

- whether item 8's list of candidate routes belongs in a requirement or only
  in the design;
- whether Q02 and Q08 stay at requirement level (what evidence accepts a
  criterion) or slide into implementation detail;
- missing questions, for example on behaviour under pytest-xdist, on the
  record's location in a consuming project without an artifact home, or on
  what the summary shows when only one plugin is loaded;
- whether the public-repository rule holds: the document counts the consuming
  projects checked and gives their pytest and Python versions, without naming
  any.

No reviewer wording suggestion exists yet, so none was applied.

### Change summary for feature-request shared_lifecycle_gate (round 1)

First round: the feature request is new. It was written from the draft
`docs/v0.14.0/draft.v0.14.0.shared_lifecycle_gate.md`, then its open-questions
section (Q01 to Q10) was placed with `oqm`. There is no earlier round to
compare against.

### Writer response for feature-request shared_lifecycle_gate (round 1)

Writer response:

No reviewer feedback exists yet, so there is nothing to accept or dispute in
this round. The user asked for this independent review and plans to go
through the undecided questions with the writer once the review converges.

### Reviewer focus for feature-request shared_lifecycle_gate (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `C:/Users/[private project]/git/llm-shared_shared_lifecycle_gate/.reviews/a.review-active.specification.feature-request.v0.14.0.shared_lifecycle_gate.md`
- `C:/Users/[private project]/git/llm-shared_shared_lifecycle_gate/.reviews/a.review-requested.feature-request.v0.14.0.shared_lifecycle_gate.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-03T23:38:31+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 1

The split into independently enabled lifecycle and process plugins is coherent, and the requirement preserves the existing CPU, wall, record and controller contracts. No private consuming-project identifier appears in the reviewed requirement. Version counts and generic package-collision facts do not identify a project.

Disposition: changes-requested. The Python 3.12 evidence recommendation is insufficient for the runtime support promise; the prepared-environment proposal lacks a defined response to activation failure. These need revised question formulations before convergence. All Q01-Q10 decisions remain pending; reviewer preferences below are advisory.

The current implementation confirms the narrow audit window: tests/simulation_policy.py installs an audit hook permanently but rejects process events only while its runtest-protocol tracking is active. The reference explicitly covers both clocks, strict operation without a safe artifact home, and serial/xdist controller writes. Those already specified behaviors do not need duplicate questions.

There is no current-request drift requiring a separate rejection: the requestor correctly describes Q01's proposed change to the baseline. Preserve the distinction between the current baseline and changes conditional on a future user answer.

### Question verdicts for feature-request shared_lifecycle_gate round 1

| Question | Assessment and reviewer choice | Suggested formulation or consequence |
| --- | --- | --- |
| Q01 | Relevant; A1/A2/A3 have distinct enforcement and availability consequences. Prefer A2 for the stated agent workflow, subject to an explicit activation-failure rule. | Say: "When opted in, both a plain pytest invocation from the project's prepared shell and every groundhog test stage load the selected plugins. Runs outside that prepared environment acquire no automatic activation." Do not promise every agent uses that environment. Label the changes to gap items 1/8 and acceptance as conditional on the user selecting A2. Permit explicit invocation elsewhere when the plugin is available. |
| Q02 | Relevant evidence decision, not an implementation prescription. Disagree with B2 as sufficient evidence. Choose B1. Static targeting cannot demonstrate import-time behavior, pytest hook compatibility, or runtime library behavior on 3.12. | Proposed answer: "Acceptance includes executable evidence under Python 3.12 for plugin loading, independent and combined operation, settings rejection, lifecycle enforcement and audit attribution. It uses tests independent of the host project's 3.13-only helpers; static checks supplement this evidence." Exact harness and test location belong to design. Keep B2 as the explicitly weaker alternative if the human chooses it, and remove the claim that it guarantees runtime support. |
| Q03 | Relevant; choices distinguish tested support from portability expectations. Prefer C3 with narrower wording. | Say "Validated on Windows; intended to use portable APIs. Linux and macOS are unvalidated in this release." "Platform-independent by construction" is a stronger assurance than the evidence supports. A portable API does not prove the same audit events and timing behavior on every OS. |
| Q04 | Relevant and distinct from exemption policy; choose D1. Matches the current source and worker startup behavior. | State that the hook may remain installed, while enforcement is active only during test setup, call and teardown, including shared-fixture work attributed to the active lifecycle. Collection and worker startup remain outside this window. |
| Q05 | Relevant adoption policy; E1/E2/E3 have distinct bypass consequences. Choose E1 to preserve the confirmed whole-suite simulation policy. | "There are no per-test or path exemptions from the audit. A project may enable the lifecycle plugin without enabling the audit." No new exemption mechanism. |
| Q06 | Relevant because accepted decisions and measured ceilings have different sharing needs. Choose F1 to preserve the per-checkout contract. | "Accepted CPU exceptions remain in the ignored per-checkout record and are not copied into tracked configuration." No change to accepted exception fields or wall limits. |
| Q07 | Useful confirmation of the existing no-disable policy rather than a missing default. Choose G1. | Mention both test_lifecycle_limit and test_lifecycle_wall_limit for staged adoption; raising only CPU does not help wall overruns. Replace "a failing run lists every offender anyway" with "a run reports violations for executed lifecycles; selection or early-stop options may prevent a complete inventory." |
| Q08 | Relevant acceptance-evidence decision. H1/H2/H3 have distinct repeatability and environment coverage. Prefer H3, provided its scope is made explicit. | "Acceptance combines repeatable isolated-project evidence and a temporary trial in a consuming environment, without changing that project's files or enabling the plugins persistently." Distinguish persistent adoption (out of scope) from the proposed temporary validation. Coordinate this evidence with B1 so the two acceptance checks can share a run where appropriate. A command-line trial in one context alone does not establish both prepared-shell and groundhog activation. |
| Q09 | Relevant, but combines compatibility for the extraction with an indefinite future-version policy. Prefer a bounded I1. A changelog entry cannot prevent behavioral surprises. | "For this extraction, existing valid records remain readable, exceptions retain their meanings, and proofs remain eligible under the unchanged current-ceiling rules. Later contract changes must be documented with their compatibility or migration behavior." Do not promise that every historical proof remains usable after a changed ceiling, or that every possible future schema is preserved forever. I3 pinning remains a distinct design/upgrade-policy alternative, not an assumed current packaging model. |
| Q10 | Redundant with gap item 6 as a missing requirement, but useful as an explicit confirmation choice. Choose J1. | Preserve 0.1 s CPU, 1 s wall, 2.5 band and 3 drift runs with the existing override precedence. If J2 or J3 is selected, report the resulting conflict with the unchanged-contract baseline before consolidation. |

Missing decision: extend Q01 with a prepared-environment activation-failure question, or add Q11 if independent choices need separate answers. When a project has opted in and llm-shared prepares a run but cannot import one selected plugin, should that run (K1) fail startup identifying the plugin, (K2) warn and continue without it, or (K3) run the remaining selected plugin and report partial enforcement? K1 preserves the enforcement guarantee but temporarily blocks testing until setup is repaired. K2 preserves availability but lets the budget disappear. K3 preserves partial checks but makes an opt-in mean different things across runs. Recommend K1; environments outside the prepared scope remain unaffected. This is an observable product decision; the injection and packaging mechanisms remain design work. Leave its user decision pending.

No additional question is needed about xdist: gap items 5/6 and the explicit controller-write acceptance criterion already require operation with and without it. No separate record-location question is needed: gap item 4 states strict mode and no recording when the ignored home is absent. Add acceptance examples for those rules rather than reopening the choices. Audit-only operation should have no lifecycle CPU band summary or lifecycle-record writes; this follows from independence and can be made explicit without a new human decision.

### Requested changes for feature-request shared_lifecycle_gate round 1

Requested changes:

Required for another round: an evidence standard consistent with Python 3.12 runtime support (Q02), a defined failure policy for unavailable selected plugins inside the proposed prepared environment (Q01/Q11), an unambiguous temporary-validation boundary (Q08), and compatibility wording that preserves valid proofs without promising indefinite schema support (Q09). The verdicts provide concrete replacement wording and the reviewer choice for all ten existing questions. Q03's platform wording and Q07's wall/early-stop corrections are accompanying precision fixes.

Keep packaging candidates as nonbinding design considerations, or replace gap item 8's candidate list with "The design selects one supported import route that satisfies the chosen activation scope and package-collision requirements." No packaging choice needs to be made at requirement review. Q02 and Q08 properly belong here as acceptance-evidence decisions; exact commands, harnesses and module layouts belong to design and plans.

Use only generic consuming-project descriptions in tracked evidence. No private trial has been performed or approved by this reviewer. The stale request conclusion saying "project-root" is superseded by the artifact-home policy; answer publication will use the core-returned .reviews path.

### Writer instructions for feature-request shared_lifecycle_gate round 1

Revise the open-question formulations and proposed answers only; do not consolidate or record a human decision. Keep Q01-Q10 as pending. Preserve the current baseline as such, and describe consequences of each proposed answer conditionally.

1. Rework Q02's recommendation to executable Python 3.12 evidence (B1), or explicitly dispute this finding with concrete evidence of what the static tools can establish. Do not claim static targeting demonstrates runtime behavior.
2. Extend Q01 or add Q11 with the activation-failure choice described in the verdicts, recommending failure inside a prepared opted-in environment and leaving outside environments unaffected.
3. Clarify Q08's temporary validation scope versus persistent adoption, and the coverage needed for the two activation contexts. Preserve H3 as proposed rather than authorized.
4. Bound Q09's compatibility wording to this extraction and current proof eligibility; separate documented future migrations from an unlimited backwards-compatibility promise.
5. Apply the specific Q03 and Q07 corrections. Make audit-only summary/record independence explicit where appropriate, without introducing a new policy choice.
6. In the next request, identify each revision and any disagreement. Publish another review request through the existing exchange. No plugin implementation or consuming-project trial is requested by this review.

### Final reviewer decision for feature-request shared_lifecycle_gate round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-03T23:50:13+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 2

### Requestor assessment for feature-request shared_lifecycle_gate (round 2)

The writer's assessment after applying the round 1 review.

Open questions: eleven, Q01 to Q11, each with options, a recommendation and a
proposed answer, and every one still at `User decision: pending`. Q11 is new,
added as the reviewer asked: what a prepared run of an opted-in project does
when a selected plugin cannot be imported, with K1 (fail at startup, naming
the plugin) recommended.

Every round 1 instruction was applied, and no reviewer finding is disputed:

- Q02 now recommends executable Python 3.12 evidence (B1), with static checks
  as a supplement and B2 kept as the explicitly weaker alternative.
- Q01 states its consequences conditionally: the current gap items 1 and 8 and
  the first acceptance criteria stay the baseline, and change only if the user
  selects A2.
- Q08 separates the temporary validation trial from persistent adoption and
  requires the trial to cover both activation contexts.
- Q09 is bounded to this extraction plus documented later changes.
- Q03, Q04, Q05, Q06, Q07 and Q10 carry the reviewer's precision wording.

Requirement body: gap item 8 no longer lists packaging candidates and leaves
the import route to the design; the acceptance criteria now state that an
audit-only run shows no `lifecycle CPU band` summary and writes no record, and
add the no-artifact-home example the reviewer asked for. The xdist
controller-write criterion was already present.

The writer sees no further missing question. Points still worth an
independent look: whether Q11 should stay separate from Q01 (it applies under
A1 too, since every run is then prepared-or-failing), and whether any revised
answer now reads as a recorded decision rather than a proposal.

### Change summary for feature-request shared_lifecycle_gate (round 2)

Changes to the reviewed feature request since round 1:

- Gap item 8: the list of candidate import routes is replaced by "The design
  selects that route so that it satisfies the activation scope this
  requirement settles and the package-name rule of item 3".
- Acceptance criteria: the audit-only criterion adds that no
  `lifecycle CPU band` summary appears and no lifecycle record is written; a
  new criterion states that, without an existing ignored artifact home, every
  test is held to its ceiling, nothing is recorded, and the summary says so.
- Q01: option A2 now reads "a plain `pytest` run from the project's prepared
  shell and every groundhog test stage load the selected plugins; runs outside
  that prepared environment get no automatic activation, and may still name a
  plugin explicitly where it is importable". Its pro and the recommendation no
  longer promise that every agent uses that environment. The answer marks the
  changes to gap items 1 and 8 and the first acceptance criteria as
  conditional on the user selecting A2, and points to Q11.
- Q02: recommendation changed from B2 to B1, with the reviewer's proposed
  answer; B2's con now says it cannot demonstrate import-time, hook or runtime
  behaviour on 3.12; B2 stays as the weaker alternative.
- Q03: option C3 and its answer now say "validated on Windows; intended to use
  portable APIs; Linux and macOS unvalidated in this release".
- Q04: the answer states that the hook may stay installed while enforcement is
  active only during setup, call and teardown, shared-fixture work attributed
  to the active lifecycle included.
- Q05: the answer states that there are no per-test or path exemptions, and
  that the lifecycle plugin may be enabled without the audit.
- Q06: the answer states that accepted exceptions stay in the ignored
  per-checkout record, are not copied into tracked configuration, and keep
  their fields and the wall limit unchanged.
- Q07: option G1, the picture and the answer name both `test_lifecycle_limit`
  and `test_lifecycle_wall_limit`; "a failing run lists every offender anyway"
  is replaced by wording on executed lifecycles and selection or early-stop
  options.
- Q08: option H2 is a temporary trial covering both activation contexts,
  changing no file and enabling nothing persistently, with a new con about a
  single-context trial; the recommendation separates temporary validation
  from persistent adoption and lets it share a run with the Q02 evidence.
- Q09: option I1, the recommendation and the answer are bounded to this
  extraction (valid records readable, exceptions keep their meaning, proofs
  eligible under the current-ceiling rules) plus documented compatibility or
  migration behaviour for later changes; I3's con calls pinning a design and
  upgrade-policy alternative.
- Q10: the answer adds the existing override precedence and the report of a
  conflict with gap item 6 if J2 or J3 is selected.
- Q11: new question on a prepared run that cannot import a selected plugin
  (K1, K2, K3; K1 recommended), decision pending.

Placement note: `oqm --append` appended the amended section after the old one
instead of replacing it. The writer then ran `oqm --strip` and `oqm --append`
from the complete companion, and checked that the document's single section
equals the companion (eleven questions, every option and pending answer kept).

### Writer response for feature-request shared_lifecycle_gate (round 2)

Writer response:

All round 1 findings are accepted and applied as the reviewer worded them; there
is no disagreement. Q11 was added as a separate question rather than folded into
Q01, because its choice stays meaningful whichever activation scope the user
selects.

Every decision remains pending: no answer records a user choice, and nothing
was consolidated.

For the record: the requestor's round 1 input
`a.spec-review.assessment.shared_lifecycle_gate.r1.md` was overwritten after
publication with the reviewer's assessment text, apparently through a shared
scratch name. The published request was not affected. This round's requestor
inputs use `requestor`-prefixed names to avoid the collision.

### Reviewer focus for feature-request shared_lifecycle_gate (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-03T23:52:24+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 2

Convergence recommended for the current question formulations. The revised specification and the validated round 2 request agree. The Python 3.12 recommendation now requires executable evidence; Q11 covers unavailable selected plugins; Q08 distinguishes temporary validation from persistent adoption; Q09 preserves valid records without an unlimited future-schema promise. The independent audit summary/record behavior and missing-home criterion are explicit. The packaging mechanism remains design work.

No further missing requirement-level decision was identified. Existing xdist, record-location, unchanged-contract and package-collision requirements supply the remaining boundaries. Two small formulation improvements below do not change the recommended answers or require another automatic round.

Every Q01-Q11 user decision is still pending. This convergence is agreement with the proposed questions and answers, not permission to implement, consolidate, run a consuming-project trial, or treat recommendations as confirmed choices.

The requestor reports a shared scratch-name collision from round 1. Its published request was unaffected. These reviewer inputs use an explicit reviewer prefix to avoid repeating that collision.

### Question verdicts for feature-request shared_lifecycle_gate round 2

| Question | Reviewer choice and verdict |
| --- | --- |
| Q01 | A2. Clear distinction between prepared and outside environments; consequences for the current baseline are now explicitly conditional on the user's choice. |
| Q02 | B1. Executable Python 3.12 evidence now matches the runtime promise; B2 is accurately presented as weaker static evidence, and B3 explicitly drops support. |
| Q03 | C3. Validated Windows support and unvalidated portability intent are distinguished without claiming proof on Linux or macOS. |
| Q04 | D1. Preserves the active test-lifecycle window while distinguishing permanent hook installation from active enforcement. |
| Q05 | E1. Independent gate adoption supplies the gradual path; no per-test or path audit exemption is introduced. |
| Q06 | F1. Machine-specific accepted CPU values remain in the ignored checkout record with unchanged fields and wall rules. |
| Q07 | G1. No report-only mode is needed; temporary CPU and wall overrides are explicit, and inventory limitations are acknowledged. |
| Q08 | H3. Repeatable isolated-project checks plus temporary environment validation cover complementary risks; no persistent adoption is authorized. |
| Q09 | I1 as revised. Existing valid records and current-ceiling proof eligibility survive this extraction; later changes document compatibility or migration. |
| Q10 | J1. Shared defaults and override precedence remain consistent, with conflict handling if the user selects a different option. |
| Q11 | K1. A selected plugin missing inside the promised activation scope should stop startup and identify the broken opt-in, preserving enforcement. |

Q11 may remain separate: Q01 chooses the activation scope, and Q11 chooses failure behavior within that scope. Their relation should be explained when obtaining human decisions. Under A1, startup failure is already part of that option, so K2 or K3 would require reconciling the conflicting answers; under A3, a prepared-run K1 can coexist with warning-and-continuing outside that scope only if that qualification is made explicit. These are consequences of alternative combinations, not confirmation of A2/K1.

Wording-only suggestions: in Q11, qualify the statements about outside environments with "under proposed option A2". For sharper distinction, describe K2 as continuing with neither selected policy enforced and K3 as continuing with the available selected policy when both were selected. When only one policy was selected, those permissive outcomes coincide. The preferred K1 is unambiguous already.

### Convergence evidence for feature-request shared_lifecycle_gate round 2

Covered wording:

Covered formulation: the full working-tree requirement with SHA-256 177b4ad77dff0a7fe0f4a3faa91311275365a7085ba84d521d5e7f36b624ea50, including Q01-Q11 and their proposed answers. Current-body baseline wording remains intentionally distinct from changes conditional on pending answers. The activation, evidence, platform, audit-window, exemption, exception, adoption, validation, compatibility, defaults and activation-failure choices are all covered.

This assessment covers the current reviewed document and the exact published round 2 request; it does not claim implementation validation, private project trial evidence, or approval of future human choices.

Convergence rationale:

All substantive round 1 findings are resolved in the current formulation, and the requestor's change report matches the document. The options expose material tradeoffs, the proposed recommendations follow the stated unchanged-contract and adoption goals, and the runtime-support recommendation now demands appropriate evidence. No additional in-scope question is required before the human considers the eleven pending choices. Remaining scope qualification and option-boundary edits are wording-only.

Convergence is advisory. The requestor must retain the human gate; the reviewer neither confirms it nor authorizes the owning action.

### Writer instructions for feature-request shared_lifecycle_gate round 2

No substantive automatic revision remains. Preserve all eleven pending user decisions and the requirement baseline until the human chooses. Present the proposed answers and their consequences through the existing requestor workflow; do not interpret this reviewer recommendation as consolidation authority.

Optional wording polish is limited to making Q11's outside-scope statements conditional on A2 and sharpening K2/K3 as described in the verdicts. If the human chooses a different activation scope, reconcile its interaction with the failure answer explicitly. A later user decision can create a new conflict even though the current proposed formulation converges.

Any implementation, trial, or consolidation remains outside this reviewer handoff. The reviewer will wait globally after publication.

### Final reviewer decision for feature-request shared_lifecycle_gate round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

### LLM nature override for requestor (exchange 1)

Human-approved Override: the requestor continues as `codex` instead of `claude`.

Previous nature: `claude`

Recorded nature: `codex`

<!-- review-entry-id: llm-nature-override-requestor-exchange-1-claude-to-codex -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-04T20:10:18+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: # Verbatim user guidance for the shared lifecycle gate decisions

Let's got for A2, but add more detail when explaining the other questions.

D1

E2

F1

G1, make sure all those values are configurable

H3

I1

J1

K1

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-04T20:11:01+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 3

### Requestor assessment for feature-request shared_lifecycle_gate (round 3)

#### Writer assessment for the decided shared lifecycle gate requirement for feature-request shared_lifecycle_gate (round 3)

All eleven original questions now have explicit user decisions. The full
decision scan reports zero undecided questions and no diagnostics. The
requirement passes Markdown validation. This round reviews the complete
specification, all recorded decisions and qualifications, and consequences
for related documents before any consolidation.

The current body intentionally retains the pre-decision baseline. Its Python
3.12 support, tracked addopts activation and unconditional process prohibition
must be read with the explicit B3, A2 and E2 decisions recorded below. Those
baseline changes await authorized consolidation; the historical B1 and E1
recommendations are preserved rather than rewritten as user choices.

Existing options were sufficient to record the user's eleven choices. The
main possible missing requirement-level decision is E2's interaction with D1:
per-test exemptions and attributed shared fixture setup/teardown may need a
clear permission rule. Please independently determine whether an additional
question is required, including any other gaps introduced by the decisions.
An exemption feature does not itself authorize subprocess-based tests in
llm-shared's own suite. H3's temporary activation without consumer-file changes
must be achievable, while its mechanism remains future design work.

Round 2's covered wording suggestions for Q11 were applied: outside-scope
statements are conditional on A2; K2 means neither selected policy; K3 retains
the available selected policy, with the single-selection case distinguished.
These edits preceded the user discussion and are included in this review.

Please assess full-specification consistency, sufficiency of options and
answers, effects on earlier decisions and associated documents, missing or
new questions, and whether the record-preservation and validation promises
are clear. User decisions are authoritative; surface any conflict rather
than replacing a confirmed choice with a reviewer recommendation. No
implementation, consuming-project trial, consolidation, staging or commit
is authorized by this handoff.

### Change summary for feature-request shared_lifecycle_gate (round 3)

#### Changes since shared lifecycle gate round 2 convergence for feature-request shared_lifecycle_gate (round 3)

- Q01 A2: project opt-in is automatically applied in the prepared shell and
  every groundhog test stage. Outside runs receive no automatic activation;
  explicit loading remains possible.
- Q02 B3: minimum Python 3.13; no Python 3.12 support or validation obligation.
  Preserve the historical B1 recommendation until consolidation.
- Q03 C3: validate Windows; portable API intent with Linux/macOS explicitly
  unvalidated for this release.
- Q04 D1: enforce the process audit during setup, call and teardown, including
  attributed shared fixtures; collection, collection-time conftest imports
  and worker startup remain outside enforcement.
- Q05 E2: per-test process-audit exemption with a required reason and listing
  at the end of every run; no timing exemption. Preserve historical E1.
- Q06 F1: keep ignored per-checkout CPU exceptions with the unchanged cpu,
  attempted and reason fields, without a tracked second source.
- Q07 G1: immediate enforcement with no report-only mode or automatic grace.
  User explicitly requires all four settings configurable. The answer records
  finite positive CPU/wall limits, finite band factor at least 1, whole drift
  count at least 1, and command-line/project/default precedence.
- Q08 H3: repeatable in-process isolation checks plus a temporary consuming
  trial covering prepared-shell pytest and groundhog. Change no consumer
  files, enable nothing persistently, name no consumer publicly. Evidence is
  Python 3.13 on Windows; the old Python 3.12 evidence suggestion is superseded.
- Q09 I1: preserve valid records, accepted exception meaning and eligible
  proofs across extraction; validate llm-shared's own record continuity.
  Later contract changes document compatibility or migration behavior.
- Q10 J1: retain defaults of 0.1 seconds CPU, 1 second wall, factor 2.5 and
  3 drift runs, with all four configurable under G1.
- Q11 K1: prepared opted-in runs fail at startup if any selected plugin cannot
  import, naming the plugin and the opt-in. No partial selected enforcement.
- Q11 also includes the covered wording changes from the retained round 2
  answer, clarifying A2 scope and K2/K3 outcomes.

All question IDs, options, recommendations and historical explanations remain.
Only explicit answer records and their qualifications were added during the
human discussion. No consolidation or implementation was performed.

### Human guidance and writer response for feature-request shared_lifecycle_gate (round 3)

Human guidance:

#### Verbatim user guidance for the shared lifecycle gate decisions for feature-request shared_lifecycle_gate (round 3)

Let's got for A2, but add more detail when explaining the other questions.

D1

E2

F1

G1, make sure all those values are configurable

H3

I1

J1

K1

Writer response:

#### Writer response for shared lifecycle gate post-decision review for feature-request shared_lifecycle_gate (round 3)

The round 2 recommendation converged on the question formulations before
human decisions. Its evidence does not cover the subsequent choices. This
authorized replacement round requests independent review of all decisions
and comments, not repetition of the original recommendation.

The user selected B3 instead of the historical B1 and E2 instead of E1.
Those explicit choices control the eventual requirement; old proposals remain
visible as history. All other selections match the proposed answers, with
the user's explicit requirement that all four numerical settings remain
configurable. The answer records preserve dates and qualifications.

No disagreement with the prior review is asserted: differing human choices
are new requirements to assess. Please identify any additional decision
needed for a coherent E2 exemption contract, especially shared fixtures under
D1, and check whether any chosen combination creates a conflict elsewhere.
Do not infer that new questions have user decisions. Technical packaging,
activation injection and implementation details remain design work.

The writer will assess feedback and preserve every confirmed choice and
question block. The review must end at the human convergence gate; it grants
no consolidation authority.

### Reviewer focus for feature-request shared_lifecycle_gate (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

### LLM nature override for reviewer (exchange 1)

Human-approved Override: the reviewer continues as `claude` instead of `codex`.

Previous nature: `codex`

Recorded nature: `claude`

<!-- review-entry-id: llm-nature-override-reviewer-exchange-1-codex-to-claude -->

## Round 3 by reviewer

- Recorded: 2026-11-05T08:08:44+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 3

I read the complete current specification (SHA-256
`e450283a44d3e9cda335a6c3425992b520443f8061798c91a5ff8a1d42750c04`), the
round 3 request, and the code the specification cites as its current
behavior: `tests/simulation_policy.py`, the validation in
`tests/lifecycle_cpu_record.py` and the pytest options in `pyproject.toml`.

**Overall verdict.** The eleven recorded decisions agree with one another
within their own scope, and the user's choices B3 and E2 are recorded as
superseding the historical B1 and E1 proposals without erasing them. That
part of the record is sound. Implementation cannot yet proceed from it,
though: E2 leaves three observable behaviors undefined, B3's word "require"
has two readings with different outcomes, and E2 combined with A2 breaks
A2's promise for runs outside the prepared environment unless the
requirement states how the exemption marker is registered. I request four
new questions (Q12 to Q15) and a set of recorded consequences, so this round
returns `changes-requested`. None of the findings replaces a user decision.

**Finding 1, the E2 and D1 interaction the writer flagged, is real and
order dependent.** `reject_process` in `tests/simulation_policy.py` blames
`_ACTIVE[-1]`, the test whose `pytest_runtest_protocol` is running. pytest
sets up a module- or session-scoped fixture inside the setup of the first
test that requests it, and runs its teardown inside the teardown of the
last test before its scope ends (for a session fixture, the last test of
that process). If an exemption follows that attribution, a
shared fixture that starts a process passes when an exempt test reaches it
first and errors when a test without exemption does; pytest then reports
that cached setup error for every test using the fixture, the exempt one
included. Under pytest-xdist each worker sets the fixture up separately, so
the result also changes with the distribution. The same holds for shared
teardown work. This needs a requirement-level decision: new Q12.

**Finding 2, E2 does not say where the marker may be placed or what a
missing reason does.** A pytest mark on a class or module (`pytestmark`)
reaches every test inside it, including tests added later. That is exactly
the coarseness for which E3 (path patterns) was not chosen. New Q13.

**Finding 3, A2 combined with E2 breaks outside runs unless the marker is
registered by the project.** Under A2, runs outside the prepared environment
load no plugin automatically, and a gate-only run never loads the audit. A
marker that only the audit plugin registers is then unknown: with
`--strict-markers` (llm-shared's own `addopts` in `pyproject.toml` carries
it) collection fails; without it pytest warns about an unknown mark, which a
warnings-as-errors setting turns into a failure. Q01's confirmed record says
other environments keep working without llm-shared. Only one answer keeps
that promise, so I record it as a consequence inside Q13 rather than as a
separate choice: the documented opt-in has the project register the marker
in its tracked pytest `markers` setting, and the marker has no effect where
the audit plugin is not loaded.

**Finding 4, E2's end-of-run listing is unspecified.** Which exempt tests
appear (collected or run), what each line shows, whether a gate-only run
shows a list, who writes it under xdist, and what happens to an exemption
whose test no longer starts a process are all open. The last point is how
E2's own con (an escape that weakens over time) would show. New Q14.

**Finding 5, B3's "require" has two observable readings.** It can be a
documented support floor, or a load-time check that stops an older
interpreter. One consuming project runs Python 3.12; if it declared the
opt-in, the readings differ between an unvalidated run (or an unrelated
import error) and a named startup stop. A check exercised on 3.13 by
simulating the version is not 3.12 validation, so either reading is
compatible with "no 3.12 validation". New Q15.

**Finding 6, the CPU clock does not see child processes.** The lifecycle
CPU is `time.process_time()` of the test process. A process started by an
exempt test, or by any test in a gate-only run, does its CPU work outside
every test's budget; only the wall limit bounds the wait for it. E2's
qualification "the exemption does not grant a CPU or wall-time exception"
is true but can be read as if the child's cost were still budgeted. The
requirement should state the measurement boundary. No alternative is
practical within C3 (Windows has no portable child-CPU accounting through
the standard library), so this is a statement, not a question.

**Finding 7, A2 and gap item 7 need two acceptance statements.** llm-shared
keeps loading both plugins through `tests/conftest.py`, which A2 allows
("explicit loading remains possible"). Two consequences follow. First, a
plugin selected twice in one run (by the opt-in activation and explicitly)
must load once, with no duplicate-registration error and no doubled
summary or exemption list. Second, llm-shared's own suite does not exercise
the A2 activation or the K1 startup failure by loading through `conftest.py`,
so their repeatable evidence must come from in-process tests of the
activation logic in `tools`, beside H3's one-off trial. That follows from the
existing 100% coverage gate on `tools`, but the acceptance criteria should
name it so that H3's "isolation checks" are not read as the only repeatable
evidence.

**Finding 8, K1 needs an observable acceptance signal.** The criterion
should say the run stops before any test runs, with a non-zero exit and a
message naming the plugin and the opt-in. I propose the existing usage-error
exit code 4 for consistency with gap item 6; that is a reviewer proposal for
the writer and user to confirm, not a recorded decision. Naming the opt-in
means the activation layer, not a bare `-p`, reports the failure; how stays
design work.

**Finding 9, llm-shared's own suite should declare no exemption.** The
writer already notes that E2 does not authorize process-starting tests in
llm-shared. An acceptance criterion should make it checkable: llm-shared's
whole-suite run lists no exemption.

**Finding 10, stale cross-references and one incomplete baseline line
(wording only).** Q01's user comment says "Q11's missing-plugin behavior
remains undecided", Q02's record says Q08's "consuming-environment
validation choice remains open", and Q11's description speaks of "Q01's
recommended answer" and "proposed option A2". All three were later settled
(K1, H3, A2). The "Current behavior" bullet on rejected values omits that a
non-finite band factor or drift count is also refused, which
`setting()` in `tests/lifecycle_cpu_record.py` does for every key; the G1
table is therefore consistent with today's code, and only that bullet is
incomplete.

**Checked and consistent.** C3 with H3 (evidence on Windows, Python 3.13);
D1 with the CPU window (both cover setup, call and teardown); F1 with E2 (CPU
exceptions stay per checkout, exemptions are tracked test code, different in
nature and both preserved); G1 with J1 and gap item 6 (all four keys, their
finite validation and the `-o`, configuration, default precedence exist
today); I1 with F1 (record continuity keeps per-checkout exceptions); K1 with
A2 (failure only in prepared runs); gap item 10 with H3 (no consumer named).

### Question verdicts for feature-request shared_lifecycle_gate round 3

Every existing question is in scope, its options are distinct and its
recorded user decision is explicit and dated. Below, "my choice" is the
answer I would choose today knowing the user's decisions; it never replaces
them.

- Q01, A2 (user decision confirmed). Agree; my choice A2. Consequences:
  outside runs must not be broken by E2 markers (Finding 3, folded into new
  Q13), and a plugin selected twice must load once (Finding 7).
- Q02, B3 (user decision confirmed, supersedes historical B1). I recommended
  B1 earlier because the requirement then promised 3.12; with the user's
  statement that 3.12 is not a priority, B3 is coherent and removes the most
  expensive validation item. My choice now B3. Open consequence: what
  "require" does on an older interpreter (new Q15). The record's sentence
  that Q08's validation choice "remains open" is stale (H3 is decided).
- Q03, C3 (confirmed). Agree; my choice C3. Consistent with H3's Windows,
  Python 3.13 evidence.
- Q04, D1 (confirmed). Agree; my choice D1. The window is correct; how an
  E2 exemption treats shared-fixture work attributed to it is the open part
  (new Q12).
- Q05, E2 (confirmed, supersedes historical E1). I recommended E1 earlier;
  E2 is a legitimate user choice and conflicts with no other decision once
  Q12 to Q14 settle its contract and the marker registration of Finding 3 is
  stated. Given E2, my choices are L1, M1 and N2 below. The qualification
  on timing should also state that a child's CPU is never measured
  (Finding 6).
- Q06, F1 (confirmed). Agree; my choice F1. Exemptions (tracked test code)
  and CPU exceptions (per-checkout record) stay separate.
- Q07, G1 with all four settings configurable (confirmed). Agree; my choice
  G1. The table matches today's validation exactly: `setting()` refuses a
  non-finite value for every key. Only the "Current behavior" bullet needs
  to mention non-finite factor and drift values (wording).
- Q08, H3 (confirmed). Agree; my choice H3. The repeatable side should also
  cover the activation logic and K1's failure in-process (Finding 7) and the
  exemption behaviors of Q12 to Q14.
- Q09, I1 (confirmed). Agree; my choice I1. Needs its acceptance criterion
  for llm-shared's own record continuity at consolidation.
- Q10, J1 (confirmed). Agree; my choice J1. Consistent with G1.
- Q11, K1 (confirmed). Agree; my choice K1. Needs an observable acceptance
  signal (Finding 8). Its description still calls A2 "proposed" (wording).

Missing questions, all arising from the recorded decisions:

- Q12: what an exemption covers when shared fixtures start processes. My
  choice L1 (the exempt test's own call and function-scoped fixtures only).
- Q13: what makes an exemption marker valid, with project-side marker
  registration stated in every option. My choice M1 (function or
  parametrized case only; misplaced or unexplained marker is a usage error at
  collection).
- Q14: what the end-of-run exemption list reports. My choice N2 (exempt
  tests that ran, with reason, unused exemptions flagged but not failed).
- Q15: what the Python 3.13 requirement does on an older interpreter. My
  choice O2 (load-time check with a usage error), with O1 acceptable if the
  user wants no code for 3.12 at all.

None of Q12 to Q15 has a user decision; each must start at
`User decision: pending`.

### Requested changes for feature-request shared_lifecycle_gate round 3

Requested changes:

1. Add Q12, Q13, Q14 and Q15 after Q11, using the blocks below (or an
   equivalent formulation). Each starts at `User decision: pending`. The
   blocks follow the document's existing detailed format, as the user asked
   for in the Q01 comment.
2. Record the consequences listed after the blocks next to the decision each
   one follows from, labelled as review consequences pending consolidation,
   never as user decisions. Do not change any confirmed choice or the user's
   words.
3. Correct the stale cross-references with a dated note rather than by
   rewriting the record: Q01's comment ("Q11's missing-plugin behavior
   remains undecided", later decided K1), Q02's record ("its
   consuming-environment validation choice remains open", later decided H3),
   and Q11's description ("Q01's recommended answer", "proposed option A2",
   later confirmed A2).

Proposed Q12 block:

```markdown
### Q12: What an exemption covers when shared fixtures start processes

Question description: added after the round 3 review of the recorded
decisions. Q04's D1 charges shared-fixture work to the test whose lifecycle
is running. pytest sets up a module- or session-scoped fixture inside the
setup of the first test that requests it, and tears it down inside the
teardown of the last test before its scope ends (for a session fixture, the
last test of the process). Q05's E2 exempts single tests. If an exemption
follows D1's attribution, a shared fixture that starts a process passes when
an exempt test reaches it first, and errors when a test without exemption
does; pytest then reports that cached setup error for every test using the
fixture, the exempt one included. Under pytest-xdist each worker sets the
fixture up separately, so the result also changes with the distribution.
Shared teardown work behaves the same way. The requirement does not say
which process starts an exemption covers. Whatever the answer, the CPU clock
(`time.process_time`) counts only the test process: a child process's CPU is
outside every test's budget, and only the wall limit bounds the time an
exempt test waits for it.

#### BBQ for Q12

The patio's no-flame rule has one signed note for the family's old fire pit.
Lighting the pit also lights the shared patio heater. If the note covers
anything that happens while the pit is in use, the heater passes on the days
the pit is lit first, and breaks the rule on the days a guest switches the
heater on earlier. The family can tie the note strictly to the pit, accept
that the heater's verdict depends on who arrives first, or sign a second
note for the heater itself. In this picture: the patio rule is the process
audit, the signed note is a test's exemption marker, the fire pit is the
exempt test's own work, the patio heater is a module- or session-scoped
fixture that starts a process, who arrives first is the test order or the
xdist distribution, and the second note is a fixture-level exemption.

#### Options for Q12

- Option L1: an exemption covers only the exempt test's own work: its call
  and the setup and teardown of the function-scoped fixtures it requests.
  Work of a broader-scoped fixture is never exempt, whichever test triggers
  it.
  - pro: deterministic: the same suite gives the same audit result in every
    order and distribution.
  - pro: keeps E2 a strictly per-test exemption.
  - con: a project that starts a process in a shared fixture (for example a
    server started once per session) must move that start into the exempt
    test or a function-scoped fixture, paying it per test, or take the gate
    without the audit.
- Option L2: an exemption covers everything D1 charges to the exempt test's
  lifecycle, shared-fixture setup and teardown included.
  - pro: the simplest rule; it follows D1's attribution exactly.
  - con: the same commit can pass or fail the audit depending on test order
    and xdist distribution.
  - con: shared work a test without exemption depends on can pass only
    because an exempt test happened to trigger it.
- Option L3: L1, plus a fixture-level exemption marker with its own required
  reason, also listed at the end of every run; an exempt shared fixture may
  start processes whichever test triggers it.
  - pro: deterministic, and supports process-starting shared fixtures.
  - con: a second exemption form beyond E2's per-test marker, with its own
    contract and tests.
  - con: one fixture exemption covers every test using that fixture.

#### Recommended option for Q12 (with arguments for this choice)

Option L1: an audit whose result changes with test order cannot be trusted
when it fails, which rules out L2. L1 is the reading of E2 that keeps the
exemption per test, and its cost falls only on projects that start processes
in shared fixtures, which can still take the gate alone. L3 extends E2 to a
second exemption form; it can be decided later if a real project needs it.

#### Answer to Q12: option L1 (with reason why it must be accepted as the answer)

Option L1: the requirement then states that an exemption covers the exempt
test's call and its function-scoped fixtures, that a process started by a
module-, class-, package- or session-scoped fixture fails in every test, and
that a child process's CPU is not measured while the wall limit still
applies. How the plugin tells shared-fixture work apart stays design work.

User decision: pending
```

Proposed Q13 block:

```markdown
### Q13: What makes an exemption marker valid

Question description: added after the round 3 review. E2 asks for a per-test
marker with a required reason. pytest marks also apply to a whole class or
module (`pytestmark`) and to one parametrized case
(`pytest.param(..., marks=...)`), and a class or module mark reaches every
test inside it, including tests added later. That is the coarseness for
which E3 (path patterns) was not chosen. The requirement does not say where
the marker may be placed, or what a missing or empty reason does.
Separately, a marker known only to the audit plugin is unknown wherever that
plugin is not loaded: in a run that takes the gate alone, and, under Q01's
A2, in every run outside the prepared environment. With `--strict-markers`
such a run fails collection; without it, pytest warns about an unknown mark,
which a warnings-as-errors setting turns into a failure. A2 promises that
those environments keep working, so in every option below the documented
opt-in has the project register the marker in its tracked pytest `markers`
setting, and the marker has no effect where the audit plugin is not loaded.

#### BBQ for Q13

The signed fire-pit note can be pinned to the pit itself, to the backyard, or
to the whole house. A note on the house also covers every pit built later,
without anyone signing again. A note whose reason is left blank can be
refused, or the pit can be lit anyway with a grumble. Guests who do not
follow the patio rule must still be able to read the note without being
confused by it. In this picture: the pit is one test function or
parametrized case, the backyard is a test class, the house is a test module,
a later pit is a test added to that class or module, the blank reason is a
marker without a non-empty reason, the grumble is a warning, and the guests
are runs where the audit plugin is not loaded.

#### Options for Q13

- Option M1: the marker counts only on a test function or one parametrized
  case; a class- or module-level exemption mark, or a marker without a
  non-empty reason, stops the run at collection with a usage error naming
  the test.
  - pro: every exemption names one test and its reason; no test becomes
    exempt by being added to a file.
  - pro: a misplaced or unexplained exemption is caught before any test runs,
    pointing at the line to fix.
  - con: a module with several process-starting tests repeats the marker on
    each.
- Option M2: the marker counts wherever pytest marks apply, class and module
  included; a missing or empty reason stops the run at collection.
  - pro: familiar pytest behaviour; one line exempts a whole end-to-end
    module.
  - con: brings back E3's coarseness: a new test in an exempted module is
    exempt without review.
- Option M3: placement as in M1, but a class- or module-level mark or a
  missing reason only warns, and the test stays audited.
  - pro: never blocks a run.
  - con: the mistake shows up later as an audit failure, after a warning that
    is easy to miss.

#### Recommended option for Q13 (with arguments for this choice)

Option M1: E2 was chosen over E3 as a reviewed escape for a named test. M1
keeps that property, and a collection-time usage error, like the existing
one for invalid `test_lifecycle_*` values, names the line to fix. The
repetition it costs is the visible review the exemption is meant to carry.

#### Answer to Q13: option M1 (with reason why it must be accepted as the answer)

Option M1: the requirement then states that the exemption marker counts only
on a test function or a parametrized case, that a class- or module-level
exemption mark or a missing or empty reason stops the run at collection with
a usage error naming the test, that the opt-in how-to has the project
register the marker in its tracked pytest `markers` setting, and that the
marker has no effect in runs without the audit plugin.

User decision: pending
```

Proposed Q14 block:

```markdown
### Q14: What the end-of-run exemption list reports

Question description: added after the round 3 review. E2 lists exemptions at
the end of every run. The requirement does not say which tests appear (every
collected exempt test, or only those that ran), what each line shows,
whether a run without the audit plugin shows a list, or what happens to an
exemption whose test no longer starts a process. That last case is how E2's
own con, an escape that weakens over time, would show: a test is converted,
its exemption stays, and nothing says so. Under pytest-xdist, as for the
lifecycle record, only the controller sees the whole run.

#### BBQ for Q14

At the end of each cookout, the host reads out the signed fire-pit notes.
The host can read every note on file or only the notes for pits used that
day, can also say which of those pits stayed cold, or can tear up the note
of a pit that stayed cold. In this picture: the cookout is one pytest run
with the audit plugin loaded, the notes on file are exemption markers, the
pits used that day are exempt tests that ran, a pit that stayed cold is an
exempt test that started no process in this run, and tearing up the note is
failing that test.

#### Options for Q14

- Option N1: one end-of-run list, written once by the controller under
  xdist, of the exempt tests that ran, each with its reason; shown only when
  the audit plugin is loaded.
  - pro: short and stable; the minimum E2 asks for.
  - con: an exemption that is no longer needed goes unnoticed.
- Option N2: N1, and each line says whether that test started a process in
  this run; an unused exemption is flagged, never failed.
  - pro: makes the weakening visible and points at exemptions to remove.
  - con: a test that starts a process only on some platforms or inputs is
    flagged on the runs where it did not; worker reports carry one more fact.
- Option N3: N1, and an exempt test that starts no process fails, like a
  strict expected failure.
  - pro: no stale exemption survives.
  - con: a test that starts a process only sometimes fails on the other runs.

#### Recommended option for Q14 (with arguments for this choice)

Option N2: it answers E2's main risk without adding a failure mode. N1
leaves stale exemptions invisible, and N3 turns a conditional process start
into a failing test. Listing only tests that ran keeps the list true for
selected runs, and the controller-only write matches the record rule.

#### Answer to Q14: option N2 (with reason why it must be accepted as the answer)

Option N2: the requirement then states that a run with the audit plugin
ends with one list of the exempt tests that ran, each with its reason and
whether it started a process in that run, written once by the controller
under pytest-xdist; that an unused exemption is flagged and never fails; and
that a run without the audit plugin shows no exemption list.

User decision: pending
```

Proposed Q15 block:

```markdown
### Q15: What the Python 3.13 requirement does on an older interpreter

Question description: added after the round 3 review. Q02's B3 says the
plugins require Python 3.13 and removes the 3.12 promise and its
validation. It does not say whether "require" is a documented support floor
or a check at load time. The difference is observable: one consuming project
runs Python 3.12. If it declared the opt-in, its prepared runs would, without
a check, load plugins whose behaviour on 3.12 is unvalidated, or fail at
import with an unrelated error that Q11's K1 diagnostic would report; with a
check, they would stop at startup with a message naming the required
version. A check tested on 3.13 by simulating an older version is not 3.12
validation, so both readings fit B3.

#### BBQ for Q15

A new grill says "for gas bottles made from 2024 on". The label can be
advice only, so an older bottle may fit and may leak, or the valve can
refuse older bottles with a tag saying why. In this picture: the grill is
the plugin pair, a 2024 bottle is Python 3.13, an older bottle is Python
3.12, advice only is a documented support floor without a check, and the
refusing valve is a load-time version check that stops the run with a
message.

#### Options for Q15

- Option O1: a documented floor only: the plugins support Python 3.13 and
  later; on an older interpreter their behaviour is unspecified and nothing
  checks the version.
  - pro: no code and no test; the lightest reading of B3.
  - con: an opted-in project on 3.12 may get unvalidated enforcement that
    looks valid, or an import error that does not name the cause.
- Option O2: a load-time check: on Python older than 3.13, loading either
  plugin stops pytest at startup with a usage error naming the plugin and
  the required version.
  - pro: the same principle as K1: no quiet, unvalidated enforcement, and
    the message says what to change.
  - pro: tested in llm-shared's own suite on 3.13 by simulating the version,
    with no second interpreter.
  - con: a little code and one test for a version the user does not
    prioritize; a 3.12 project that would have worked is stopped.

#### Recommended option for Q15 (with arguments for this choice)

Option O2: the user chose K1 so that a prepared run never carries less
enforcement than the opt-in promises without saying so; O2 applies the same
rule to an unsupported interpreter for the cost of one check and one test.
O1 is acceptable if the user prefers no code at all for Python 3.12.

#### Answer to Q15: option O2 (with reason why it must be accepted as the answer)

Option O2: the requirement then states that loading either plugin on Python
older than 3.13 stops pytest at startup with a usage error naming the plugin
and the required version, and gap item 5 says Python 3.13 and later.

User decision: pending
```

Consequences to record now, pending consolidation (each is a reviewer
proposal for the writer and user to confirm, not a user decision):

- With Q01 A2 and gap item 7: a plugin selected twice in one run (by the
  opt-in activation and by explicit loading, as in llm-shared's own
  `tests/conftest.py`) loads once, with no duplicate-registration error and
  no doubled summary or exemption list.
- With Q01 A2, Q11 K1 and Q08 H3: the activation logic in the prepared shell
  and groundhog, and K1's startup failure, have repeatable in-process tests
  in llm-shared's suite, counted by the 100% coverage gate on `tools`; H3's
  trial adds the real-environment confirmation.
- With Q11 K1: the acceptance criterion says the run stops before any test
  runs, with a non-zero exit and a message naming the plugin and the opt-in.
  Proposed: the existing usage-error exit code 4, as for invalid
  `test_lifecycle_*` values.
- With Q05 E2: llm-shared's own whole-suite run lists no exemption; the
  audit-only acceptance criterion allows the exemption list while keeping
  "no `lifecycle CPU band` summary"; the first acceptance criterion becomes
  "a project that has not opted in" and also shows no exemption list.
- With Q05 E2 and the gate-only path of gap item 2: a child process's CPU is
  outside the test process clock; only the wall limit bounds it.
- With Q07 G1: the "Current behavior" bullet on refused values also names a
  non-finite band factor and a drift count that is not a finite whole number,
  matching `setting()` in `tests/lifecycle_cpu_record.py`.

### Human guidance response for feature-request shared_lifecycle_gate round 3

Human guidance:

Let's got for A2, but add more detail when explaining the other questions.

D1

E2

F1

G1, make sure all those values are configurable

H3

I1

J1

K1

Guidance response:

The user's choices are treated as authoritative. B3 and E2 differ from the
historical recommendations; this review does not contest them and instead
reports what they require elsewhere (Q12 to Q15 and the recorded
consequences).

G1's configurability is satisfied by the current contract and by the
recorded answer: all four `test_lifecycle_*` keys are pytest ini settings
today, each takes a `-o` override over project configuration over the plugin
default, and each refuses a non-finite or out-of-range value with exit code
4. The G1 table matches that validation; J1's defaults fit within it.

The request for more detail when explaining questions is applied to the new
questions: each proposed block has a concrete description of the failure it
prevents, a BBQ picture with its mapping, options with tradeoffs, a
recommendation and its effects on the decided questions. The guidance does
not decide Q12 to Q15; they remain pending until the user chooses.

### Writer instructions for feature-request shared_lifecycle_gate round 3

1. Apply the requested changes: add Q12 to Q15 at `User decision: pending`,
   record the listed consequences next to their decisions as review
   consequences pending consolidation, and add dated notes to the three stale
   cross-references. Keep every confirmed choice, the user's words, the
   historical B1 and E1 proposals and every existing question block intact.
2. Do not mark Q12 to Q15 decided from this review, and do not consolidate.
   Present them to the user with the same level of explanation the user
   asked for in the Q01 comment (concrete example, option tradeoffs,
   recommendation and effects on other questions).
3. Run the Markdown validation on the requirement after the edits; the new
   blocks use the document's existing heading pattern and need unique
   headings.
4. Request another automated review round on the new formulation. The next
   round should check Q12 to Q15 and the recorded consequences, and, if the
   user has decided any of them by then, the decisions too.
5. Keep this checklist for the later consolidation, once every question is
   decided, so the reviewer can verify it then:
   - gap item 1, gap item 8 and the first acceptance criterion: A2's opt-in
     declaration and prepared activation replace the bare `-p` in
     `addopts`; explicit loading stays possible;
   - gap item 2: a project may also exempt single tests under E2 and Q12 to
     Q14;
   - gap item 5: Python 3.13 and later (B3), with Q15's outcome;
   - gap item 9: the opt-in how-to covers the declaration, the marker
     registration of Q13, adoption with temporarily higher limits (G1), the
     note that only a full run without selection or early-stop options lists
     every offender, and C3's Windows validation statement;
   - acceptance criteria to add: A2 activation in the prepared shell and a
     groundhog stage; outside runs not activated; K1's startup failure;
     single load when selected twice; D1's enforcement window; E2 and Q12 to
     Q14 behaviors; llm-shared lists no exemption; I1's continuity of
     llm-shared's existing record; H3's trial recorded without naming the
     project; C3's documentation statement;
   - the "Current behavior" bullet on refused values (non-finite factor and
     drift count).

### Final reviewer decision for feature-request shared_lifecycle_gate round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-05T08:19:24+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 4)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 4

### Requestor assessment for feature-request shared_lifecycle_gate (round 4)

#### Writer assessment for the new exemption and interpreter questions for feature-request shared_lifecycle_gate (round 4)

The round 3 review identified requirement gaps introduced by the recorded E2
and B3 decisions. Q12 to Q15 now state those gaps, distinguish their options,
give detailed examples and mapped BBQ analogies, and propose answers without
claiming user approval. The fresh whole-document decision scan finds eleven
confirmed decisions and four undecided questions, Q12 through Q15, without
diagnostics. The requirement body and every historical question remain intact.

Q12 separates the enforcement window in D1 from the scope of a permission:
its proposed L1 exempts function-scoped work but leaves shared-fixture work
audited. Q13 addresses marker placement, missing reasons, and registration
when the audit is absent. Q14 specifies reporting and unused exemptions.
Q15 distinguishes a documented interpreter floor from a startup check.
The existing options are sufficient for the eleven recorded choices; the
four new questions need human decisions after their formulation converges.

The writer accepted all round 3 findings and recorded their consequences
next to the affected decisions, explicitly pending consolidation. The K1
non-zero-before-tests behavior follows its confirmed startup requirement;
exit code 4 remains labelled a reviewer proposal without user confirmation.
No user decision was changed or inferred from the reviewer recommendations.

Two small precision changes were made to the proposed blocks. A shared
fixture's process attempt fails the lifecycle carrying it, rather than
necessarily every dependent test, particularly for shared teardown. Wall
measurement bounds waits within the lifecycle, not a detached child's later
lifetime. M3 no longer claims a warning can never block a run: warning filters
and later audit failures still apply. Please verify those distinctions and
whether any additional behavior needs a user decision.

The private question companion now mirrors the full current question section,
including the eleven explicit decisions; it cannot restore stale pending
markers on a later append. The original completed explanation batch retains
its Q01-Q11 boundaries. Q12-Q15 are outside that batch and have not been
explained to or decided by the user in this resumed session.

Please assess the full specification, the sufficiency of the new options and
answers, the review consequences, the preservation of confirmed decisions,
and any missing requirement questions. H3's trial must remain temporary and
change no consumer files. Packaging, activation mechanisms and fixture-hook
implementation remain design work. No consolidation or implementation is
authorized.

### Change summary for feature-request shared_lifecycle_gate (round 4)

#### Changes after the round 3 shared lifecycle gate review for feature-request shared_lifecycle_gate (round 4)

Added Q12-Q15 as pending questions in the existing detailed format. Recorded
review consequences beside A2, E2, G1 and K1, including duplicate activation,
repeatable activation and failure evidence, marker registration, the
test-process CPU boundary, exemption summaries and no exemption in
llm-shared's own suite. Added dated clarifications for stale Q01, Q02 and
Q11 references, preserving the historical text and every confirmed decision.

Clarified shared teardown attribution, lifecycle wall measurement and M3's
warning behavior relative to the reviewer's proposed wording. The main
pre-decision body is unchanged pending authorized consolidation. The private
question companion is synchronized; no implementation, test execution,
consumer trial, consolidation, staging or commit was performed.

### Writer response for feature-request shared_lifecycle_gate (round 4)

Writer response:

#### Writer response to the round 3 shared lifecycle gate findings for feature-request shared_lifecycle_gate (round 4)

Accepted the four new questions and all identified consequences. Q12-Q15
remain at User decision: pending, with L1, M1, N2 and O2 as proposals only.
The eleven recorded choices, their qualifications, historical B1 and E1
recommendations, and the user's comments remain unchanged. Review notes
clarify stale references without rewriting the decision record.

The proposed Q12 answer now attributes shared-fixture rejection to the
lifecycle actually carrying that work; a teardown failure need not fail
every dependent test. The child-CPU clarification expressly limits wall
measurement to elapsed time inside the lifecycle. Q13's M3 tradeoff no
longer promises a warning cannot fail under warnings-as-errors. These are
precision corrections, not disagreement with the findings.

K1's proposed usage-error exit code 4 is recorded as unconfirmed review
guidance. Please determine whether it needs a separate explicit choice or
can be confirmed together with the relevant question discussion. No proposal
is promoted to a human decision by this request.

Please review the new formulations and full-specification consistency before
the human discussion resumes. A convergence recommendation will retain the
answer and return to the human gate with four undecided questions. It will
not authorize consolidation or implementation. No reviewer session was
started or contacted by this requestor.

### Reviewer focus for feature-request shared_lifecycle_gate (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-05T08:28:31+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 4

I read the complete current specification (SHA-256
`eeaa80fa4e532248f763bd9ee6409c4ec06836aad8eb1293758683f63175182a`) and the
round 4 request. The body above the open questions is unchanged, as the
writer states; every change sits in the question section.

**Round 3 findings are all applied.** Q12 to Q15 are present at
`User decision: pending` with the proposed L1, M1, N2 and O2 as proposals
only. The consequences sit next to A2, E2, G1 and K1, each labelled as
pending consolidation and not as a user decision. The three stale
cross-references carry dated clarifications, and the user's comments, the
historical B1 and E1 proposals and all eleven confirmed decisions are
intact.

**The writer's three precision changes are correct.**

- Q12's answer now says a shared fixture's process start "fails the
  lifecycle carrying it". That matches pytest: a setup error is cached and
  re-raised for every later test in that fixture's scope, while a teardown
  error is reported only on the teardown of the test that ends the scope.
  My round 3 wording blurred the two.
- The wall clarification under Q05 and in Q12 is correct: the wall limit
  measures setup-through-teardown time, waits for a child included, and
  says nothing about a detached child that outlives the test.
- M3's revised pro is accurate: a warning can still fail a run under
  warnings-as-errors, so "never blocks a run" was wrong.

**One sentence in Q12's description still uses the blurred wording
(wording only).** After the xdist sentence it says "Shared teardown work
behaves the same way". Read next to the cached-setup-error sentence before
it, this suggests a teardown failure also spreads to every dependent test,
which the answer now correctly denies. The covered wording gives a
replacement.

**M1's usage error under pytest-xdist needs to be named explicitly (wording
in the requirement, work in the design).** Under xdist the controller does
not collect; workers do. In the installed pytest-xdist, a worker that raises
a usage error during collection reports its own exit status through
`workerfinished`, and `DSession.worker_workerfinished` handles only status 2
specially, so the controller's exit code does not become 4 by itself. M1's
"stops the run at collection with a usage error" is still achievable (for
example by carrying the worker's verdict to the controller's exit status),
and gap item 5 already promises the same behavior with or without xdist.
Adding "with or without pytest-xdist" to M1 and its answer keeps the
promise visible to the design. O2's interpreter check and K1's startup
failure run before collection, on the controller, so they are not affected.

**K1's exit code 4 does not need its own question block.** M1 and O2
already propose a "usage error" for their refusals, and pytest's usage error
is exit code 4, the code invalid `test_lifecycle_*` values already use. One
consistent rule covers all four startup or collection refusals: invalid
settings (confirmed today), a selected plugin that cannot be imported (K1),
an invalid exemption marker (M1, pending) and an older interpreter (O2,
pending). The user can confirm that rule in one explicit line during the
Q12 to Q15 discussion; the alternatives (pytest's own import failure status,
or a generic failure code) have no tradeoff worth a full question. It must
still be an explicit user confirmation, recorded as a K1 qualification, not
inferred from Q13 or Q15.

**No further question is missing.** I checked the new questions against
each other and against the decisions: L1 with N2 (an exempt test whose
shared fixture starts a process fails under L1, and N2 still lists its own
use or non-use correctly); M1 with A2 (registration in the project's
`markers` setting keeps outside runs collecting); M1 with gate-only runs
(the marker has no effect, so a misplaced mark is caught only where the
audit is loaded, which is where it matters); O2 with A2 (outside runs that
do not load a plugin are unaffected; an explicit load on 3.12 stops, as
intended); O2 with K1 (an import failure is K1, a successful import on an
older interpreter is O2; both name the plugin); N2 with xdist (the
controller-only list mirrors the record rule). Packaging, the opt-in
declaration format, marker name and fixture-hook mechanics remain design
work, as the request states.

### Question verdicts for feature-request shared_lifecycle_gate round 4

Confirmed decisions (unchanged since round 3, all preserved):

- Q01 A2, Q03 C3, Q04 D1, Q06 F1, Q07 G1, Q08 H3, Q09 I1, Q10 J1, Q11 K1:
  agree; these are also my choices.
- Q02 B3 and Q05 E2: the user's choices over the historical B1 and E1;
  coherent with the rest once Q12 to Q15 are decided. My choices B3 and E2.
- The review consequences recorded under A2, E2, G1 and K1 are accurate and
  correctly labelled as pending consolidation, not as user decisions.

Pending questions (formulation reviewed; no user decision yet):

- Q12: in scope, options distinct (per-test only, follow attribution,
  add a fixture-level exemption), consequences stated. My choice L1. One
  description sentence needs the teardown precision already in the answer.
- Q13: in scope, options distinct, registration consequence correctly
  common to all options. My choice M1, stated as applying with or without
  pytest-xdist.
- Q14: in scope, options distinct. My choice N2.
- Q15: in scope, options distinct; correctly framed as compatible with B3
  either way. My choice O2, O1 acceptable if the user wants no code for 3.12.

Outstanding human decisions: Q12, Q13, Q14 and Q15, plus one explicit line
confirming (or rejecting) the reviewer-proposed exit code 4 for K1's startup
failure. No question is missing.

### Convergence evidence for feature-request shared_lifecycle_gate round 4

Covered wording:

1. Q12 description: replace "Shared teardown work behaves the same way."
   with:

   > Shared teardown work is order dependent in the same way: it runs in
   > whichever test ends the fixture's scope, and a failure there is
   > reported on that test's teardown only.

2. Q13 option M1 and the Q13 answer: after "stops the run at collection with
   a usage error naming the test", add "(exit code 4, with or without
   pytest-xdist)". Under xdist only the workers collect, so the design must
   carry a worker's verdict to the controller's exit status; the
   requirement only needs to keep the promise visible.

3. K1 review consequence: append one sentence so the user sees a single
   rule rather than four separate codes:

   > The same usage error (exit code 4) is proposed for every refusal before
   > tests run: invalid settings (today), a selected plugin that cannot be
   > imported (K1), an invalid exemption marker (Q13 M1) and an older
   > interpreter (Q15 O2). The user confirms it explicitly; it is not
   > inferred from the Q13 or Q15 decision.

Convergence rationale:

The question set is complete and consistent: every gap that the B3 and E2
decisions opened is now an explicit pending question with distinct options,
concrete consequences and a recommendation, and every consequence of the
eleven confirmed decisions is recorded without being promoted to a user
decision. The remaining edits are the three covered wording changes above;
none changes an option, a recommendation or a confirmed choice. The next
step belongs to the human: decide Q12 to Q15 and confirm or reject the
exit code 4 proposal for K1. Once those decisions are recorded, the
requirement still needs a follow-up review of the new decisions before
consolidation, as for the earlier batch. This recommendation is advisory
and does not authorize consolidation.

### Writer instructions for feature-request shared_lifecycle_gate round 4

1. Apply the three covered wording changes (Q12 teardown sentence, M1's
   xdist and exit code, the single usage-error rule under K1). They do not
   need another automated round.
2. Present Q12 to Q15 to the user with the detailed explanations the user
   asked for, and ask for an explicit yes or no on the exit code 4 proposal
   for K1. Record each answer only from the user's explicit choice.
3. Do not consolidate. After the user decides Q12 to Q15, request a
   follow-up review of those decisions before consolidation; keep the
   round 3 consolidation checklist for that review.

### Final reviewer decision for feature-request shared_lifecycle_gate round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-05T13:32:42+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: yes on K1 exit code 4. What's next?

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 5 by requestor

- Recorded: 2026-11-05T13:32:57+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 5)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 5

### Requestor assessment for feature-request shared_lifecycle_gate (round 5)

All fifteen questions now have explicit human decisions. The writer finds no
known missing question, subject to independent review of the interactions
below. Existing options, recommendations and explanations remain historical
review context; the explicit dated decisions govern where they differ.

Round 4's covered wording corrections were applied before this batch. The
new decisions are Q12 L3, Q13 M1 adapted to L3, Q14 N2 adapted to L3 and Q15
O2 amended to a Python 3.12 minimum. The user separately confirmed K1's
startup-import-failure exit code 4. The user also superseded Q02 B3:
Python 3.12 compatibility is mandatory because a current consumer requires
it. Q02 and Q08 now require executable 3.12 evidence alongside 3.13
validation, without changing llm-shared's own interpreter.

Please review the full specification and all explicit decisions and comments,
including effects on earlier decisions and related documents. In particular:

- L3: test-body/function-fixture permission versus a separate explicitly
  identified fixture permission, own reason, own reporting, shared setup and
  teardown, test-order independence and behavior with pytest-xdist.
- M1: validation of test and fixture declarations, rejection of blanket
  class/module test exemptions, strict-marker registration outside audit,
  identifying usage errors and exit code 4 with or without xdist.
- N2: each exercised test/fixture permission's own identity, reason and usage;
  fixture process starts are not credited to consuming tests; unused exercised
  permissions are flagged without failure; unexercised fixtures are excluded;
  one controller summary under xdist and no summary without audit.
- Restored 3.12 support: independent plugin loading and behavior, executable
  evidence without 3.13-only helpers, H3's two activation contexts, Windows
  scope, and O2 refusing only interpreters below the amended 3.12 minimum.
- K1: refusal before any test, explicit exit code 4, plugin and opt-in named,
  with repeatable evidence and no expansion of A2's prepared activation scope.

Identify contradictions, insufficient options or answers, and any additional
questions raised by these choices. Historical B3 and the old O2 threshold
are superseded, not competing active decisions. Fixture declaration and
aggregation mechanics remain design work. Do not replace user choices with
the earlier L1/B3 recommendations. No consolidation or implementation is
authorized in this round. No consumer identity may enter public documents.

### Change summary for feature-request shared_lifecycle_gate (round 5)

Since round 4 convergence:

- Recorded Q12 L3, preserving the historical L1 proposal and separating
  fixture permission from consuming test-body permission.
- Recorded Q13 M1 with L3 fixture declarations, required reasons, no blanket
  class/module test exemptions, pre-test usage errors with exit code 4 and
  marker registration for outside strict-marker runs.
- Recorded Q14 N2 with distinct exercised test/fixture reporting, own-scope
  process usage, non-failing unused-permission flags, controller aggregation
  and no reporting when audit is absent.
- Recorded Q15 O2, then applied the user's compatibility amendment: both
  plugins support Python 3.12 and later and refuse only versions below 3.12.
- Superseded Q02 B3 with mandatory 3.12 runtime compatibility, executable
  3.12 evidence independent of 3.13-only helpers and continued 3.13 validation.
  Updated the necessary Q08 dependency while retaining H3 and C3.
- Recorded the user's separate confirmation of K1's startup-import-failure
  exit code 4. Reconciled earlier statements that Q13/Q15 did not themselves
  authorize that qualification.

The full decision scanner reports 15 confirmed, zero undecided and no
diagnostics. The private companion matches the entire question section.
All question IDs, historical options and recommendations remain. No code,
consumer files, persistent activation, staging or commits were changed.

### Human guidance and writer response for feature-request shared_lifecycle_gate (round 5)

Human guidance:

yes on K1 exit code 4. What's next?

Writer response:

The writer accepted round 4's convergence recommendation on the question
formulations and applied its covered wording corrections. The user then
selected Explain, authorizing explicit decision recording and one follow-up
independent review. That authority is used for this replacement round;
consolidation remains unauthorized.

The user's L3 choice supersedes the historical L1 proposal. M1 and N2 were
explained and confirmed with L3's separate fixture permissions included.
The user corrected an ambiguous M2 response to N2; Q13 remains M1.

After selecting O2, the user explicitly required Python 3.12 compatibility
where a consumer needs it. Read-only inspection confirms a current consumer
declares a Python 3.12 constraint. Its identity and local details are omitted
from public review artifacts. This supersedes B3 and lowers O2's refusal
threshold to below 3.12; executable 3.12 compatibility evidence is required,
and simulating the version for the refusal path is insufficient by itself.
The consumer was not modified or upgraded. The shared tooling can remain on
3.13 while its exported plugins support 3.12.

The user separately confirmed K1 exit code 4. Its prepared opted-in boundary,
clear diagnostic and pre-test refusal remain unchanged. There is no explicit
writer/reviewer disagreement; these are new human decisions requiring a
fresh consistency review. Please surface conflicts rather than silently
overwriting any choice, and identify any genuinely new undecided questions.

### Reviewer focus for feature-request shared_lifecycle_gate (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-11-05T13:48:02+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 5

I read the complete current specification (SHA-256
`85d939f77a7dab93fe82dff20389bb523a8684ab590ce10220df7b080a44b7f0`) and the
round 5 request. Every change since round 4 sits in the question section;
the body above it is unchanged.

**The new decisions are recorded faithfully.** Q12 L3, Q13 M1, Q14 N2 and
Q15 O2 carry dated explicit decisions, and the historical L1 proposal, B3
decision and Python 3.13 floor stay visible as superseded history, not as
competing choices. Q02's compatibility decision and K1's exit code 4 are
recorded as the user's own statements, and the earlier notes that Q13 and
Q15 did not confirm K1's code are reconciled. Round 4's covered wording is
applied. No consuming project is named.

**L3 is deterministic and consistent with D1, M1 and N2.** A test
permission covers its call and its function-scoped fixtures; a separate
permission covers a shared fixture's own work. No audit verdict then depends
on which test reaches a fixture first or on the xdist distribution: a shared
fixture without permission that starts a process fails in every order, and
an exempt one passes in every order. Three precisions are still needed so
the design does not have to guess (wording, in the requested changes): what
a fixture's own work includes, which permission a process start is credited
to when both could apply, and how N2 reports a fixture permission exercised
several times in one run.

L3 grants no timing exception, as the user stated. The wall time of a
shared process start still counts toward whichever test triggers the
fixture, so a slow start can make that test's wall verdict depend on test
order and distribution. That is today's gate behavior for any shared
fixture, but L3 is the decision that invites process-starting shared
fixtures, so the requirement and the how-to should say so.

**A2 also binds the L3 fixture declaration (consequence, beyond wording).**
Q13 keeps the test marker harmless outside the audit by having the project
register it in its `markers` setting. The fixture declaration has no such
provision, and the obvious mechanisms break A2's promise that runs outside
the prepared environment keep working:

- pytest 9.1 refuses any mark applied to a fixture ("Marks cannot be applied
  to fixtures"), so the test marker cannot simply be reused;
- a decorator imported from the plugin fails to import wherever llm-shared
  is absent, so the project's own test files stop collecting there;
- a new pytest configuration key is reported as unknown by every run that
  does not load the audit plugin, which is a usage error under
  `--strict-config` or pytest's `strict` setting, and no project-side
  registration exists for configuration keys.

The mechanism remains design work, but the requirement must state the
constraint, as Q13 already does for the test marker.

**O2's refusal needs the version check to run before anything an older
interpreter cannot read (consequence).** pytest 9.1 still installs on Python
3.10 and 3.11 (its metadata says `Requires-Python >=3.10`). If code reached
before the check uses syntax or a standard-library import newer than the
running interpreter, a real Python 3.11 run fails at import instead of
refusing with the required version. Within K1's scope that is reported as a
plugin that cannot be imported, without the version; outside it, pytest
shows its own import error. The simulation the decision prescribes runs on
Python 3.13 and tests the version logic only; it cannot see this. A
repeatable static check of the code reached before the version check, for
example parsing it in process with the Python 3.10 grammar, closes the gap
without another interpreter.

**Restoring Python 3.12 support leaves one question open and adds one
design constraint.** Q02 requires executable 3.12 evidence for acceptance,
but does not say whether that evidence runs again when the plugins change.
That matters after acceptance. Consuming projects load the plugins from the
live checkout (Q09), and llm-shared's static checks treat `tools/` as
Python 3.13 code: Ruff takes its target from `requires-python = ">=3.13,
<3.14"`, and Pyright sets `pythonVersion = "3.13"`. Nothing would flag a
Python 3.13-only API added to a plugin later. On the 3.12 consumer, K1 would
then stop every prepared run before any test until llm-shared is fixed.
Either answer has a real cost (a second interpreter in routine validation,
or a promise that can lapse unnoticed), so this is a user question, proposed
as Q16, not a wording fix.

The same `requires-python` declaration means gap item 8's import route
cannot rely on installing llm-shared into a consuming project's 3.12
interpreter, or into the later interpreters that gap item 5's "and later"
includes. Q02's decision already keeps llm-shared's own interpreter
unchanged, so this is a consequence to state, not a new choice. The plugin
documentation should name the interpreters actually validated, 3.12 and
3.13, as C3 does for platforms.

**K1 is complete.** The qualification fixes the scope (prepared opted-in
runs only, with no expansion of A2), the stop before any test, exit code 4,
the named plugin and opt-in, and repeatable in-process evidence beside
H3's trial. Under pytest-xdist the controller loads the plugins before it
starts any worker, so the rule holds with or without xdist. pytest's own
failure to import a plugin cannot name the opt-in, so the design needs its
own loader step for this message; that is design work.

**Consolidation checklist.** Any step derived from B3 or from the earlier
O2 answer that would set gap item 5 to Python 3.13 no longer applies. Gap
item 5 keeps Python 3.12 and later, and the acceptance criteria gain the
Python 3.12 evidence on the schedule Q16 settles.

**Disposition.** One new user question (Q16) and three requirement
consequences (the fixture declaration under A2, the refusal before
unreadable code under O2, the import route outside llm-shared's own
interpreter range) go beyond wording. Another automated round should check
them once the writer has added them.

### Question verdicts for feature-request shared_lifecycle_gate round 5

Confirmed decisions:

- Q01 A2, Q03 C3, Q04 D1, Q06 F1, Q07 G1, Q09 I1, Q10 J1: agree; these are
  also my choices. Unchanged since round 4.
- Q02, compatibility decision of 2026-11-05 superseding B3: agree; it
  matches my original B1 choice and fits C3 (Windows validation), H3 (a
  shared run is allowed) and the amended O2. It leaves one open point, the
  schedule of the 3.12 evidence (proposed Q16), and one consequence for gap
  item 8's import route.
- Q05 E2: the user's choice; coherent once the round 5 consequences are
  recorded. The round 3 consequence that llm-shared's own suite lists no
  exemption should also cover L3 fixture exemptions.
- Q08 H3 with its 3.12 amendment: agree; my choice.
- Q11 K1 with exit code 4: agree; my choice, and the qualification is
  complete.
- Q12 L3: the user's choice over my L1 recommendation. It keeps L1's
  determinism in every order and distribution and keeps test exemptions per
  test; I do not contest it. It needs the precisions on a fixture's own
  work, credit when two permissions apply, and timing.
- Q13 M1 with L3 fixture declarations: agree; my choice. It needs the A2
  constraint on the fixture declaration.
- Q14 N2 with L3: agree; my choice. It needs the rule for a fixture
  permission exercised several times in one run.
- Q15 O2 with the Python 3.12 minimum: agree; my choice. It needs the
  version check to run before any code an older interpreter cannot read.

Proposed new question:

- Q16, when the Python 3.12 evidence runs: my choice P3 (repeatable static
  and executable 3.12 checks); P2 acceptable if a second interpreter in
  routine validation is not wanted.

Outstanding human decision: Q16. No other question is missing.

### Requested changes for feature-request shared_lifecycle_gate round 5

Requested changes:

1. Add Q16 after Q15, using the block below (or an equivalent
   formulation), at `User decision: pending`.
2. Record the consequences listed after the block next to the decision each
   one follows from, labelled as review consequences pending consolidation
   (round 5, 2026-11-05), never as user decisions. Do not change any
   confirmed choice or the user's words.
3. Add two dated clarifications rather than rewriting the record:
   - under Q05, the round 3 consequence "llm-shared's own whole-suite run
     must list no exemption" covers L3 fixture exemptions too: llm-shared's
     suite declares no test or fixture exemption;
   - under Q12, L3's historical con "one fixture exemption covers every test
     using that fixture" means the fixture's own work in every test that
     uses it, not those tests' own work, as the L3 decision states.
4. Optional wording: Q15's title still says "the Python 3.13 requirement";
   "the minimum Python requirement" fits the amended decision, or keep the
   title and rely on the dated amendment.

Proposed Q16 block:

```markdown
### Q16: When the Python 3.12 evidence runs

Question description: added after the round 5 review of the recorded
decisions. Q02 now requires executable Python 3.12 evidence for
acceptance, alongside Python 3.13 validation. It does not say whether that
evidence runs once, for this release's acceptance, or again whenever the
plugins change. The difference shows after acceptance. A consuming project
loads the plugins from the live llm-shared checkout (Q09), so a later
plugin change reaches its next prepared run at once. llm-shared's own
static checks treat everything under `tools/` as Python 3.13 code: Ruff
takes its target from `requires-python = ">=3.13, <3.14"`, and Pyright
sets `pythonVersion = "3.13"`. Neither would flag a Python 3.13-only
syntax or API added to a plugin later. On a consuming project's Python
3.12, that plugin would then fail to import or fail while running, and
under K1 every prepared run of that project would stop before any test
until llm-shared is fixed. llm-shared's suite cannot start a Python 3.12
run itself, because its tests may not start a process, so a repeated 3.12
run is a separate validation step.

#### BBQ for Q16

The sauce from Q02 must suit the guest who cannot eat garlic. The cook
tasted it on plain bread once, when the recipe was written. Later cooks
adjust the recipe and taste it only with garlic bread. The kitchen can rely
on that first tasting, check each new recipe card for garlic, or taste it
on plain bread again after every change. In this picture: the first
tasting is the one-off Python 3.12 acceptance evidence, a later adjustment
is a later plugin change, the garlic bread is llm-shared's Python 3.13
validation, checking the card is a static check set to Python 3.12, and
tasting again is a repeated Python 3.12 run of the plugins' own tests.

#### Options for Q16

- Option P1: once: the executable Python 3.12 evidence belongs to this
  release's acceptance only, and may share H3's temporary trial; later
  changes are validated on Python 3.13 only.
  - pro: no second interpreter in routine validation.
  - con: a later change can break Python 3.12 without any check noticing;
    the first sign is a consuming project's prepared runs stopping under K1.
- Option P2: the executable evidence once at acceptance, plus static checks
  of the plugin modules set to Python 3.12 in every llm-shared check.
  - pro: cheap, runs on every change, and catches the likeliest regression:
    syntax or a standard-library API newer than Python 3.12.
  - con: cannot show import-time, pytest-hook or runtime behaviour on 3.12,
    which Q02 says static checks alone cannot demonstrate.
- Option P3: P2's static checks, and the plugins' own Python 3.12 tests run
  again in llm-shared's regular whole-suite validation.
  - pro: the Python 3.12 promise stays demonstrated for as long as it
    stands, reusing the harness acceptance already requires.
  - con: a second interpreter and test environment in routine validation,
    run as a separate step outside the process-free suite.

#### Recommended option for Q16 (with arguments for this choice)

Option P3: Python 3.12 support is required because a current consuming
project needs it, and Q02 already rejects static evidence alone. Once
acceptance has built a Python 3.12 harness that does not depend on
llm-shared's 3.13-only helpers, running it again costs one separate step,
while P1 and P2 let the promise lapse without notice until a consuming
project's runs stop. P2 is the fallback if a second interpreter in routine
validation is not acceptable.

#### Answer to Q16: option P3 (with reason why it must be accepted as the answer)

Option P3: the requirement then states that the executable Python 3.12
evidence of Q02 is a repeated part of llm-shared's whole-suite validation,
not a one-off acceptance run, and that the plugin modules are also checked
statically against Python 3.12. How that step is launched, and what
provides the Python 3.12 interpreter, is design work.

User decision: pending
```

Consequences to record now, pending consolidation (each is a reviewer
proposal for the writer and user to confirm, not a user decision):

- With Q13 M1, Q12 L3 and Q01 A2: whatever mechanism declares a fixture
  exemption, a project's test files and pytest configuration keep collecting
  and running unchanged where the audit plugin is not loaded, in gate-only
  runs and outside the prepared environment where llm-shared may not be
  importable. The declaration therefore needs no import of llm-shared code
  from the project's test or `conftest.py` files, and adds no pytest
  configuration key that a run without the plugin reports as unknown,
  including under `--strict-markers`, `--strict-config`, pytest's `strict`
  setting and warnings-as-errors. pytest 9.1 refuses marks applied to
  fixtures, so the test marker cannot be reused for fixtures.
- With Q15 O2: the refusal below Python 3.12 must happen before any code
  that an older interpreter cannot parse or import is reached. pytest 9.1
  still runs on Python 3.10 and 3.11; on a real older interpreter, newer
  syntax or a newer standard-library import reached first would turn the
  refusal into an import failure (reported under K1 without the required
  version, or as pytest's own import error outside K1's scope). The
  simulated version test covers the decision logic; a repeatable check that
  the code reached before the version check is valid for Python 3.10 covers
  the rest. How is design work.
- With Q02 and gap item 8: llm-shared declares `requires-python = ">=3.13,
  <3.14"` for itself. The import route must work in a consuming project's
  interpreter outside that range, Python 3.12 today and the later versions
  gap item 5 includes, without installing llm-shared or anything bound by
  that declaration into it. The plugin documentation names the interpreters
  validated in this release, Python 3.12 and 3.13, as C3 does for
  platforms.
- With Q12 L3: a fixture exemption covers process starts made while that
  fixture's own setup or teardown runs, its finalizers included. It does
  not cover the setup or teardown of the fixtures it requests, the work of
  the tests that use it, or a process started later by a thread or pool it
  left running; such a start belongs to the lifecycle running at that
  moment, under D1.
- With Q12 L3 and Q14 N2: when an exempt function-scoped fixture of an
  exempt test starts a process, the start is credited to the fixture's
  permission only, so N2 may report the test's own permission as unused.
  A fixture permission exercised several times in one run (once per module
  or class for those scopes, once per worker under pytest-xdist) appears
  once in the summary, as used when any exercised instance on any worker
  started a process.
- With Q12 L3 and Q05 E2's timing qualification: a fixture exemption grants
  no timing exception. The wall time of its process start, and of waits for
  that process, counts toward the lifecycle carrying the fixture's setup or
  teardown, whichever test that is. A slow shared start can therefore make
  that test's wall verdict depend on test order and distribution, as for
  any shared fixture today; Q07 G1's wall limit remains the project's
  remedy, and the opt-in how-to says so.
- Consolidation: any step derived from B3 or the earlier O2 answer that
  would set gap item 5 to Python 3.13 no longer applies. Gap item 5 keeps
  Python 3.12 and later; the acceptance criteria add the Python 3.12
  evidence on the schedule Q16 settles.

### Human guidance response for feature-request shared_lifecycle_gate round 5

Human guidance:

yes on K1 exit code 4. What's next?

Guidance response:

K1's exit code 4 is recorded as the user's explicit qualification, and it
is complete: a selected plugin that cannot be imported in a prepared
opted-in run stops the run before any test, with exit code 4 and a message
naming the plugin and the opt-in, backed by repeatable in-process tests.
The same exit code now covers every refusal before tests run: invalid
settings, K1, invalid exemption declarations under M1, and interpreters
below the Python 3.12 minimum under O2.

What's next: the writer adds one new question, Q16 (whether the Python 3.12
checks run again when the plugins change, or only once at acceptance), and
records three consequences of the new decisions. Those consequences are
that the fixture exemption must not break runs without the audit plugin,
that the version check must run before code an older Python cannot read,
and that the import route must work outside llm-shared's own Python range.
The user then decides Q16 (recommended P3), and one more automated review
checks the result. Consolidation stays a separate human choice after that.

### Writer instructions for feature-request shared_lifecycle_gate round 5

1. Apply the requested changes: add Q16 at `User decision: pending`, record
   the round 5 consequences next to Q01/Q02, Q12, Q13, Q14 and Q15 as review
   consequences pending consolidation, and add the two dated clarifications
   under Q05 and Q12. Keep every confirmed choice and the user's words
   unchanged, and name no consuming project.
2. Present Q16 to the user with the detailed explanation the user asked
   for, including what each option costs in routine validation. Record a
   decision only from the user's explicit choice.
3. Request another automated review round covering Q16 and the new
   consequences. If the user has decided Q16 by then, include that decision
   in the same round.
4. Do not consolidate. The round 3 consolidation checklist still applies,
   except any step that would set gap item 5 to Python 3.13.

### Final reviewer decision for feature-request shared_lifecycle_gate round 5

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-5 -->

## Round 6 by requestor

- Recorded: 2026-11-05T13:52:13+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 6)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 6

### Requestor assessment for feature-request shared_lifecycle_gate (round 6)

The writer accepts round 5's requested changes. All fifteen earlier user
decisions remain confirmed and unchanged. One new question, Q16, is pending
and has not been answered on the user's behalf. The writer finds no other
known missing question and considers its P1/P2/P3 options sufficient for the
human choice, subject to this independent formulation review.

Q16 distinguishes one-off executable 3.12 acceptance evidence, one-off
evidence plus repeated 3.12 static checks, and repeated static plus executable
3.12 validation. The writer and reviewer recommend P3, but no selection is
recorded. The user's mandatory 3.12 compatibility requirement remains in
force under every option; this question chooses the validation schedule.

All round 5 consequences are recorded beside their affected decisions as
review consequences pending consolidation, not human choices. They cover:
the import route outside llm-shared's interpreter range; safe fixture
declarations when audit is absent under strict settings; refusal before
unsupported syntax or imports; fixture-own-work and finalizer boundaries;
fixture permission precedence and repeated-instance reporting; unchanged
timing attribution and its order-dependent wall consequences. The two
requested historical clarifications and Q15's neutral title were applied.

Please review the full specification and cross-question consistency. Verify
these consequences faithfully follow A2/D1/E2/L3/M1/N2/O2 and do not change
user choices. Check the new Q16 formulation and identify any remaining
missing question. Python 3.12 compatibility and separate K1 code 4 remain
settled. Consolidation and implementation are still unauthorized.

### Change summary for feature-request shared_lifecycle_gate (round 6)

Since the round 5 reviewed digest:

- Added Q16 at User decision: pending, preserving all prior question IDs
  and decisions. Its proposed P3 is a recommendation only.
- Under Q02, recorded the import-route constraint outside llm-shared's own
  Python range, release-validated interpreters and superseded B3 checklist.
- Under Q05, clarified that llm-shared's suite declares no fixture or test
  exemption.
- Under Q12, clarified L3's historical con and recorded own setup/teardown,
  finalizers, excluded dependency fixtures and later background starts,
  fixture-permission precedence and unchanged timing attribution.
- Under Q13, recorded the A2 compatibility constraint for fixture declarations,
  including absent-plugin strict runs and no consumer import dependency.
- Under Q14, recorded one row per exercised fixture permission and used-if-any
  aggregation across repeated instances and xdist workers.
- Under Q15, recorded early refusal compatibility and a repeatable pre-check
  compatibility check for Python 3.10 without promising runtime support on it;
  renamed the title to refer to the minimum Python requirement.

Full scanner: 16 questions, 15 confirmed, Q16 alone pending, no diagnostics.
The private companion matches the complete question section. No consolidation,
implementation, consumer changes, staging or commits occurred.

### Human guidance and writer response for feature-request shared_lifecycle_gate (round 6)

Human guidance:

yes on K1 exit code 4. What's next?

Writer response:

Accepted all round 5 requested changes. No writer/reviewer disagreement.
The requested consequences remain explicitly labelled as review consequences
pending consolidation and are not new user decisions. Every existing explicit
choice remains intact, including restored Python 3.12 support and K1 code 4.

Q16 uses an equivalent formulation of the proposed block. One precision avoids
overstating K1: a later 3.12 incompatibility may fail at runtime as well as at
import; K1's before-test refusal specifically applies to import failure.
The static-tool settings and live-checkout dependency remain explicit. P3
remains a proposal and Q16 awaits a human decision.

This intermediate round reviews the new formulation and the consequences
before returning to the human discussion gate. The prior Q12-Q15 explanation
batch retains its captured endpoint; appended Q16 has not been silently
included in that batch or given an inferred answer. At convergence, the
requestor will surface Q16 and the available human choices. Do not consolidate.

### Reviewer focus for feature-request shared_lifecycle_gate (round 6)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-6 -->

## Round 6 by reviewer

- Recorded: 2026-11-05T13:56:18+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 6

I read the complete current specification (SHA-256
`6edff395b51f9af1d6589e102cca020dadef44c6fbdbac1fdd1a19fc25bdfa6c`) and the
round 6 request. The body above the open questions keeps its line layout;
every change sits in the question section.

**Round 5's requested changes are all applied, and none changes a user
choice.** Q16 is present at `User decision: pending`, with P3 shown as a
recommendation only. Each consequence sits beside the decision it follows
from and is labelled as a review consequence pending consolidation:

- Q02: the import route works outside llm-shared's own Python range, the
  documentation names 3.12 and 3.13 as validated, and the superseded
  step that would have raised gap item 5 to 3.13 is withdrawn. This follows
  from the Q02 decision, which keeps llm-shared's interpreter unchanged.
- Q05: llm-shared's suite declares neither test nor fixture exemptions.
  This follows from E2 and L3 and the round 3 consequence.
- Q12: a fixture's own work (setup, teardown, finalizers; not requested
  fixtures, consuming tests or later background starts), credit to the
  fixture when both permissions apply, and no timing exception. This
  follows from L3's boundary, D1's attribution and the user's statement
  that CPU and wall enforcement are unchanged.
- Q13: the fixture declaration keeps runs without the audit plugin working,
  under every strict setting. This follows from A2, L3 and M1.
- Q14: one row per exercised fixture permission, used if any instance on
  any worker started a process. This follows from N2's own-scope reporting
  and its single controller summary.
- Q15: the refusal runs before code an older interpreter cannot read,
  backed by a repeatable Python 3.10 validity check, explicitly without a
  3.10 support promise. This follows from O2 as amended.

The two dated clarifications under Q05 and Q12 are accurate, and Q15's
neutral title fits the amended decision.

**The writer's K1 precision in Q16 is correct.** K1 covers a plugin that
cannot be imported; a Python 3.13-only API reached later fails while
running instead, so Q16 now says an import failure stops every prepared run
under K1, and a runtime failure does not. That is more accurate than my
round 5 wording.

**Q16 is complete, with distinct options and stated costs.** It asks only
for the validation schedule, under every option the Python 3.12
requirement itself stays settled, and it is compatible with C3 (Windows),
H3 (the trial may carry the first 3.12 run) and the Q15 check. Two
precisions help the user decide (wording only):

- P3's cost should name what it asks of every machine that runs the
  whole-suite validation: Python 3.12 must be available there. Its answer
  should say that validation which cannot provide Python 3.12 fails rather
  than skipping the step. Otherwise P3 could lapse silently, which is the
  outcome A3 and K2 were rejected for.
- The Q14 consequence's phrase "including for function-scoped fixtures"
  can be read as moving every function-scoped fixture's process start away
  from the test's permission. L3 says a test exemption covers its
  function-scoped fixtures. Only an exempt fixture takes the credit; the
  Q12 consequence already says this precisely, and Q14 should match it.

The new Q16 text and the round 5 consequence under Q02 write
`requires-python`, `tools/` and `pythonVersion` as plain text; code spans
match the rest of the document.

**No further question is missing.** I checked Q16 against Q02, Q08, Q09,
Q11 and Q15, and the round 5 consequences against each other. The 3.10
validity check (Q15) and the 3.12 static checks (Q16 P2 and P3) cover
different things: the refusal path and the supported range. Under every
Q16 option, the acceptance criteria still need executable 3.12 evidence
for this release. The remaining edits are wording, so the formulation can
converge; Q16 is the only outstanding human decision.

### Question verdicts for feature-request shared_lifecycle_gate round 6

Confirmed decisions (unchanged since round 5, all preserved):

- Q01 A2, Q03 C3, Q04 D1, Q06 F1, Q07 G1, Q08 H3, Q09 I1, Q10 J1, Q11 K1
  with exit code 4, Q13 M1, Q14 N2, Q15 O2 with the Python 3.12 minimum:
  agree; these are also my choices.
- Q02, Python 3.12 compatibility superseding B3: agree; my choice.
- Q05 E2 and Q12 L3: the user's choices over the historical E1 and L1
  proposals; coherent with the rest. I do not contest them.
- The round 5 consequences under Q02, Q05, Q12, Q13, Q14 and Q15 follow
  from A2, D1, E2, L3, M1, N2 and O2 and change no user choice. One phrase
  in the Q14 consequence needs the wording fix below.

Pending question (formulation reviewed; no user decision yet):

- Q16: in scope, options distinct, costs stated, compatible with C3, H3 and
  the Q15 check. My choice P3; P2 acceptable if a second interpreter in
  routine validation is not wanted. P3's cost and answer should name the
  Python 3.12 availability it requires and that validation fails rather
  than skipping.

Outstanding human decision: Q16. No question is missing.

### Convergence evidence for feature-request shared_lifecycle_gate round 6

Covered wording:

1. Q16 option P3: replace its con with:

   > con: a second interpreter and test environment in routine validation,
   > run as a separate step outside the process-free suite; every machine
   > that runs the whole-suite validation must be able to provide Python
   > 3.12.

   And append to the Q16 answer:

   > A whole-suite validation that cannot provide Python 3.12 fails rather
   > than skipping that step.

2. Q14 round 5 consequence: replace "Credit such starts to the fixture
   rather than a consuming test permission, including for function-scoped
   fixtures." with:

   > Credit such starts to the exempt fixture rather than a consuming test
   > permission, including when that fixture is function-scoped. A start in
   > a function-scoped fixture without its own exemption stays covered by,
   > and credited to, the exempt test's permission, as L3 states.

3. Code spans: in the Q16 description write `tools/`,
   `requires-python = ">=3.13, <3.14"` and `pythonVersion = "3.13"`; in
   the round 5 consequence under Q02 write `>=3.13,<3.14`.

Convergence rationale:

Every round 5 change is applied faithfully: Q16 is a complete pending
question with distinct options, stated costs and a recommendation only, and
each consequence follows from a confirmed decision without changing it. The
remaining edits are the three covered wording changes above; none changes
an option's substance, a recommendation or a confirmed choice. The next
step belongs to the human: decide Q16. Once that decision is recorded, it
needs a follow-up review before consolidation, as for the earlier batches.
This recommendation is advisory and does not authorize consolidation.

### Human guidance response for feature-request shared_lifecycle_gate round 6

Human guidance:

yes on K1 exit code 4. What's next?

Guidance response:

K1's exit code 4 stays recorded as the user's explicit qualification and
needs nothing further.

What's next: the question set has converged. The only open decision is
Q16, whether the Python 3.12 checks run again whenever the plugins change
(recommended P3) or only once at acceptance (P1, or P2 with repeated static
checks). After the user decides Q16, one follow-up review checks that
decision, and consolidation then remains a separate human choice.

### Writer instructions for feature-request shared_lifecycle_gate round 6

1. Apply the three covered wording changes (Q16 P3's cost and answer, the
   Q14 consequence's function-scoped phrase, the code spans). They do not
   need another automated round.
2. Present Q16 to the user with the detailed explanation the user asked
   for, including what P3 asks of every validation machine. Record a
   decision only from the user's explicit choice.
3. Do not consolidate. After the user decides Q16, request a follow-up
   review of that decision before consolidation; the round 3 checklist
   still applies, except any step that would set gap item 5 to Python 3.13.

### Final reviewer decision for feature-request shared_lifecycle_gate round 6

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-6 -->

## Round 6 by human - human-confirmation

- Recorded: 2026-11-05T15:05:06+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: P3

<!-- review-entry-id: human-confirmation-round-6 -->

## Round 7 by requestor

- Recorded: 2026-11-05T15:05:24+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request shared_lifecycle_gate (round 7)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
Review round: 7

### Requestor assessment for feature-request shared_lifecycle_gate (round 7)

All sixteen question blocks remain intact. A full decision scan confirms
sixteen explicit decisions, zero undecided questions and no diagnostics.
The newly recorded Q16 P3 decision matches the formulation reviewed in round
6, including its Python 3.12 availability requirement and failure instead of
silent skipping. The three covered round 6 wording corrections are applied.

The writer finds no missing question: validation scheduling is now explicit,
Python 3.12 support remains mandatory, and executable 3.12 evidence is separate
from llm-shared's process-free suite and Python 3.13-only helpers. Interpreter
provision and the launch mechanism remain design work. Existing confirmed
decisions are preserved, including K1 startup exit code 4.

Please independently review the full specification for consistency, the new
decision and its effects on Q02, Q08, Q09, Q11 and Q15, related documents,
and any additional question raised by the user's choices. Historical proposals
remain pending consolidation and must not override explicit decisions.

### Change summary for feature-request shared_lifecycle_gate (round 7)

Since round 6, applied its covered wording corrections: Q16 P3 states that
every whole-suite validation machine must provide Python 3.12 and absence
fails validation; Q14 distinguishes credit for an exempt fixture from the
permission of an exempt test; Q02 and Q16 use the requested code spans.

The user then explicitly selected P3. Replaced only Q16's pending decision
marker with a confirmed decision and dated clarification: regular static
checks targeting Python 3.12 and executable plugin tests under 3.12,
alongside 3.13 validation, with a separate step and independent harness.
Updated the private question companion to match. No question was removed,
no earlier decision changed, and no consolidation or implementation occurred.

### Human guidance and writer response for feature-request shared_lifecycle_gate (round 7)

Human guidance:

P3

Writer response:

The writer agrees with round 6's convergence recommendation and has applied
all three covered wording corrections. The user's exact new choice is P3.
Its dated Q16 record preserves every cost and boundary of the reviewed
option, including failure when Python 3.12 cannot be provided. The record
does not select a launch mechanism or interpreter-provision design.

This follow-up asks for review of the new human decision rather than reuse
of pre-decision convergence. Please preserve all sixteen confirmed choices,
identify any inconsistency or genuinely missing question, and recommend
convergence if no further decision is needed. Consolidation remains a separate
human choice and has not been authorized.

### Reviewer focus for feature-request shared_lifecycle_gate (round 7)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-7 -->

## Round 7 by reviewer

- Recorded: 2026-11-05T15:10:25+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request shared_lifecycle_gate round 7

I read the complete current specification (SHA-256
`92c7f44160c99b4ea6e47d15830ce948aa7c0f0e28124599df7cdd71f7a1cb8c`) and the
round 7 request. The body above the open questions is byte-identical to the
round 6 version; every change sits in the question section.

**Round 6's covered wording is applied exactly.** Q16 P3's cost names the
Python 3.12 availability it requires, its answer says validation fails
rather than skipping, the Q14 consequence now separates an exempt fixture's
credit from a function-scoped fixture covered by the test's permission, and
the code spans are in place.

**The Q16 P3 decision matches the reviewed option.** The dated record keeps
every element of P3: static checks targeting Python 3.12 for the plugin
modules, executable plugin tests under Python 3.12 in regular whole-suite
validation alongside Python 3.13, a separate step outside the process-free
suite, a harness independent of the 3.13-only helpers, and failure when
Python 3.12 cannot be provided. Launch and interpreter provision stay
design work. No other decision changed.

**Effects on the related decisions are consistent.**

- Q02: P3 makes the required executable 3.12 evidence a lasting check, not
  a one-off; static checks still supplement it and never replace it, as Q02
  requires.
- Q08 H3: the repeated 3.12 run does not replace the temporary
  consuming-environment trial, which still covers both activation contexts;
  the trial may still carry the first 3.12 run.
- Q09 I1: P3 is what keeps the 3.12 promise true for a live checkout that
  reaches every consumer at once.
- Q11 K1: unchanged; a later import failure on 3.12 is now caught in
  llm-shared's validation before it reaches a consumer's prepared run.
- Q15 O2: the Python 3.10 validity check of the code before the version
  check and the Python 3.12 static checks of the plugin modules are
  separate checks with separate targets; both stay required.

**Two wording precisions remain.**

- The Q16 decision record says "regular whole-suite validation" and
  "every machine running whole-suite validation", while option P3 says
  "llm-shared's regular whole-suite validation". groundhog's whole-suite run
  is shared tooling that consuming projects also use, so the shorter phrase
  could be read as requiring Python 3.12 in every project's validation. A
  dated clarification should restate that the step belongs to llm-shared's
  own validation and adds no requirement to a consuming project's
  validation.
- The round 5 consequence under Q02 still says "the 3.12 evidence schedule
  remains the new Q16 decision"; Q16 is now decided as P3.

**No question is missing.** All sixteen questions carry explicit user
decisions, the review consequences follow from them without changing any,
and the remaining edits are wording. At consolidation, the acceptance
criteria need the Python 3.12 evidence on P3's schedule, alongside the
round 3 checklist and the round 5 consequences.

### Question verdicts for feature-request shared_lifecycle_gate round 7

Confirmed decisions (all sixteen preserved):

- Q01 A2, Q02 (Python 3.12 compatibility superseding B3), Q03 C3, Q04 D1,
  Q06 F1, Q07 G1, Q08 H3, Q09 I1, Q10 J1, Q11 K1 with exit code 4, Q13 M1,
  Q14 N2, Q15 O2 with the Python 3.12 minimum: agree; these are also my
  choices.
- Q05 E2 and Q12 L3: the user's choices over the historical E1 and L1
  proposals; coherent with the rest. I do not contest them.
- Q16 P3: agree; my recommendation. The record matches the reviewed option
  and needs only the scope clarification below.
- The review consequences under Q01, Q02, Q05, Q07, Q11, Q12, Q13, Q14 and
  Q15 follow from the confirmed decisions and change none of them.

Outstanding human decisions: none. No question is missing. Consolidation
remains a separate human choice.

### Convergence evidence for feature-request shared_lifecycle_gate round 7

Covered wording:

1. Q16, after the dated decision: add a dated clarification so the step's
   scope matches option P3:

   > Review clarification dated 2026-11-05 (round 7): the Python 3.12 step
   > belongs to llm-shared's own whole-suite validation, as option P3
   > states. It adds no Python 3.12 requirement to a consuming project's
   > validation, including a groundhog run of that project's own suite.

2. Q02 round 5 consequence: replace "the 3.12 evidence schedule remains the
   new Q16 decision" with "the 3.12 evidence schedule is settled by Q16
   P3".

Convergence rationale:

All sixteen questions now carry explicit user decisions. The Q16 P3 record
matches the option reviewed in round 6, and its effects on Q02, Q08, Q09,
Q11 and Q15 are consistent. The review consequences follow from the
confirmed decisions without changing any. The remaining edits are the two
covered wording changes above, which change no decision. No human decision
is outstanding. Consolidation is the next step, and it remains a separate
human choice; this recommendation is advisory and does not authorize it.

### Human guidance response for feature-request shared_lifecycle_gate round 7

Human guidance:

P3

Guidance response:

P3 is recorded faithfully and is also my recommendation. The plugins'
Python 3.12 tests and 3.12 static checks now run in llm-shared's regular
whole-suite validation, and that validation fails if Python 3.12 is not
available. One dated clarification should say this applies to llm-shared's
own validation only, not to consuming projects. With Q16 decided, no human
decision remains open; consolidation is the next step whenever the user
chooses it.

### Writer instructions for feature-request shared_lifecycle_gate round 7

1. Apply the two covered wording changes (the Q16 scope clarification and
   the Q02 consequence's reference to Q16). They do not need another
   automated round.
2. Do not consolidate until the user explicitly chooses to. At
   consolidation, apply the round 3 checklist (except any step that would
   set gap item 5 to Python 3.13), the round 5 consequences, and an
   acceptance criterion for the Python 3.12 evidence on Q16 P3's schedule.

### Final reviewer decision for feature-request shared_lifecycle_gate round 7

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-7 -->

## Round 7 by human - human-confirmation

- Recorded: 2026-11-05T17:28:43+01:00
- Exchange: specification/feature-request/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-7 -->
