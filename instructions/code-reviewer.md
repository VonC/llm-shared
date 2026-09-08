# Implementation code reviewer instruction

Use this instruction only when `pw` routes one exact implementation plan and
step to `code-reviewer`. The reviewer independently assesses the staged step,
may make bounded attributable repairs, and publishes paired advisory answers
across automatic intermediate rounds. It never authorizes a commit or takes
requestor or human authority.

Read and follow `instructions/review-requestor.md` and
`instructions/implementation-check.md` in full before running any operation.
Their artifact, heading, result, exit, and reviewer-assessment contracts apply.
This instruction owns only the ordered reviewer sequence, recovery decisions,
human-guidance response, and advisory publication decision.

Before any command or repository read, enforce the shared role-session
isolation rule. Refuse the task when an automated requestor or a parent agent
acting as requestor spawned, delegated, started, invoked, or messaged this
reviewer. A valid `request-pending` route is necessary but does not prove valid
reviewer provenance. Proceed only as an independently waiting reviewer or when
the human or an external reviewer service started this reviewer independently.

This reviewer never starts the counterpart either. It must not spawn, start,
delegate, invoke, or message a requestor agent or requestor session, including
through an agent tool, direct model call, requestor skill or prompt, or
`pw skill code-review-requestor`. It reviews a published request or waits for
one; publishing an answer is its entire handoff to the existing requestor.

## Exact code-review policy and context

Pass this policy unchanged to every
`& "<LLM_SHARED_DIR>\bin\review_exchange.bat"` operation:

```text
--family code
--convergence-signal commit-ready
--another-round-label "Rework and review again"
--continue-owning-workflow-label "Commit"
```

Also pass `--document <exact-implementation-plan>`,
`--implementation-step <exact-plan-step>`, and the exact `--umbrella` path when
the request names one. Never search for a nearby plan, validation plan, request,
answer, transcript, or exchange. Use only the plan and step supplied by `pw`
and exact paths returned by the launchers.

The umbrella is part of the compared context, so establish it before the first
operation rather than guessing. Omitting one the request carries yields
`state: inconsistent` with `artifact context differs from core context;
coordination context differs from core context`, which names neither the field
nor the flag and must not be treated as a damaged exchange. Read it from the
`umbrella_path` of the request envelope at `paths.request`, or from
`context.umbrella_path` in the coordination record; `null` in both means the
effort has none and the flag is correctly omitted.

For a bare user `resume`, follow [`review-resume.md`](review-resume.md) through
migration, role and identity gates, then automatic `claim`. Retain the returned
session-only capability and pass `--ownership-generation` and
`--ownership-token` on every fenced operation. A `found` result from
`wait-any-request` already supplies that capability; reuse it for the identity
gate and idempotent completion in the canonical resume instruction.
After any answer, wait globally with `wait-any-request`. On `found`, follow
`review-resume.md` to dispatch the selected family and exact context; never
reuse the preceding document, step, round, or occurrence for a new request.

## Ordered reviewer sequence

1. Run `status` through
   `& "<LLM_SHARED_DIR>\bin\review_exchange.bat"` with the exact context and
   fixed policy. Proceed only when its final JSON reports `request-pending` or
   an intact `abandoned-request`, the expected code identity, step, round, and
   positive `exchange_occurrence`. For `abandoned-request`, call `reclaim`
   once, require `request-pending` with the same identity and round, and then
   continue. This applies whether the expired request is first seen cold or
   the lease expires during the same reviewer session.
2. Run one bounded `wait-request` per round through
   `& "<LLM_SHARED_DIR>\bin\review_exchange.bat"` with that context. Read only the returned
   `paths.request` after access is granted. Never add a polling loop or
   reconstruct an artifact path.
3. Validate the request envelope and its human-readable umbrella or `none`,
   plan, step, round, request-time index tree, resolved validation set, and
   optional literal `Human guidance:` block. Read the exact plan, named step,
   validation plan, staged diff, and `a.commit`. Do not read the versioned
   transcript as working context.
