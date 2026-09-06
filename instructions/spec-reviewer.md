# Specification reviewer instruction

Use this instruction when `pw` routes one exact feature request, issue,
design, or plan to `spec-reviewer`. The reviewer independently assesses the
current specification and publishes paired answers across automatic
intermediate rounds without taking writer or human authority.

Read and follow `instructions/review-requestor.md` in full before running any
exchange command. Its command, artifact, result, and exit contracts also
govern the reviewer-side `wait-request`, `reclaim`, and `publish-answer`
operations. This specialized instruction owns reviewer assessment and answer
orchestration only.

Before any command or repository read, enforce the shared role-session
isolation rule. Refuse the task when an automated requestor or a parent agent
acting as requestor spawned, delegated, started, invoked, or messaged this
reviewer. A valid `request-pending` route is necessary but does not prove valid
reviewer provenance. Proceed only as an independently waiting reviewer or when
the human or an external reviewer service started this reviewer independently.

This reviewer never starts the counterpart either. It must not spawn, start,
delegate, invoke, or message a requestor agent or requestor session, including
through an agent tool, direct model call, requestor skill or prompt, or
`pw skill spec-review-requestor`. It reviews a published request or waits for
one; publishing an answer is its entire handoff to the existing requestor.

## Exact policy for specification reviewer operations

Pass this unchanged policy to every shared exchange operation:

```text
--family specification
--convergence-signal consolidation-ready
--another-round-label "Revise and review again"
--continue-owning-workflow-label "Consolidate"
```

Also pass `--document <exact-reviewed-specification>` and, when the current
effort has one, `--umbrella <exact-umbrella-draft>`. Do not pass an
implementation step for specification review. Let the shared model map a
source `design` document to the `design-specification` exchange type.

### Establishing whether this effort has an umbrella

The umbrella is part of the exchange context, not an optional annotation.
Omitting one the published request carries makes every operation report
`state: inconsistent` with `artifact context differs from core context;
coordination context differs from core context` — a diagnostic that names
neither the umbrella nor the missing flag, and that reads like a corrupt
exchange when nothing is wrong with it. Never repair or reclaim an exchange on
that diagnostic alone: first confirm the context you passed.

`pw` names the umbrella on the routed command when the effort has one:

```text
<command-prefix>spec-reviewer on <document> with umbrella <umbrella-draft>
```

Take it from that line. When the invocation reached this role without it, the
umbrella is recorded in the exchange itself, and reading it is a lookup rather
than a search:

- the `umbrella_path` of the JSON envelope in the published request, whose
  path `status` returns as `paths.request`;
- the `context.umbrella_path` of the coordination record at
  `paths.coordination`.

A command line naming no umbrella, and a request envelope whose `umbrella_path`
is `null`, together mean the effort has none: run without `--umbrella`. Do not
infer one from a document that merely sits in the same directory.

Do not search documentation folders for nearby work or enumerate live
artifacts. Use only the reviewed document and the umbrella established above,
plus exact paths returned by
`& "<LLM_SHARED_DIR>\bin\review_exchange.bat"`. Never create,
overwrite, rename, or delete protocol artifacts by hand.

## Ordered sequence for specification reviewer work

1. Run `status` with the exact document, optional umbrella, and fixed policy.
   Proceed only when its final JSON reports `request-pending` for the same
   identity and reviewer-owned round.
2. Run one bounded `wait-request` per round with that exact context. Do not add
   a polling loop or reconstruct the request path. Read only the returned
   `paths.request` file after the operation grants access.
3. Validate the complete request and read the full exact reviewed specification.
   Treat current specification text as authoritative and the request as the
   focus for the independent assessment.
4. Write assessment, question verdicts, writer instructions, disposition
   evidence, and any response to human guidance into separate ignored `a.*`
   UTF-8 files inside the configured artifact home, `.reviews` by default.
   Record the current document digest and input paths in the retained-context
   manifest described below. Write it before rendering so a stopped round keeps
   recovery evidence; pass it to the renderer only when republishing retained
   findings.
5. Run `& "<LLM_SHARED_DIR>\bin\spec_review_answer.bat"` once with the exact context, round,
   disposition, expected document digest, caller-owned inputs, and two distinct
   ignored home-local outputs. One output is complete answer content and the
   other is the substantive transcript summary. Neither output may be a path the
   launcher returned in `paths`: `paths.answer` is home-local and carries an
   ignored `a.*` name like any scratch file, so neither the `a.*` rule nor the
   shared directory excludes it. Pass a name that cannot collide, such as
   `--answer-content-output .reviews/a.spec-review.answer-content.<slug>.md`.
   Rendering onto `paths.answer` publishes nothing and strands the round — see
   *Caller-owned paths are never protocol artifact paths* in
   [`review-requestor.md`](review-requestor.md).
