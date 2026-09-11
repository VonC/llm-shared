# Report active review status through a skill and command

## User story for review status

As a human or agent returning to an interrupted review, I want an installed
`$llm-shared:review-status-command` skill that uses one read-only repository
command to report every active review exchange, including whether the
continuing agent is the requestor or the reviewer and which umbrella owns the
work, so I can discover and request the capability by name and understand the
durable workflow state without reconstructing its identity from prompt memory
or transient shell state.

## Review-mode revision for `rvw_status`

The review-mode umbrella adds a public `review-status-command` skill, exposed
by the installed llm-shared plugin as `$llm-shared:review-status-command`, plus
a repository-root `rvw_status` command, a shared read-only implementation, a
concise human-readable report, and a stable machine-readable result. The skill
refers to the command as its execution mechanism. The command diagnoses
specification and implementation-code exchanges from protocol-owned
coordination records.

The focused child draft adds two explicit identity rules:

1. Status must say plainly whether the continuing agent is a `requestor` or a
   `reviewer`; a generic actor label by itself is insufficient.
2. Status must visibly identify the exact umbrella draft when one exists and
   must state that no umbrella exists otherwise.

## Requirement clarifications

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Report a stable broad `requestor` or `reviewer` role plus its specification/code specialization, so humans and automation receive the same direct identity. | Required `rvw_status` command contract | A specialized role alone makes every caller derive the broad role; display-only identity cannot support `rvw_resume`. |
| Q02 | At `convergence-gate`, report the requestor as the continuing agent and human confirmation as the next action, keeping agent responsibility separate from human authority. | Required `rvw_status` command contract | A `human` agent role breaks the two-role contract; reporting both agents leaves continuation ambiguous. |
| Q03 | Use `unknown` only for genuine corrupt or irreconcilable evidence and attach diagnostics; differing healthy `owner` and `expected_next_actor` values are not conflicts. | Umbrella visibility rules | Preferring the newest evidence guesses authority; omitting the exchange hides the case needing repair. |
| Q04 | Treat every implemented nonterminal state as active and `idle` as inactive, explicitly including `owning-action-pending` so an authorized action is not sent through a second human gate. | Multiplicity and diagnostic outcomes | Immediately runnable states alone hide blocked work; recent completed history belongs in transcripts. |
| Q05 | Take umbrella identity or confirmed absence only from durable exchange identity; a missing legacy field is repair-required, with document metadata allowed only as a non-authoritative hint. | Umbrella visibility rules | Inference can silently change identity; treating a missing field as `none` states a false fact. |
| Q06 | Report each protocol-canonical artifact path with expected, present, missing, or not-applicable status, so missing evidence remains diagnosable. | Required `rvw_status` command contract | Existing-only paths hide missing artifacts; expected-only paths hide their observed presence. |
| Q07 | Return healthy and damaged exchanges independently, attach diagnostics to damaged entries, and mark the repository-wide result as having errors. | Multiplicity and diagnostic outcomes | All-or-nothing failure hides healthy exchanges; skipping damaged entries hides repair evidence. |
| Q08 | Treat zero, one, or multiple well-formed exchanges as a successful query; unreadable, malformed, inconsistent, or repair-required evidence is non-success while retaining useful partial results. | Multiplicity and diagnostic outcomes | Exactly-one success confuses status with selection; payload-only failures are easy for shell callers to miss. |
| Q09 | Make a stable machine action identity authoritative and derive a concise human description or command from it. | Required `rvw_status` command contract | Prose alone forces machine parsing; an identifier alone does not tell a human what to do. |
| Q10 | Derive the continuing role from `expected_next_actor` and report `owner` separately, because ownership and the next turn are distinct responsibilities. | Required `rvw_status` command contract | Using `owner` directs the wrong agent in a healthy request-pending round; showing both without a designated role leaves the next actor unclear. |
| Q11 | Report `lease_renewed_at` and freshness against the configured wait timeout, preserving raw evidence and the degree of staleness needed for later reclaim decisions. | Required `rvw_status` command contract | A timestamp alone makes every caller repeat the comparison; omitting lease data loses the degree of staleness. |
| Q12 | Resolve the repository from the caller's working directory by default, allow an explicit override, and require launcher/shared-entry-point parity. | Required `rvw_status` command contract | The installed location can select the tooling repository; a mandatory argument contradicts argument-free discovery. |
| Q13 | Provide a public `review-status-command` skill, discoverable as `$llm-shared:review-status-command`, whose canonical instruction delegates status collection to `rvw_status`. | Required review-status skill contract | A command alone is not discoverable as a skill; copying command logic into an adapter would create competing implementations. |

## Current review-status behavior in v0.11.0

- No repository-root `rvw_status` command provides a complete account of live
  review exchanges.