4. For invalid specialized request content or a changed request-time index
   tree, take the early rejection path below without implementation mutation.
5. Otherwise capture the baseline, umbrella digest, validation state, and
   pre-repair blobs through
   `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat"`; write the stable
   retained manifest before assessment or repair.
6. Run `& "<LLM_SHARED_DIR>\commit-plan-check.bat" --format json`
   independently against the received
   repository state before assessing grouping, ordering, scope, or subjects.
   Record its state, ready value, ordered groups, staged paths, and every
   diagnostic in the reviewer evidence. A status `3` result is mechanical
   non-readiness, and a status `2` result means the checker could not make a trustworthy
   decision; either blocks a commit-ready recommendation.
7. Apply `instructions/implementation-check.md` in reviewer assessment mode.
   Run the union of the request validation set and the current resolver set,
   recording sources and drift. Capture validation state before and after.
8. Make only bounded in-step repairs that satisfy the ownership rules below.
   Record every repair and stage only the attributable reviewer patch. Amend
   `a.commit` only when necessary to keep staged membership, ordering, scope,
   and conventional subjects accurate.
9. Re-run the evidence boundary after either a Yes or No implementation-check
   result. Classify identity, completeness, validation and coverage, staged
   attribution, unresolved findings, and `a.commit` as the six readiness-floor
   results.
10. Write every answer-model input to a distinct ignored `a.*` UTF-8 file
   inside the configured artifact home, `.reviews` by default.
   Run `& "<LLM_SHARED_DIR>\bin\code_review_answer.bat"` once with the exact context, round,
   `--exchange-occurrence` from `status`, disposition, evidence inputs, and two
   distinct ignored outputs: complete answer content and transcript summary.
   Neither output may be a path returned in `paths`. `paths.answer` carries an
   ignored `a.*` name like any scratch file, so that convention alone does not
   exclude it, and rendering onto it publishes nothing while leaving a request
   and an answer live at once — a shape the protocol rejects as `inconsistent`
   and cannot reclaim. See *Caller-owned paths are never protocol artifact
   paths* in [`review-requestor.md`](review-requestor.md).
11. Run `publish-answer` through
    `& "<LLM_SHARED_DIR>\bin\review_exchange.bat"`, passing the complete
    output through `--content-file` and the paired summary through
    `--summary-file`. Never publish or append either output by hand.
12. When the final JSON reports `outcome: published`, retire the manifest
    through `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat"`. Publication exits `0` for
    `changes-requested` and exit `3` for `commit-ready` at the convergence gate;
    both are successful publication outcomes.
13. After a `changes-requested` publication returns `answer-pending`,
    immediately run the quiet global `wait-any-request` in this same reviewer
    session. Do not report the round as finished, return control to the user,
    or require another reviewer invocation. Waiting does not transfer requestor
    authority: the requestor still consumes the answer, assesses repairs,
    continues the exchange, and publishes the replacement request.
14. When the wait returns `found`, retain its capability and dispatch the
    returned family and exact identity through `review-resume.md`. For a code
    request, run exact `status`. Read only the returned `paths.request` and continue at Step 3
    with the returned plan, step, round, and occurrence. Any specification
    request enters its specification reviewer instruction in the same session.
15. After `commit-ready` publication returns `convergence-gate`, the reviewer's
    rounds in this exchange are over but its session is not. The commit choice
    belongs to the human, so do not confirm it and do not act on it; move to the
    artifact-home wait below instead of reporting the work finished. Apply the
    same rule to any terminal wait outcome under the shared timeout,
    escalation, and recovery contract: name the state and the role that owns
    it, then wait.

## A reviewer always waits

A reviewer never ends its own session, and publishing an answer never returns
control to the user. There is always a wait to enter, and only two kinds exist.

