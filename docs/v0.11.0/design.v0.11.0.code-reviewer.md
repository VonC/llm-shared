# Design v0.11.0 -- Independent implementation code reviewer

Reference feature request: [feature-request.v0.11.0.code-reviewer.md](feature-request.v0.11.0.code-reviewer.md)

---

## Context for v0.11.0 implementation code review responses

The review exchange core and code-review requestor already establish a durable code-family dialogue around one exact implementation plan step. This design adds the independent responder that assesses the staged implementation, makes bounded repairs, publishes an advisory answer, and leaves commit authority with the writer and human gate.

The design carries the requirement's nine consolidated clarifications and the convergence review's design-phase observation: human guidance in a post-override request informs the assessment, but cannot override exchange identity, the current staged state, or the reviewed step's scope.

## Scope for v0.11.0 implementation code review responses

The v0.11.0 outcomes are:

1. Route one pending code-review request to an exact `code-reviewer` invocation.
2. Assess and repair one staged plan step without acquiring commit or workflow-completion authority.
3. Produce a typed answer and paired transcript summary through the shared publication transition.
4. Preserve sufficient repair and index evidence for deterministic recovery when a round stops before publication.

### In scope for v0.11.0 implementation code review responses

- Canonical reviewer instruction and LLM-specific adapters.
- Exact plan, implementation-step, umbrella, round, and staged-state validation.
- Code-family request-payload extensions for the mandatory request-time Git index tree and resolved validation set, including `tools/code_review_request.py`, the code-review request template, and the `code-review-requestor` instruction.
- Bounded repair ownership, staging boundaries, and `a.commit` assessment.
- Reviewer-safe application of `implementation-check` criteria.
- Mandatory validation evidence and commit-readiness classification.
- Paired answer rendering, answer publication, recovery evidence, and human-guidance handling.

### Deferred from v0.11.0 implementation code review responses

- Requestor-side round continuation, human confirmation, and authorized commit execution, which remain owned by `code-review-requestor`.
- Shared artifact naming, transition locking, timeout classification, and transcript append semantics, which remain owned by `review-exchange-core`.
- User documentation for operating all review-mode roles, which remains assigned to the later `review-mode-docs` umbrella item.
- Any change that lets the reviewer confirm convergence, consume answers, complete exchanges, or commit.

---

## Confirmed technical facts for v0.11.0 code-reviewer design

**The shared CLI already exposes the responder transitions**: `tools/review_exchange_cli.py` registers `wait-request` and `publish-answer`, so the new role can use the same durable state machine without adding private artifact mutations.

**The code-family request renderer already exists**: `tools/code_review_request.py` derives the code-review context and renders the complete request plus transcript summary from one typed input.

**The code-review route is currently requestor-only**: `tools/prompt_workflow_code_review.py` defines the `code-review-requestor` route, while no canonical `instructions/code-reviewer.md` or LLM-specific code-reviewer skill adapter exists yet.

**The paired specification responder is an established reference**: `tools/spec_review_answer.py`, `tools/spec_review_answer_cli.py`, `bin/spec_review_answer.bat`, and the shared and specialized answer templates already separate reviewer reasoning from durable publication.

**The code-review answer surfaces are absent**: there is no code-review answer template, answer renderer, or `bin/code_review_answer.bat` launcher in the current tree.

**The Git index is the shared review subject**: the completed requestor design reaches the reviewer only after the implementation cycle has staged changes and prepared `a.commit`.

**A typed batch-commit parser already exists**: `tools/git_batch_commit_parsing.py` exposes `parse_clipboard_content(content, *, interactive=True)`, returns typed `CommitBlock` values from `tools/git_batch_commit_models.py`, and raises `CommitMessageError`. No public side-effect-free validation entry point exists yet; this effort adds one beside the parser.

## Current behavior for v0.11.0 implementation responses

The requestor can publish a code-family request, but ordinary workflow routing has no independent responder to select and no typed code-review answer producer.

