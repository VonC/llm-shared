# Report active review status

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Review-mode status need

A review can stop because its shell, VPN connection, terminal, computer, or
agent session ended. The repository retains protocol-owned coordination
records, but today a caller has to reconstruct the exchange family, reviewed
document, round, artifact names, and responsible role from memory.

Add one repository-root `rvw_status` command that diagnoses every active
review exchange without requiring the caller to supply that identity. Its
human-readable output and stable machine-readable result must make the current
role unmistakable: they state whether the continuing agent is a `requestor` or
a `reviewer`, in addition to reporting the review family and other exchange
facts. A generic actor label alone is not sufficient.

## Umbrella relationship

This feature belongs to the review-mode umbrella at
`docs/v0.11.0/draft.v0.11.0.review-mode.md`. Status output must preserve that
context for any exchange associated with an umbrella.

- When an umbrella exists, show the exact repository-relative umbrella path in
  the human-readable result and expose it as a stable structured field.
- Make the umbrella relationship visibly labelled, rather than leaving users
  to infer it from a reviewed-document path or exchange identifier.
- When no umbrella exists, state `Umbrella: none` and return the corresponding
  empty or null structured value defined by the later design.
- The reported umbrella, reviewed document, role, family, round, and exchange
  occurrence must agree with the machine-readable exchange identity.

## Status command scope

The effort regroups:

- a repository-root `rvw_status` launcher;
- one shared read-only implementation used by that launcher;
- a concise human-readable account of every review exchange currently in
  progress; and
- a stable machine-readable result that the later `rvw_resume` effort can
  consume without scraping prose.

The command covers both specification and implementation-code review. It may
diagnose either side of those exchanges, but it does not perform requestor or
reviewer work and does not resume an exchange.

## Required exchange identity

For each discovered exchange, report all of the following:

- whether the review is active and its current protocol state;
- whether it is a specification or implementation-code review;
- the explicit continuing role, labelled `requestor` or `reviewer`, so the
  agent and human both know who the agent is in this exchange;
- the more specific role context when useful, such as specification requestor,
  specification reviewer, code requestor, or code reviewer;
- the exact reviewed specification or implementation plan;
- the exact umbrella draft when one exists, otherwise `none`;
- the implementation step for code review when applicable;
- the current round and exchange occurrence;
- the request, answer, transcript, and durable coordination artifact paths
  applicable to the current state; and
- the next protocol action owned by the reported role.

The human-readable form must present role and umbrella as first-class labelled
facts. The structured form must use stable typed fields for the same facts so
another command does not need to interpret display text.

## Discovery and multiplicity rules

Discover live specification and code exchanges only from protocol-owned
coordination records. Do not require the caller to remember or provide a
family, document, slug, step, round, occurrence, artifact path, requestor, or
reviewer identity.

Distinguish these outcomes explicitly:

1. no active review exchange;
2. exactly one active exchange, with its complete identity and next action;
3. multiple active exchanges, listing each complete identity without silently
   choosing one.

Malformed, inconsistent, repair-required, or escalated records remain visible
as diagnostic states. The status command must not guess a role, umbrella, or
next action when durable evidence disagrees.

## Read-only and restart guarantees

`rvw_status` is strictly read-only. It must not create, overwrite, append,
delete, renew, reclaim, or otherwise mutate requests, answers, transcripts,
leases, coordination records, Git state, or review-mode markers.

The command must work after a shell, VPN, terminal, computer, or agent restart
without relying on prompt memory. Its result describes the durable repository
state as found; the separate `review-resume-command` effort owns any later
lease-independent pickup or continuation.

## Boundary and dependencies

Discovering who owns a stopped review and what it concerns is read-only
diagnosis. It belongs outside the requestor and reviewer roles so either side
can rely on the same facts before acting.

This effort depends on the settled review exchange core and both specification
and code requestor/reviewer roles. It does not include the `rvw_resume` command,
host-specific continuation instructions, lease reclamation, or automatic
workflow execution; those belong to the next umbrella item.