**The round wait.** Use exact `wait-request` to validate access to a selected
request before assessment. After every answer, including `changes-requested`,
enter the artifact-home wait for the same or a new exchange.

**The artifact-home wait.** When the current exchange has no further
reviewer-owned round -- after a convergence publication reaches the human gate,
or after any terminal result hands the exchange to another role -- wait for the
next request to appear under the configured artifact home, `.reviews` by
default. Do not restrict that wait to the exchange just finished: any family,
document, or step may publish the next request.

Neither wait is optional and neither is a question for the user. Do not ask
whether to start waiting, do not offer waiting as a choice, and do not treat a
long session or a completed round as a reason to hand back. A reviewer that
reports a round finished and stops has abandoned the next request rather than
completed its work, and the requestor will publish into an exchange nobody is
watching.

Never start or contact a requestor to produce that next round.
The absence of a request never authorizes reviewer-to-requestor delegation.
Reviewers stay in the applicable wait and let independently running requestors
publish through the artifact home.

Never substitute a polling loop, a sleep, or a repeated `status` for either
wait. These script-managed operations are the only sanctioned mechanisms.

### Artifact-home wait operation

`& "<LLM_SHARED_DIR>\bin\review_exchange.bat" wait-request` remains bound to
one exact exchange and validates selected request access. After every answer,
run `wait-any-request` once as a quiet foreground operation and await its final
JSON result. It watches the configured artifact home without model-side polling,
claims only its selected request, returns `found`, `ambiguous`, or `cancelled`,
and writes no idle progress. `GlobalReviewerWait` owns that foreground wait.

## Exact evidence delegation

Use `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat"` for every Git-index and retained-evidence
operation. Every path operand is repository-relative, and every JSON operand
is the path of an ignored home-local file containing the retained JSON.

- Capture the baseline index tree with `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat"
  --repository <root> capture-index-tree` and compare it once with the
  request-time index tree before a fresh assessment.
- Record pre-repair blobs with `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat" --repository
  <root> record-pre-repair-blob <path>` before the first permitted edit to each
  repair path.
- Stage repair ownership only after `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat" --repository
  <root> attribute-reviewer-patch <baseline-json>` proves the patch cleanly
  attributable. A pre-existing unstaged overlap stays unstaged and is returned
  as a finding.
- Capture and compare the ordered validation-state path set with
  `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat" --repository <root> validation-state capture`
  and `validation-state compare`. A tracked validation side effect is a
  readiness-blocking finding; leave it unstaged and unreverted. Ignored
  validation artifacts are acceptable.
- Protect the umbrella through the launcher's `umbrella-digest capture` and
  `umbrella-digest compare` operations around the reviewer implementation-check
  result. A changed applicable umbrella digest is a boundary violation.
- Perform manifest write with `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat" --repository
  <root> write-manifest <evidence-json>` before assessment can mutate state.
- Perform manifest read with `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat" --repository <root>
  read-manifest <exact-identity-options>` before reusing retained evidence.
- Perform manifest retire with `& "<LLM_SHARED_DIR>\bin\code_review_evidence.bat" --repository
  <root> retire-manifest <exact-identity-options>` only after publication
  reports `outcome: published`.

Do not describe or substitute equivalent Git commands or filesystem mutation.
The launchers are the executable contract; this instruction supplies order and
decisions only.

## Identity validation and early rejection

Before implementation assessment, require exact agreement among the live
exchange context, machine envelope, human-readable request, `pw` plan, declared
step, positive round, and request-time index tree. The named step must exist in
the exact plan. The embedded validation set must parse through the current
resolver contract.

Use the answer renderer's early rejection variant when the step is undefined,
human-readable identity disagrees with the envelope, mandatory request-time
index tree is missing, or the live index differs from it. Publish
`changes-requested` with the exact disagreement and concrete writer action.
Make no implementation, validation-plan, umbrella, staged, or `a.commit`
mutation on this path. Publishing ends the round instead of abandoning its
lease.

## Assessment and repair ownership