```txt
code-review-requestor publishes request
  -> request-pending
  -> no code-reviewer route or canonical responder
  -> request remains pending until external intervention
```

## Target behavior for v0.11.0 implementation responses

```txt
code-review-requestor publishes exact plan + step request
  -> request-pending
  -> pw selects code-reviewer for that exact identity
  -> reviewer waits for and validates the request
  -> reviewer verifies the mandatory request-time index tree once
  -> invalid request content or index drift ends the round with an
     early-rejection answer
  -> reviewer captures baseline index and working-state evidence
  -> reviewer applies implementation-check criteria
  -> reviewer runs mandatory validation and performs bounded repairs
  -> reviewer stages only reviewer-authored repairs and reassesses the index
  -> paired renderer creates answer + transcript summary
  -> shared publish-answer transition
       -> request consumed
       -> transcript summary appended once
       -> answer becomes visible
  -> changes-requested or convergence-gate
  -> pw returns control to code-review-requestor
```

The reviewer never calls answer consumption, round continuation, human confirmation, exchange completion, or commit operations.

---

## Exact routing and reviewer orchestration for v0.11.0

### State-aware code-reviewer routing

The code-review observer continues to resolve one exact plan and implementation-step context. Routing assigns the reviewer role to a sole `request-pending` code-family exchange or its intact `abandoned-request` form. Both shapes retain the reviewer-owned request artifact, so one state partition can keep them with the same actor; writer-owned, convergence, authorization, escalation, and repair-required states continue to route to `code-review-requestor`.

An explicit `pw skill code-reviewer` route accepts only the same pending or intact abandoned request that ordinary routing would choose. It cannot activate an exchange, pick the oldest request, or infer a nearby plan. For an abandoned request, it enters the same reviewer role so that the canonical sequence can perform the shared guarded reclaim.

### Fixed reviewer policy and allowed operations

The canonical instruction registers the code-family policy already used by the requestor:

```text
family: code
convergence signal: commit-ready
another-round label: Rework and review again
owning-workflow label: Commit
```

It calls `status`, reclaims once when the exact request is an intact `abandoned-request`, then requires the same round to return to `request-pending` before one bounded `wait-request`. The same guarded reclaim applies whether the reviewer first sees the request cold or its lease expires during the session. Any mismatch, interruption, escalation, or repair-required state stops with the shared diagnostic.

The reviewer may wait, assess, repair, render, and publish. It may not consume, continue, confirm, complete, escalate, resolve, archive, cancel, or commit.

## Assessment context and repair ownership for v0.11.0

### Validated review context

Before reading implementation details, the reviewer requires agreement among:

- the machine envelope;
- the request's human-readable umbrella, plan, step, and round;
- the exact plan path supplied by `pw`;
- a step identifier actually defined by that plan; and
- the live exchange context returned by the shared launcher.

When request content that the shared exchange cannot validate is wrong, the reviewer publishes `changes-requested` naming the exact disagreement and mutates nothing. This covers a step identifier the plan does not define, a human-readable identity field that disagrees with the envelope, and a missing mandatory request-time index tree. Publishing the allowed answer ends the reviewer's round instead of leaving its lease to expire.

Every code-family request from this version must include the Git index tree object captured when the request was published. Before a fresh assessment begins, the reviewer compares it once with the live index tree. A mismatch publishes `changes-requested`, naming both tree objects and the differing paths, because the reviewer cannot cancel or replace the round. Once assessment starts and reviewer repairs may be staged, recovery uses the retained assessed index tree instead of repeating the request-time gate.

The reviewer reads the current plan, the named step, its validation plan, the current staged diff, `a.commit`, and the exact request. It never uses the transcript as working context.

### Baseline and reviewer-authored change model

The reviewer captures the Git tree object of the index before assessment and records the content of every file it may repair before the first repair, as Git object-database blobs. It also records pre-existing unstaged and untracked paths that overlap the reviewed step. A created file has no baseline blob and is wholly reviewer-authored. A file the writer deleted while unstaged is not a repair target. This baseline separates writer state from later reviewer-authored changes.