- No installed `$llm-shared:review-status-command` skill exposes this
  capability by name or directs an agent to the repository command.
- A caller returning after a shell, VPN, terminal, computer, or agent restart
  must reconstruct the exchange family, reviewed document, round, artifacts,
  and responsible role from durable files and prior context.
- Review summaries carry identity, including umbrella context, but there is no
  single read-only diagnostic result that exposes those facts across all live
  specification and code exchanges.
- Existing requestor and reviewer workflows own their actions; neither role is
  the proper owner of family-neutral status discovery.

## Gap to close for active review diagnosis

1. Add a public `review-status-command` skill that is discoverable after the
   llm-shared plugin is installed and delegates status collection to
   `rvw_status`.
2. Add a repository-root `rvw_status` launcher that needs no exchange-specific
   arguments.
3. Discover every live specification and implementation-code exchange from
   protocol-owned coordination records.
4. Return the complete durable identity and current state for each exchange.
5. Make the continuing role explicit as `requestor` or `reviewer` in both
   human-readable and machine-readable results.
6. Make the umbrella relationship a labelled first-class fact, using the exact
   repository-relative umbrella path when present and an explicit absence when
   not present.
7. Distinguish zero, one, and multiple live exchanges without silently choosing
   one.
8. Remain strictly read-only so diagnosis cannot alter or resume the workflow.

## Required review-status skill contract

The llm-shared plugin must expose a skill named `review-status-command`, so a
user can invoke it as `$llm-shared:review-status-command`. Its reusable content
must live in one canonical root instruction. Every provider-specific skill file
must remain a thin adapter that refers directly to that canonical instruction
rather than copying or summarizing it.

The canonical skill instruction must invoke or direct the agent to invoke the
repository-root `rvw_status` command and report its result. The skill must not
reimplement exchange discovery, state classification, result rendering, or
exit-code policy in Markdown. Its behavior remains read-only and accepts the
same caller-repository default and explicit root override as the command.

## Required `rvw_status` command contract

The command must inspect the repository containing the caller's working
directory by default, without changing to the launcher's installed location.
It may accept an explicit repository-root override for controlled callers and
tests. The repository-root launcher and shared entry point must report the same
repository when invoked from the same working directory, without requiring the
caller to remember or supply any of these exchange values:

- review family;
- reviewed document or slug;
- requestor or reviewer identity;
- implementation step;
- round or exchange occurrence; or
- request, answer, transcript, lease, or coordination-artifact path.

For every discovered exchange, the result must report:

- whether a review is active and its current protocol state;
- whether the family is specification or implementation-code review;
- the continuing role, explicitly labelled `requestor` or `reviewer` and
  derived from the protocol's `expected_next_actor`;
- the exchange `owner` as a separate responsibility from the continuing role;
- the more specific context when applicable, such as specification requestor,
  specification reviewer, code requestor, or code reviewer;
- the exact reviewed specification or implementation plan;
- the exact umbrella draft when one exists, otherwise an explicit `none`;
- the implementation step for code review when applicable;
- the current round and exchange occurrence;
- the protocol's canonical artifact paths:
  - request, answer, transcript, durable coordination, tombstone, and
    transition lock; and
  - for each path, its expected, present, missing, or not-applicable status;
- the durable `lease_renewed_at` timestamp and a derived freshness indication
  against the configured wait timeout; and
- the next protocol action owned by the reported role.

The continuing role describes who must perform the next protocol action, not
merely which side owns the exchange or last wrote an artifact. A healthy
record may therefore have different `owner` and `expected_next_actor` values.
Human-readable wording and structured identity must agree.

At `convergence-gate`, the continuing role is `requestor`, while the next
action states that human confirmation is required. The requestor owns
presenting and consuming that decision but does not receive authority to make
it. Every next action carries one stable machine identity and a concise human
description or command derived from that identity.

## Umbrella visibility rules

The human-readable report must display umbrella context as a clearly labelled
field. When an exchange belongs to the review-mode umbrella, it reports:

`docs/v0.11.0/draft.v0.11.0.review-mode.md`

The machine-readable result must expose the same repository-relative path as a
stable structured value. For a standalone effort, the human report states
`Umbrella: none`, and the structured result represents the same absence without
inventing a path.

Durable exchange identity is authoritative for both an umbrella path and a
confirmed absence. When an older record omits the umbrella field, status marks
the entry repair-required rather than inferring identity or reporting `none`.
Document metadata may be shown only as a non-authoritative repair hint.

The umbrella, reviewed document, family, continuing role, state, round, and
exchange occurrence must agree with the protocol's machine-readable exchange
identity. Genuine corruption, such as a state and artifact set that cannot both
be true or an identity that disagrees with its own envelope, is reported as an
inconsistent or repair-needed state rather than guessed. Different healthy
`owner` and `expected_next_actor` values are not conflicting evidence.