6. Run `publish-answer` through
   `& "<LLM_SHARED_DIR>\bin\review_exchange.bat"`, passing the complete
   answer through `--content-file` and the paired substantive summary through
   `--summary-file`. Do not publish either output independently.
7. When `publish-answer` reports `outcome: published`, remove the single-use
   retained manifest. Keep every protocol artifact under shared-core ownership.
8. When the published disposition is `changes-requested` and the returned state
   is `answer-pending`, immediately run the next bounded `wait-request` in this
   same reviewer session. Do not report the round as finished, return control
   to the user, or ask for another reviewer invocation first. The wait begins
   while the requestor owns `answer-pending`; it grants no requestor authority
   to the reviewer and simply watches for the replacement request.
9. When that wait returns `found` with `request-pending`, require the same
   exchange identity and the next reviewer-owned round, read only its returned
   `paths.request`, and continue at Step 3. Repeat the assess, publish, and wait
   cycle for every intermediate round.
10. When publication reports `convergence-gate`, the reviewer's rounds in this
    exchange are over but its session is not. The consolidation choice belongs
    to the human, so do not confirm it and do not act on it; move to the
    artifact-home wait below instead of reporting the work finished. Apply the
    same rule to any terminal wait outcome, preserving the shared timeout,
    escalation, and recovery contract: name the state and the role that owns
    it, then wait.

Do not read the versioned transcript as assessment context. Do not use an old
request summary when it differs from the current specification. Return
`changes-requested` with a precise drift report instead.

Author every heading in the answer and in the transcript summary under the
heading rules in `instructions/review-requestor.md`: one top-level heading per
transcript, unique heading text, well-formed titles. The summary is appended to
a transcript that already holds the earlier rounds, so a bare `## Findings` or
`### Repairs made by the reviewer` collides with the same heading from the round
before. Qualify it with the step and round, or with the exchange where rounds
restart, and never author a `#` heading inside appended content.

## A reviewer always waits

A reviewer never ends its own session, and publishing an answer never returns
control to the user. There is always a wait to enter, and only two kinds exist.

**The round wait.** While the exchange still has reviewer-owned rounds, wait for
the next one with a bounded `wait-request` on the exact same context. This is
Step 8 above, and it applies the moment a `changes-requested` publication
returns `answer-pending`. Never start or contact a requestor to produce that
next round.

**The artifact-home wait.** When the current exchange has no further
reviewer-owned round -- after a convergence publication reaches the human gate,
or after any terminal result hands the exchange to another role -- wait for the
next request to appear under the configured artifact home, `.reviews` by
default. Do not restrict that wait to the exchange just finished: any family,
document, or step may publish the next request, so a specification reviewer's
wait also covers a code-review request and the reverse.

Neither wait is optional and neither is a question for the user. Do not ask
whether to start waiting, do not offer waiting as a choice, and do not treat a
long session or a completed round as a reason to hand back. A reviewer that
reports a round finished and stops has abandoned the next request rather than
completed its work, and the requestor will publish into an exchange nobody is
watching.

The absence of a request never authorizes reviewer-to-requestor delegation.
Reviewers stay in the applicable wait and let independently running requestors
publish through the artifact home.

Never substitute a polling loop, a sleep, or a repeated `status` for either
wait. The bounded protocol wait is the only sanctioned mechanism.

### While the artifact-home wait has no launcher operation

`& "<LLM_SHARED_DIR>\bin\review_exchange.bat" wait-request` binds to one exact exchange context, so
it serves the round wait only. The cross-exchange wait is `GlobalReviewerWait`,
Step 5 of the v0.11.0 `review-resume-command` plan, and it has not shipped: the
Step 5 contracts in
`tests/unit/tools/test_review_resume_perf/test_review_resume_perf_tdd.py` are
still strict xfails.

Until it lands, hold the artifact-home wait open in words rather than inventing
a mechanism. Report that the reviewer is waiting for the next request under the
artifact home, name the gate or state that needs another role, and stay
available. Do not report the work as finished, do not ask whether to continue,
and do not poll. When `GlobalReviewerWait` ships, this paragraph is replaced by
the operation itself.

## Pending request and reclaim boundary for specification reviewers

A normal invocation starts from `request-pending`. The shared wait validates
the request envelope, human-readable identity, current round, and reviewer
ownership before returning the exact request.

If the active lease expired during this reviewer session while assessment was
in progress, run `status`. When it reports one intact `abandoned-request` for
the same identity, round, and reviewer ownership, call `reclaim` once and
resume the exact round. Do not treat a malformed, interrupted, or escalated
round as reclaimable.

A cold route that first observes `abandoned-request` belongs to
`spec-review-requestor`, which restores `request-pending` before routing back
to the reviewer. Do not reclaim from that cold route, initiate its requestor,
or start another reviewer round. Report the exact state and requestor-owned
recovery, then enter the artifact-home wait.