A repair stays in scope only when every touched file is named by the plan step or already belongs to that step's staged set, introduces no new design decision, and changes no other step or requirement. The reviewer reports boundary-crossing work instead of changing it.

After each repair, the reviewer computes its patch from the recorded pre-repair content to the post-repair content and stages only cleanly attributable hunks. Pre-existing unstaged work is never swept into the index. If a reviewer repair overlaps an unstaged writer change in a way that cannot be separated safely, the reviewer leaves that repair to the writer and reports the overlap.

Every repair path and its effect are recorded in the answer. `a.commit` is amended only to keep file membership, grouping, ordering, scope, and conventional subjects accurate for the resulting staged set. The reviewer parses it with `parse_clipboard_content(..., interactive=False)` and uses the new side-effect-free validator to check staged-file membership, group ordering, and conventional subjects without permitting an input prompt.

### Reviewer-safe implementation-check boundary

When the request names an umbrella document, the reviewer records its digest, then applies the existing `implementation-check` criteria to the exact plan step in reviewer assessment mode. Step-level validation-plan rows may be updated to record the check result and are treated as review metadata rather than substantive implementation changes. The reviewer-facing boundary rejects any umbrella status-table mutation, even when the reviewed step is the final step of a collected effort.

After the criteria are applied, whether they passed or failed, the reviewer compares the umbrella digest with the recorded value. A changed digest fails the review boundary and is reported as a boundary violation regardless of the workflow result. When the request states `Umbrella draft: none`, there is no umbrella status table to protect and the digest check is recorded as not applicable. The assessment surface returns the implementation result, validation-plan changes, unresolved findings, and attempted umbrella mutation as explicit evidence.

## Validation and readiness evidence for v0.11.0

### Mandatory validation-set resolution

The project validation entry point and coverage gate form the mandatory default set. The exact plan step and current request may add checks but cannot remove defaults. One shared resolver publishes the resolved set and its sources in the request, and the reviewer revalidates it before commands run. When the embedded and current sets differ, the reviewer runs their union, reports every addition or omission and its direction, and treats resolver drift alone as a finding rather than a blocker. A default required by the current resolver cannot be dropped because the request predates it.

Every mandatory command must pass under the project's own gate, including its coverage threshold. A command that cannot run is reported as missing mandatory evidence, not converted into a pass.

The reviewer records the working-tree and index state immediately before and after validation. Differences confined to ignored paths are accepted as ordinary validation artifacts. Any tracked-file difference is reported as a readiness-blocking finding, is not classified as a reviewer repair, and is neither staged nor reverted by the reviewer.

### Commit-readiness classifier

The reviewer evaluates the six requirement-level floor items as one typed readiness result:

1. exact identity agreement;
2. complete implementation of the named step;
3. passing mandatory validation and coverage;
4. attributable staged scope;
5. no unresolved current or carried finding; and
6. accurate `a.commit` grouping and description.

A change to a tracked file is substantive except for `a.commit`, ignored caller evidence, answer and transcript artifacts, and reviewed-step validation rows written only to record the reviewer's own check. Any substantive reviewer change forces `changes-requested` in that round. A complete floor with no substantive repair permits the advisory `commit-ready` recommendation.

The first round with unavailable mandatory evidence requests rework. When the same evidence remains unavailable in the next round or a writer disputes its mandatory status, the reviewer publishes that finding but does not call `escalate`. The requestor and shared no-progress bound perform the escalation transition. Missing or disputed evidence always blocks readiness.

## File-based IO cost clarification for the code-reviewer design

- Derive request, answer, transcript, manifest, plan, and validation-plan paths from the exact exchange context; never enumerate a directory to select an artifact.
- Read each caller-owned assessment input once and compare only explicitly named step files when recording repair or validation state.
- Write retained evidence to one stable ignored manifest path, and use atomic paired writes for answer content and transcript summary.
- Keep Git work proportional to the explicit staged set and repair paths rather than the repository's unrelated working tree.

## Paired code-review answer design for v0.11.0