## Multiplicity and diagnostic outcomes

`rvw_status` must distinguish:

1. no active review exchange;
2. exactly one active exchange, with its complete identity and next action;
3. multiple active exchanges, with each identity reported independently and no
   implicit selection; and
4. malformed, inconsistent, repair-required, or escalated coordination state,
   with enough evidence to explain why no role or next action can be selected
   safely.

Each discoverable exchange receives an independent result. A damaged entry
keeps its diagnostics while healthy entries remain available, and the overall
result states that errors are present. Zero, one, and multiple well-formed
exchanges are successful status queries. Operationally unreadable, malformed,
inconsistent, or repair-required evidence produces a non-success outcome while
retaining any trustworthy partial results.

Every implemented nonterminal state is active: `round-in-progress`,
`request-pending`, `answer-publication-in-progress`,
`transcript-repair-pending`, `answer-pending`, `convergence-gate`,
`owning-action-pending`, `escalated`, `abandoned-mid-round`,
`interrupted-answer-publication`, `interrupted-transcript-append`,
`abandoned-request`, `abandoned-answer`, and `inconsistent`. Only `idle` is
inactive. Reporting `owning-action-pending` explicitly lets a later requestor
finish an already-authorized owning action without repeating the human gate.

The machine-readable result must remain stable enough for the later
`rvw_resume` command to consume without parsing human prose.

## File-based IO cost clarification for review status

- Discover candidates with one bounded root enumeration of the reserved active
  coordination prefix; do not scan the documentation tree or load unrelated
  repository metadata.
- Load review configuration once per command, then inspect only the strict
  coordination record and fixed canonical artifact set for each candidate.
- Keep per-candidate reads bounded independently of repository size, including
  the before-and-after coordination fingerprint required to detect races.
- Build both output forms from one in-memory normalized result and perform no
  review, marker, index, working-tree, or ref write.

The loading phase is therefore a small protocol-index read proportional to the
number of active coordination candidates, not a broad metadata-loading pass.

## Read-only guarantees for `rvw_status`

Running status must not:

- create, overwrite, append, or delete request, answer, or transcript files;
- renew, reclaim, or otherwise change leases or coordination records;
- change Git refs, the index, or the working tree;
- create or delete review-mode markers; or
- start, resume, or complete requestor or reviewer work.

Repeated status calls over unchanged durable state must report the same
exchange identity and must leave that state unchanged. The command must work
after process or machine restarts without relying on the earlier prompt.

## Acceptance criteria for review status

1. The installed llm-shared plugin exposes a `review-status-command` skill that
   is discoverable as `$llm-shared:review-status-command`.
2. The skill has one canonical root instruction, uses thin LLM-specific
   adapters, and delegates status collection to `rvw_status` without copying
   the command's discovery or classification logic.
3. A repository-root `rvw_status` command and shared implementation are
   available for specification and implementation-code reviews, resolve the
   caller repository by default, accept an explicit root override, and agree
   when invoked from the same working directory.
4. The command discovers live exchanges without requiring identity arguments
   or resolving the repository from the launcher's installed location.
5. Every active exchange explicitly reports the continuing agent as either a
   `requestor` or a `reviewer` in human-readable output.
6. The structured result carries the same unambiguous continuing-role identity.
7. An exchange with an umbrella visibly reports the exact umbrella draft path
   in both output forms.
8. An exchange without an umbrella explicitly reports that absence.
9. The result includes state, family, reviewed document, applicable step,
   round, occurrence, protocol-canonical artifact paths and their presence,
   separate owner and expected next actor, lease timestamp and derived
   freshness, and next protocol action.
10. Zero, one, and multiple exchanges are distinguished without guessing or
   silently selecting an exchange.
11. Every implemented nonterminal state is active, including
   `convergence-gate`, `owning-action-pending`, escalated, abandoned,
   interrupted, repair-pending, and inconsistent outcomes, while `idle` is
   inactive.
12. The structured result can be consumed by the later `rvw_resume` effort
   without scraping display text.
13. Status remains strictly read-only across review artifacts, coordination
    state, markers, Git state, and workflow actions.
14. Status derives its answer from durable repository evidence, reports lease
    freshness against the configured wait timeout, and works after the caller's
    prior shell or agent context has been lost.

## Scope boundaries and dependencies

This feature owns the read-only status skill, status discovery, and reporting
only. It does not implement `rvw_resume`, renew or reclaim a lease, choose among
multiple exchanges, or run requestor or reviewer actions. Those continuation
behaviors belong to the separate `review-resume-command` umbrella item.

The feature depends on the settled review exchange core and the specification
and code requestor/reviewer roles whose durable coordination records it reads.