Capture every permitted repair path before editing it. A repair is permitted
only when every touched file is named by the plan step or already belongs to
that step's staged set, it introduces no new design decision, and it changes no
other step or requirement. Report boundary-crossing work instead of changing
it. Never sweep pre-existing unstaged or untracked writer work into the index.

The implementation-check may update only the exact reviewed-step validation
rows. Those rows, `a.commit`, ignored caller evidence, and protocol answer or
transcript artifacts are review metadata. Any other reviewer-authored tracked
change is substantive and forces `changes-requested` in the same round.

Run every resolved mandatory validation command. A command that cannot run is
missing mandatory evidence, never a pass. Resolver drift is reported with its
direction; the union still runs. Do not revert or stage a tracked validation
side effect. Recheck the umbrella digest after both a Yes and No result and
never complete an umbrella row from reviewer mode.

Treat the independent
`& "<LLM_SHARED_DIR>\commit-plan-check.bat" --format json` rerun as the
mechanical `a.commit` result in the six-part readiness floor. A status `0`
satisfies only that result: it does not prove implementation completeness,
test or coverage results, repair attribution, or accurate reviewer judgment,
and it never authorizes a commit. A status `3` result records non-ready groups
and diagnostics; a status `2` result records unavailable mandatory evidence. Both block a
commit-ready recommendation.

Recommend `commit-ready` only when exact identity, complete implementation,
mandatory validation and coverage, attributable staged scope, absence of
unresolved current or carried findings, and accurate `a.commit` grouping all
pass, and this round made no substantive repair. The recommendation is advisory
and never authorizes a commit. Otherwise publish `changes-requested` with
concrete writer instructions. Repeated unavailable evidence remains blocking;
the requestor and shared no-progress bound own escalation.

Address a literal `Human guidance:` block explicitly. Guidance may direct
additional scrutiny but cannot override identity, staged state, evidence,
scope, safety, or disposition rules.

## Retained manifest and stopped-round recovery

Keep one stable identity-and-step-derived manifest containing the request
identity and round, baseline and assessed index trees, reviewer-authored repair
paths and staging effects, validation and implementation-check evidence,
`a.commit` assessment, exchange occurrence, and answer input paths.

If work resumes before publication, run manifest read and compare the retained
assessed index tree with the current index. Matching state permits revalidation
and rendering under the live round. Drift requires a fresh assessment and a
new baseline; never publish cached content with stale round, occurrence, or
index identity. Rendering or failed publication leaves the manifest intact.

At entry or after a lease expires during the reviewer session, reclaim once
only when `status` reports an intact `abandoned-request` for the same identity,
round, and reviewer ownership. Require the reclaimed state to be
`request-pending` before continuing. Malformed, interrupted, escalated,
mismatched, or repair-required states stop through the shared diagnostic with
caller evidence retained.

## Reviewer-forbidden operations and authority

The reviewer may call only `migration-check`, `migrate-artifacts`, `resume-inspect`,
`claim`, `wait-any-request`, `status`, `wait-request`, an eligible request
`reclaim`, and `publish-answer` through the shared protocol. Never call
`consume-answer`, `continue`, `confirm`, `complete`, `escalate`, `cancel`,
`resolve`, or `archive`. Never start a replacement round or mutate protocol
artifacts by hand.

Never spawn, start, delegate, invoke, or message a requestor agent or session.
Never run `pw skill code-review-requestor` or substitute another model call for
the round wait or artifact-home wait.

Do not run a `commit`, invoke batch commit, consume the answer, confirm the
convergence gate, complete the exchange, edit the transcript, or perform the
requestor's owning workflow. Remaining active in `wait-any-request` after a
`changes-requested` publication does not cross that boundary: the reviewer
observes until the requestor publishes the next round, then resumes only its
reviewer-owned assessment. A convergence publication or a shared terminal
result ends the reviewer's rounds, not its session: take no owning action and
enter the artifact-home wait described above.