### Two typed answer shapes and two renderings

The answer renderer accepts a discriminated union of two shapes that share the protocol-valid exchange identity, positive round, disposition, writer-response context, and optional human-guidance response.

An assessment answer additionally carries the fully validated code-review context, baseline and assessed index identities, repair report, validation report, `a.commit` assessment, and unresolved findings. Its typed validation report labels command results as covering the pre-repair staged state and carries the resolved validation set and sources, resolver drift and direction, and pre-validation and post-validation working-tree and index identities.

An early-rejection answer ends a round before full context validation or assessment and carries the protocol-valid exchange identity, round, `changes-requested` disposition, exact identity or snapshot disagreement, and writer instructions that would resolve it. Fully validated context, baseline and assessed index identities, repair report, validation report, `a.commit` assessment, and unresolved findings are absent rather than empty. The renderer validates each shape separately and rejects any mixture of early-rejection and assessment-derived fields.

It returns:

- a complete answer artifact with the reviewer envelope and full findings; and
- a paired substantive transcript summary of the same findings without protocol boilerplate.

The renderer reads caller-owned ignored inputs once and writes two separate ignored outputs. It never waits, edits implementation files, reads the transcript, or mutates protocol artifacts.

### Answer sections and disposition contract

The complete answer contains the exact umbrella or `none`, implementation plan, step, and round exactly once. An early-rejection answer renders only identity, exact disagreement, and writer-instruction sections. An assessment answer's authored sections cover:

- assessed staged-tree identity and baseline comparison;
- implementation-check result and validation-plan effects;
- mandatory-check and coverage results labeled as pre-repair evidence, including the resolved set and sources, resolver drift and direction, and repository-state comparison around validation;
- repairs made, paths staged, and `a.commit` amendments;
- contamination, unresolved findings, and boundary-crossing work;
- response to human guidance when present;
- requested rework or commit-readiness rationale; and
- one final advisory decision.

`changes-requested` requires concrete writer instructions and is mandatory after any substantive reviewer repair or unresolved readiness-floor item. `commit-ready` requires all six floor items and no substantive repair in the round. Neither disposition authorizes a commit.

### Human guidance boundary

A post-override request may contain one literal `Human guidance:` block. The reviewer addresses it explicitly and explains its effect on the assessment. Guidance may clarify priorities or request additional scrutiny, but it cannot override exchange identity, the current staged state, mandatory evidence, or the named step's scope.

When guidance conflicts with those boundaries, the reviewer records the conflict and follows the safe disposition. It never treats human wording inside a request as a protocol transition or commit authorization.

## Publication and stopped-round recovery for v0.11.0

### Shared answer publication

The reviewer passes both renderer outputs to `publish-answer` with the exact code-family context and policy. The shared transition validates both renderings, consumes the request, appends the transcript summary once, and makes the answer visible. An interrupted publication is resumed through the same idempotent operation rather than repaired by hand.

### Retained code-review evidence

If the round stops after repairs or assessment but before publication, the working tree and index remain untouched. Caller-owned ignored evidence retains:

- request identity and round;
- the baseline and assessed Git index tree objects;
- reviewer-authored repair paths and staging effects;
- validation and implementation-check results;
- `a.commit` assessment; and
- the input paths needed to rebuild the answer.

A reclaimed or resumed assessment compares the retained assessed index tree with the current index. Matching state permits revalidation and rendering under the live round identity. Drift forces a fresh assessment. The request-time gate is not repeated after the first fresh assessment. A cached answer is never published with stale round or index identity.

The stable identity-and-step-derived manifest is retired only after `publish-answer` reports `outcome: published`. A `commit-ready` publication reaches that outcome with exit `3` because the exchange stops at pending human confirmation, so manifest retirement is keyed to the published outcome rather than exit `0`.