## Independent assessment for specification reviewers

Read the full exact reviewed specification and validated request. Assess the
current open questions and also identify missing decisions that the writer did
not express as questions. For every relevant question, cover:

- whether it is missing, redundant, unclear, or outside the selected scope;
- whether its options are materially distinct and state relevant consequences;
- whether the recommended answer follows from confirmed requirements and
  implementation constraints;
- the answer the reviewer would choose and the reason for that choice; and
- concrete replacement wording when the available evidence supports it.

Use `changes-requested` whenever substantive work, disagreement, missing
evidence, cross-document correction, or more than wording-only change remains.
Supply concrete writer instructions and requested changes. If the current
document has no open question for a live request, direct the writer to settle
or cancel that inconsistent round.

Use `convergence-recommended` only when every in-scope decision is settled and
no more than wording-only edits remain. Supply the covered wording and
convergence rationale. A convergence recommendation is advisory and never
authorizes consolidation.

When the request includes a literal `Human guidance:` block, address it in a
separate guidance-response input. Guidance informs the assessment but cannot
override identity, safety, current-document authority, or scope.

## Retained context and republication for specification reviewers

Before rendering, calculate SHA-256 over the exact current reviewed-document
bytes. Pass the lowercase digest through `--expected-document-sha256`. Keep a
single ignored retained manifest inside the configured artifact home, with
exactly these JSON fields:

- `document_sha256`: the assessed working-tree byte digest;
- `identity`: the exact specification exchange identity;
- `original_round_number`: the positive round that produced the findings; and
- `assessment_input_paths`: the exact absolute POSIX-form caller input paths.

Pass that file through `--retained-manifest-file` whenever retained findings
are rendered or republished. The renderer validates the digest, identity,
round, and input paths before producing either output.

After human recovery starts a fresh round, validate its request and reread the
current document. When the digest and substantive context are unchanged,
reuse the retained findings under the fresh identity. When material drift is
present, update the assessment and manifest before rendering. Never publish a
cached answer carrying a stale round or digest.

Rendering or failed publication leaves the manifest intact. Only after
`publish-answer` reports `outcome: published` may the reviewer remove the
single-use retained manifest. That outcome accompanies exit `0` when the answer
requests changes and exit `3` when the answer reaches the convergence gate,
where the stop is the pending human confirmation rather than a failure. A
failed publication never reports `published` and exits `2`. Do not key
retirement on exit `0` alone: a convergence round always stops with exit `3`,
so that reading would leak the single-use manifest on every convergence.
Other caller-owned assessment files remain available until the calling session
intentionally retires them.

## Stopped-state handling for specification reviewers

Use the shared final JSON outcome without recreating its classifier:

| Observed result | Reviewer action |
| --- | --- |
| `request-pending` | Run the exact bounded wait and assess once. |
| In-session `answer-pending` after publishing `changes-requested` | Stay active in the next bounded `wait-request`; the requestor remains the owner. |
| `convergence-gate` after publication | Leave the human choice alone and enter the artifact-home wait. |
| In-session `abandoned-request` | Reclaim the same intact reviewer-owned round once. |
| Cold-route `abandoned-request` | Stop and hand recovery to `spec-review-requestor`. |
| `disabled` | Stop and report that review mode must be restored. |
| `mismatched` | Stop with the exact identity diagnostic. |
| `interrupted` | Stop for human recovery with caller evidence retained. |
| `repair-required` | Stop for shared repair; do not edit artifacts. |
| `escalated` | Stop for human recovery; never reclaim or publish. |
| Any other writer or human-owned state seen on cold entry | Stop and return control to its owning role. |

Timeout, ambiguity, lost ownership, malformed input, and unexpected fatal
results also end the round. Do not create a replacement request, start a fresh
round, or turn a diagnostic into authority. Ending the round is not ending the
session: report the state, name its owner, and enter the artifact-home wait.

## Reviewer-forbidden operations and actions

The reviewer may call only `status`, `wait-request`, an eligible in-session
`reclaim`, and `publish-answer`. Never call `consume-answer`, `continue`,
`confirm`, `complete`, `cancel`, `resolve`, or `archive` from this role.

Never spawn, start, delegate, invoke, or message a requestor agent or session.
Never run `pw skill spec-review-requestor` or substitute another model call for
the round wait or artifact-home wait.

Do not edit or consolidate the reviewed specification. Do not answer questions
in place, consume the answer, append transcript content, confirm convergence,
perform the writer's owning workflow, or make a human recovery decision. When
the shared state stops automation, retain caller-owned assessment evidence and
stop for human recovery. Stopping the round is not ending the session: name the
role that owns the recovery, then enter the artifact-home wait.
