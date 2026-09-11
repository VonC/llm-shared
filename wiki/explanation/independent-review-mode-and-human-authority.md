# Why independent review mode separates authority

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Read this explanation before activating independent review mode or when the
authority boundary is unclear. It explains why the roles and human gate are
separate; task procedures and exact commands belong to the linked how-to and
reference pages.

Independent review mode gives one agent the writer or requestor role and a
separate agent the reviewer role. It exists for work where an assessment should
come from a context that did not author the staged subject or specification.
The separation is operational, not a change of model brand or prompt wording.

## Three authorities in an independent exchange

The **requestor** owns the workflow being reviewed. It prepares the request,
answers requested changes, and resumes work only after the protocol returns
authority. The canonical agent policy is
[instructions/review-requestor.md](../../instructions/review-requestor.md).

The **reviewer** owns the independent assessment. A specification reviewer
questions a requirement, design, or plan under
[instructions/spec-reviewer.md](../../instructions/spec-reviewer.md). A code
reviewer checks one implementation step and its immutable evidence under
[instructions/code-reviewer.md](../../instructions/code-reviewer.md). Neither
reviewer takes over writer work or makes the final human choice.

The **human** alone accepts the convergence recommendation. A specification
answer may recommend consolidation and a code answer may recommend commit, but
that recommendation does not authorize consolidation or commit. The exchange
stops at its human gate until the registered choice is supplied.

## Why role creation stays outside the exchange

An exchange state identifies who may act next; it does not authorize that actor
to manufacture its counterpart. If a requestor could spawn its own reviewer,
the assessment would inherit the requestor's orchestration context and would no
longer be independently started. If a reviewer could spawn a requestor, it
could cross from assessment into writer-owned continuation.

For that reason, a requestor publishes and waits, while a reviewer reviews or
waits. Neither role starts, spawns, delegates to, invokes, or messages the
other. A pending artifact is necessary evidence that work exists, but it is not
proof of valid session provenance. The reviewer must already be waiting or be
started independently by the human or an external reviewer service. Each role
rejects a task initiated by the automated counterpart.

## Why reciprocal waiting is the default

The main purpose of the requestor-reviewer workflow is an automatic dialogue
between two independent agent sessions, not a sequence of rounds that the human
must restart. The requestor publishes a request and immediately waits for its
answer. When the reviewer publishes `changes-requested`, it immediately waits
for the replacement request in the same invocation. The requestor consumes the
answer, updates the reviewed work, and publishes that replacement while the
reviewer is already standing by.

The requestor waits for its exact answer with the exchange timeout. The
reviewer runs one quiet global wait across rounds and families; it can remain
idle until a request arrives or the human cancels. Native notifications and
bounded polling belong to that command, so neither agent writes its own retry
loop. Waiting does not transfer authority: while the reviewer observes
`answer-pending`, only the requestor may consume the answer or continue the
round. At convergence the durable human gate takes over that exchange, while
the reviewer stays in `wait-any-request` for future work. Routine lease expiry
alone cannot turn this availability into an error.

## Why a new session takes a new generation

An ownership capability belongs to one live agent session. Durable coordination
stores its digest, not the plaintext token, so a later session cannot silently
impersonate the former owner. The human's bare `resume` request authorizes
automatic pickup after the migration and role gates pass. Pickup issues a new
generation to the selected actor and makes the former capability stale, even
while the prior lease is fresh.

At convergence, these authorities remain separate. The human still chooses
whether to commit or start another round; the requestor receives the capability
needed to record that exact choice. The pickup is not a reset because the round,
answer, transcript, and human gate remain intact. It is not `reclaim` either:
reclaim renews an expired lease, while pickup replaces a capability that the
new process never possessed.

This generation advance makes session turnover recoverable without weakening
the ownership fence. An old session that wakes later cannot mutate the exchange
with its superseded generation and token.

## Why runtime evidence has one configured home

Requests, answers, coordination, locks, recovery records, and retained review
evidence all belong to one ignored repository-local artifact home. Keeping that
vocabulary behind one locator prevents different commands from observing
different copies of the same exchange. The default is `.reviews`; a strict
repository declaration can select another relative directory.

Older repositories may still have recognized artifacts at the project root or
in the former default home. Status therefore performs one bounded,
transactional migration preflight before it reports anything. A collision or
invalid placement blocks status instead of choosing one copy. Once placement
is ready, ordinary status projection is read-only.

The same projection reconciles separately recorded requestor and reviewer LLM
natures. Missing legacy evidence remains `unrecorded`, and contradictory
evidence remains `conflicting`; status never guesses or overwrites identity.
Together, centralized placement, explicit role identity, and ownership
generations make the reported next actor evidence rather than prompt memory.

## Why the evidence remains durable

Each round publishes an answer and appends the request, answer, and human gate
events to a versioned transcript. That transcript is evidence of how the work
converged. It is not working context for later rounds: each actor follows the
current paths returned by the launcher and reads only the live artifact assigned
to its role.

Keeping the transcript separate from live artifacts has two benefits. A later
reader can audit the questions, repairs, and human choices, while an active
agent cannot accidentally treat an old round as the current request. Lease,
reclaim, and recovery records also remain visible without changing the reviewed
document by hand.

## Independent review mode compared with the self-review loop

| Concern | Self-review loop | Independent review mode |
| --- | --- | --- |
| Intent | Challenge a generated document or check implementation in the owning workflow | Obtain a separate-agent assessment through a durable exchange |
| Participants | One agent asks or checks; the human answers or validates | Requestor agent, reviewer agent, and human gate |
| Opt-in | Part of the normal document and implementation chain | Activated by the repository review-mode marker |
| Intermediate work | Questions or missing work return inside the owning workflow | Published rounds alternate automatically through reciprocal requestor and reviewer waits |
| Final choice | Human answers questions or validates implementation evidence | Human chooses consolidation, commit, or another round |

The [self-review explanation](why-the-llm-reviews-its-own-work.md) describes the
normal owning-workflow loop. The
[review-round guide](../how-to/answer-a-review-round.md) explains how a human
answers its open questions. Those pages retain their existing purpose;
independent review mode adds a different actor boundary rather than replacing
them.

## Policy ownership for independent review mode

This page describes observable user behavior. The linked canonical
instructions remain authoritative for agent policy, including which artifact an
actor may read, which operations it may call, and where it must stop. Later
tutorial, how-to, and reference pages build on this authority split without
copying those policy bodies.