## Design decisions for v0.11.0 implementation code review responses

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Require the request-time Git index tree and compare it once before fresh assessment; recovery compares the retained assessed tree. | Validated review context; retained code-review evidence | Reviewer-start snapshot only; classified non-overlapping drift |
| Q02 | Record pre-repair blobs and stage only a cleanly attributable reviewer patch. | Baseline and reviewer-authored change model | Reject every same-file repair; isolated worktree or index |
| Q03 | Use reviewer assessment mode with an umbrella digest checked after either criteria result. | Reviewer-safe implementation-check boundary | Prompt-only restraint; separate pure evaluator |
| Q04 | Resolve validation through one shared resolver, embed the set and sources, then run the union on drift. | Mandatory validation-set resolution | Reviewer-only discovery; request list as final authority |
| Q05 | Keep one stable identity-and-step manifest and retire it on the published outcome, including exit `3`. | Retained code-review evidence | Per-round manifests; opaque path in coordination state |
| Q06 | Compose shared envelope and IO validation with a code-specific discriminated typed model. | Paired code-review answer design | Cloned specification renderer; universal sparse renderer |
| Q07 | Reuse the typed batch parser and add a side-effect-free validator, always parsing non-interactively. | Baseline and reviewer-authored change model; confirmed technical facts | Prose inspection; `gcba` subprocess dry run |
| Q08 | Accept ignored validation artifacts and report tracked validation changes without staging or reverting them. | Mandatory validation-set resolution; commit-readiness classifier | Treat every difference as reviewer repair; snapshot restoration |

---

## Acceptance cases for v0.11.0 implementation code review responses

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| One exact pending code request | `pw` routes to `code-reviewer` with the exact plan and step. | The reviewer must never select a nearby identity. |
| Request step absent from the plan | Reviewer mutates nothing and publishes `changes-requested` naming the undefined step. | Internal identity agreement cannot validate a nonexistent step, and the round must still end through an allowed operation. |
| Human-readable identity disagrees with the envelope or request-time tree is missing | Reviewer mutates nothing and publishes `changes-requested` naming the disagreement. | Invalid specialized request content must not hold the reviewer lease until abandonment. |
| Live index differs from the request-time tree | Reviewer publishes `changes-requested` with both tree objects and differing paths. | One request round must identify one immutable staged subject. |
| Small repair inside named files | Reviewer applies and stages only its own delta, lists it, and publishes `changes-requested`. | Substantive reviewer code requires writer reassessment. |
| Repair overlaps pre-existing unstaged writer work | Reviewer leaves the unsafe overlap to the writer and reports it. | The reviewer cannot stage work it does not own. |
| `implementation-check` updates the reviewed validation row | The row may be staged and does not alone force another round. | It records review evidence rather than implementation behavior. |
| `implementation-check` changes the umbrella status | Reviewer fails the boundary, reports the violation, and leaves the changed umbrella in place; the substantive change makes the round `changes-requested`. | The digest detects rather than prevents the write, while whole-effort completion remains writer-owned. |
| Mandatory coverage gate fails | Commit-readiness is withheld and rework is requested. | Every readiness-floor item must pass. |
| Validation changes only ignored paths | Reviewer accepts the artifacts and continues assessment. | Ignored validation output is outside the tracked implementation subject. |
| Validation changes a tracked file | Reviewer reports a readiness-blocking finding without staging or reverting it. | The validation command caused the difference, so it is neither writer-approved implementation nor reviewer repair. |
| Same mandatory evidence is unavailable in the next round | Reviewer publishes the repeated finding; the requestor and shared bound escalate. | Automated dialogue must terminate without granting the advisory reviewer escalation authority. |
| Reviewer makes no substantive repair and all evidence passes | Answer recommends commit readiness without authorizing commit. | Convergence remains advisory and human-owned. |
| Human override guidance accompanies a request | Reviewer addresses it but preserves identity, staged-state, evidence, and step boundaries. | Guidance informs assessment without becoming protocol authority. |
| Round stops after repairs but before publication | Tree and index stay intact and retained evidence records the assessed Git index tree. | Recovery must preserve work and detect drift. |
| Publication is interrupted | The same `publish-answer` transition is replayed idempotently. | Specialized code must not mutate protocol artifacts by hand. |
