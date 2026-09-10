# Independent review mode contract

<img src="../assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="200" align="right">

<!-- markdownlint-disable MD013 -->

This reference defines the observable marker, identity, artifact, state,
operation, result, and adapter contract for the marker-gated two-agent
exchange. Use the tutorials and how-to guides for procedures.

## Invocation model

Normal journeys start through `pw` and the appropriate writing or
implementation skill. Full launchers are for reference, recovery, and direct
reviewer operation. Every operation returns one final result; follow that
result instead of discovering nearby files.

Role-session provenance is external to the exchange. A requestor may publish
and wait but may never start, spawn, delegate to, invoke, or message a reviewer.
A reviewer may assess or wait but may never do those things to a requestor.
Each role rejects a task initiated by its automated counterpart, even when the
durable state names that role as the next actor. A human or external reviewer
service may start the independent reviewer; a valid route alone is not valid
provenance.

Automatic intermediate exchange uses reciprocal waiting. The requestor's
`wait-answer` is bounded to its exact exchange. After every answer the reviewer
runs the quiet foreground `wait-any-request` in the same session. This global
wait has no exchange timeout while idle and accepts either review family under
the configured home. A replacement request wakes it after requestor work or a
human's another-round choice; convergence leaves the human gate intact.
Native events trigger authoritative rescans, with bounded polling fallback.
`already-claimed` losers return to waiting. Intact expired leases remain
recoverable; damaged, inconsistent, escalated and repair-required evidence stops
the operation. Repeated status calls are not the wait interface.

A new agent process has no access to a prior process's plaintext ownership
token. A bare `resume` authorizes automatic `claim` after migration and role
inspection. A missing or stale capability causes lease-independent pickup,
which advances the durable ownership generation and returns a replacement
capability. At
`convergence-gate` and `owning-action-pending`, the pickup actor is the
requestor; in other live states it is the expected LLM actor. Pickup does not
change the round, artifacts, or human decision owner.

The canonical [shared requestor instruction](../../instructions/review-requestor.md),
[specification reviewer instruction](../../instructions/spec-reviewer.md), and
[code reviewer instruction](../../instructions/code-reviewer.md) remain
authoritative for agent policy. This page states their user-visible contract in
reference form and does not replace those instructions.

When `bin/review_exchange.bat` runs from another repository's Git root, that
current root overrides an unrelated inherited `PRJ_DIR`. The launcher also
places llm-shared first on `PYTHONPATH`, so a consuming repository's own
`tools` package cannot replace the shared protocol modules.

## Artifact-home configuration and migration

All protocol-owned runtime artifacts resolve through one repository-local home.
Without a declaration, the home is `.reviews`. To select another home, commit
one strict `.review-artifacts.ini` at the repository root:

```ini
[review-artifacts]
home = runtime/reviews
```

The file accepts exactly that section and property. The value must be a
nonempty repository-relative path that resolves physically inside the
repository, is not the repository root, and does not name an existing tracked
directory. Environment-variable, tilde, drive, and absolute-path expansion are
not supported. The home contains a `.gitignore` whose exact rule is `*`, so
runtime evidence remains untracked.

Placement recognizes the closed review-artifact registry in the legacy project
root, `.reviews`, and the configured home. Migration is transactional under an
exclusive lock and a versioned JSON journal. Equal-byte duplicates can be
settled safely; different-byte collisions, invalid ignore coverage, unreadable
evidence, or incomplete recovery block migration rather than selecting a copy.

`rvw_status.bat` owns the currently shipped automatic migration entry point. It
checks placement, migrates only when required, rechecks readiness, and only then
projects exchange state. After that bounded preflight, status does not mutate
the exchange.

## Marker and exchange identity

The artifact-home `a.review-mode` file opts later workflow entry into independent
review mode. The home marker wins over a legacy project-root marker. An empty file selects the default wait. One line of the form
`wait_timeout_seconds=<positive integer>` selects another bounded wait. An
absent marker produces `state: disabled`; invalid marker content produces the
fatal result described below.

The default wait itself comes from a `.review-exchange.ini` file, read in this
order and stopping at the first usable value:

| Source | Wins over | On invalid content |
| --- | --- | --- |
| `wait_timeout_seconds=` in the effective artifact-home `a.review-mode` (legacy root fallback) | everything | fatal |
| `.review-exchange.ini` at the reviewed repository root | the shipped file | ignored |
| `.review-exchange.ini` shipped with llm-shared, currently 10,800 seconds (three hours) | nothing | ignored |

The two treatments differ on purpose. A marker override was written for that
exchange, so a mistake in it must stop the run. A settings file may belong to a
repository that never meant to configure a review, so an unreadable file, a
missing section or key, or a value that is not a positive integer is ignored and
the next source applies. A broken settings file never stops a review.

Every exchange identity contains:

| Field | Meaning |
| --- | --- |
| `family` | `specification` or `code` |
| `type_token` | Reviewed document type, or `code` for implementation review |
| `version` | Exact `vX.Y.Z` token |
| `slug` | Exact effort slug |
| `implementation_step` | Positive step identifier for code review only |

The command context also carries the exact reviewed document, optional umbrella
draft, convergence signal, another-round label, and owning-workflow label.
Identity and context must agree with every durable envelope.

## Role identity and ownership

New request, answer, and coordination schemas preserve separate
`requestor_llm_nature` and `reviewer_llm_nature` snapshots. Each known value is
`claude`, `codex`, `gemini`, or `unknown`. Legacy artifacts may omit the two
fields; status renders that absence as `unrecorded`. If durable artifacts
disagree, status renders `conflicting` and retains every evidence path instead
of guessing or rewriting a value.

Every acting session uses an ownership generation and plaintext token returned
by its claim or pickup. Coordination stores only the token's SHA-256 digest.
Every later mutation supplies both values, while status remains capability-free.
A forced pickup advances the generation under the transition lock and makes all
older capabilities fail as superseded. Tokens do not appear in transcripts,
diagnostics, or human status output.

## Artifact and path contract

Artifact names help with orientation only. The final result's returned `paths`
object selects the files for the next action; do not reconstruct names, search
for a nearby version, or edit protocol artifacts by hand.

| Kind | Location and lifetime | Naming grammar or source |
| --- | --- | --- |
| Request | Artifact home; transient | `a.review-requested.<type>.<version>.<slug>.md` |
| Answer | Artifact home; transient | `a.review-answer.<type>.<version>.<slug>.md` |
| Coordination | Artifact home; durable while live | `a.review-active.<family>.<type>.<version>.<slug>.md` |
| Consumed request tombstone | Artifact home; transient while needed | `a.review-consumed.<family>.<type>.<version>.<slug>.md` |
| Transition lock | Artifact home; process-local coordination | `a.review-lock.<family>.<type>.<version>.<slug>.lock` |
| Transcript | Beside reviewed document; versioned durable evidence | `review.<type>.<version>.<slug>.md` |
| Recovery archive | Artifact home; ignored durable evidence | `a.review-archive.<family>.<type>.<version>.<slug>.<timestamp>.<kind>.md` |
| Code evidence manifest | Artifact home; ignored reviewer evidence | `a.code-review-evidence.<version>.<slug>.step-<step>.json` |
| Migration journal | Artifact home; transactional only | `a.review-artifact-migration.json` |

Requests and answers are renderer-owned envelopes. Coordination and tombstones
make transitions recoverable. Transcript entries are append-only evidence.
Code reviewers retire their ignored evidence manifest after answer publication.

Renderer-owned section headings end with `(round N)`. Headings inside authored
assessment, change, response, and guidance blocks are nested below their parent
section, retain their relative depth, and receive the round identity as their
final suffix. Headings inside fenced examples remain literal. Human guidance is
rendered as a separate nested block below its generated label; publication
checks that canonical form while still accepting exact legacy guidance from an
older round. Callers supply section content and never rewrite renderer-owned
headings in a request, answer, or transcript.

## State matrix

The first fifteen rows come from `ArtifactState`. `disabled` is the
launcher-only absent-marker result. `fatal` is the stable exit-2 payload state.
Each row names the actor who owns the next decision or the recorded actor when
ownership depends on durable coordination.

| State | Lifecycle group | Owner | Next action |
| --- | --- | --- | --- |
| `idle` | Not yet started | requestor | Start a new round |
| `round-in-progress` | Active exchange | requestor | Author and publish the request |
| `request-pending` | Active exchange | reviewer | Assess the request and publish an answer |
| `answer-publication-in-progress` | Interrupted publication | reviewer | Retry the recorded answer publication |
| `transcript-repair-pending` | Interrupted transcript append | recorded actor | Retry the recorded append or repair the eligible request entry |
| `answer-pending` | Active exchange | requestor | Consume changes or present convergence to the human |
| `convergence-gate` | Human gate | human | Choose the registered another-round or owning-workflow label |
| `owning-action-pending` | Authorized continuation | requestor | Perform every authorized consolidation or commit batch, require its clean-tree postcondition, then complete |
| `escalated` | Stopped exchange | human | Choose forced reclaim, resolve, archive, or cancellation as applicable |
| `abandoned-mid-round` | Expired lease without counterpart artifact | recorded actor or human | Reclaim the round, or human-close it with forced completion |
| `interrupted-answer-publication` | Interrupted publication | reviewer | Resume the recorded publication transition |
| `interrupted-transcript-append` | Interrupted transcript append | recorded actor | Retry the recorded transcript transition |
| `abandoned-request` | Expired request lease | reviewer | Reclaim the intact request and continue assessment |
| `abandoned-answer` | Expired answer lease | requestor | Reclaim the intact answer and continue response handling |
| `inconsistent` | Invalid artifact shape | human | Stop automation and resolve or archive authoritative evidence |
| `disabled` | Not yet started | caller | Create a valid marker before starting independent review |
| `fatal` | Invalid input or refused operation | caller | Correct the input and re-run; payload has null `identity`, empty `paths`, null round, and `fatal-input` outcome |

The `answer-pending` owner remains the requestor even while the reviewer has an
active post-publication `wait-any-request`. The wait observes the state; it does not
grant answer consumption, round continuation, or any writer-owned action to the
reviewer.

## Repository status schema 2

`rvw_status.bat` discovers the Git root upward from the caller, unless
`--root <project-root>` names an exact Git root. Human output is the default;
`--format json` emits one compact schema-2 object. The launcher neither resumes
an exchange nor grants authority to the reported role.

The repository object contains:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `2` |
| `repository_root` | Resolved absolute Git root |
| `outcome` | `trustworthy`, `untrustworthy`, or `operational-failure` |
| `active_count` | Count of healthy exchanges and retained damaged candidates |
| `has_errors` | Whether the result is not wholly trustworthy |
| `migration` | State, artifact home, moved count, and diagnostics |
| `exchanges` | Healthy exchange objects or explicitly tagged damaged candidates |

A healthy exchange reports its complete identity, reviewed document, umbrella,
implementation step, round and occurrence, protocol state, continuing role and
specialization, owner, lease, six canonical artifact observations, both role
natures and their evidence arrays, and a typed next action. The next-action
vocabulary is `wait-for-counterpart`, `requestor-work`, `reviewer-work`,
`human-confirmation`, `authorized-owning-work`, `reclaim`, `repair`,
`resolve-escalation`, and `no-safe-action`.

`human-confirmation` is valid only when durable state is already at a human
gate. A newly published, unanswered request reports `request-pending`,
reviewer ownership, and `reviewer-work`. Role-nature evidence identifies what
the artifacts recorded; it never authorizes status to create that role.

- Exit `0` means the complete status result is trustworthy, including an empty
  exchange list.
- Exit `3` retains useful evidence but at least one candidate is untrustworthy.
- Exit `2` means arguments, repository discovery, configuration, or migration
  prevented trustworthy projection. Operational-failure output goes to standard
  error and does not contain inferred exchanges.

## Operation summary

All commands enter through `bin/review_exchange.bat`. The caller supplies the
same exact context on every invocation.

| Operation | Actor and precondition | Successful effect and outcome |
| --- | --- | --- |
| `activate` | entering requestor or reviewer; valid marker and ignored paths | Validate the fixed path set; `activated` |
| `status` | any caller | Observe current state; `observed`, or `disabled` without the marker |
| `start` | requestor; idle exchange | Open round 1; `started` |
| `continue` | requestor; consumed intermediate answer | Advance to the next round; `continued` |
| `publish-request` | requestor; round in progress | Store request and append transcript; `published` |
| `wait-request` | reviewer; optional bounded exact-request wait | Return the next exact request as `found`, or `timed-out`, `abandoned`, `escalated`, `inconsistent`, or `repair-required` |
| `publish-answer` | reviewer; request pending | Consume request, expose answer, and append transcript; `published` |
| `wait-answer` | requestor; bounded wait | Return the same wait outcomes as `wait-request` |
| `consume-answer` | requestor; non-converged answer | Record response assessment; `consumed` |
| `pickup` | explicitly authorized new LLM session; valid live coordination | Advance ownership generation, fence the old capability, and return the new requestor or expected-actor capability; `ownership-picked-up` |
| `reclaim` | expected actor; intact lease-expired round | Renew the same round; `reclaimed` |
| `reclaim --force` | human-authorized caller; intact escalated artifacts | Resume the same round and append the decision; `force-reclaimed` |
| `repair-request-transcript` | requestor; eligible final legacy request entry | Replace only that final entry; `repaired` |
| `escalate` | owning automated role; automation must stop | Preserve authored reason; `escalated` |
| `confirm` | human at convergence | Return `another-round` or `continue-owning-workflow` |
| `cancel` | human at convergence | End the exchange with authored evidence; `cancelled` |
| `complete` | requestor; authorized owning action succeeded | Remove live coordination; `completed` |
| `complete --force` | human-authorized caller; intact artifact-free abandonment | Append the close decision and remove coordination; `force-completed` |
| `resolve` | human-authorized caller; stopped authoritative evidence | Clear stopped artifacts and start a fresh round; `resolved` |
| `archive` | human-authorized caller; stopped authoritative evidence | Archive stopped artifacts and start a fresh round; `archived` |

## Operation outcome snapshot

Operation outcomes are the one contract column without a single typed model.
This v0.11.0 snapshot is pinned from plain `OperationResult` construction and
conditional `OperationResult` construction. It covers all `WaitOutcome` values
and both `ConfirmationOutcome` values, plus the CLI fatal payload. Later
launcher changes must update this table deliberately; this effort does not add
AST drift tooling.

| Outcome | Source shape |
| --- | --- |
| `disabled` | Plain operation result |
| `activated` | Plain operation result |
| `observed` | Plain operation result |
| `started` | Plain operation result |
| `continued` | Plain operation result |
| `ownership-picked-up` | Plain operation result with a newly issued capability |
| `reclaimed` | Plain operation result |
| `force-reclaimed` | Plain operation result |
| `completed` | Conditional operation result |
| `force-completed` | Conditional operation result |
| `published` | Plain operation result |
| `repaired` | Plain operation result |
| `found` | Wait outcome |
| `timed-out` | Wait outcome |
| `abandoned` | Wait outcome |
| `escalated` | Wait outcome or plain operation result |
| `inconsistent` | Wait outcome |
| `repair-required` | Wait outcome |
| `consumed` | Plain operation result |
| `cancelled` | Plain operation result |
| `archived` | Conditional operation result |
| `resolved` | Conditional operation result |
| `another-round` | Confirmation outcome |
| `continue-owning-workflow` | Confirmation outcome |
| `fatal-input` | CLI fatal payload |

## Final result contract

Each invocation writes one final JSON object on standard output. During a wait,
standard error is progress only. The returned `paths` object is authoritative
for artifact access; a caller must not infer a path from the identity grammar.

The success payload always has seven fields:

| Field | Meaning |
| --- | --- |
| `diagnostic` | Human-readable state or failure detail |
| `identity` | Exact family, type, version, and slug, except null on fatal input |
| `operation` | Requested CLI operation |
| `outcome` | One value from the reviewed snapshot |
| `paths` | Six fixed path keys, except an empty object on fatal input |
| `round` | Current positive round, or null when no round exists |
| `state` | One value from the state matrix |

The six success-path keys are:

| Key | Artifact |
| --- | --- |
| `answer` | Current reviewer answer |
| `coordination` | Durable live exchange record |
| `request` | Current request |
| `tombstone` | Consumed request evidence |
| `transcript` | Versioned append-only review record |
| `transition_lock` | Transition lock |

Additional fields are conditional. `exchange_occurrence` appears for a pending
request, `owning_action_authorized` appears after human confirmation,
`ownership_generation` and `ownership_token` appear only when an operation
issues a capability, and some operations report removed or archived paths.
The token is returned once in that invocation and is never stored in plaintext
coordination or transcript evidence. Both ownership fields must be supplied to
later fenced mutations.

- Exit `0` means the operation completed and the result grants its reported
  next action.
- Exit `3` is an expected stop such as disabled mode, a bounded wait result,
  recovery state, convergence, or pending authorized work.
- Exit `2` reports invalid input or an unexpected fatal error. Correct the
  input; do not open or edit an artifact from the empty fatal `paths` object.

Specification convergence presents `Consolidate` and
`Revise and review again`. Code convergence presents `Commit` and
`Rework and review again`. A reviewer recommendation is advisory; only the
registered human choice can authorize consolidation or commit.
An authorized specification consolidation first creates a one-file Git commit
of the answered specification. It resets and verifies the index before staging
that file, then verifies the snapshot and an empty index before folding or
stripping any question content. When the fold settles the specification, the
same authorization covers repository-wide staging, grouped commits for every
remaining path, and one bounded recovery pass. The requestor may complete the
exchange or run `pw skill` only after `git status --porcelain` is empty.

An authorized code commit first validates and executes the reviewed root
`a.commit`. If any non-ignored change remains, `pw code-review-commit` stages
the complete remainder and preserves `owning-action-pending` while the
requestor prepares a replacement `a.commit` through `group-commits-msg`
without another human menu. `pw code-review-commit --residual` executes that
plan, requires an empty porcelain status, and only then completes the exchange.

## Host adapter matrix

Host adapters contain discovery metadata and delegate to canonical root
instructions. They do not copy policy bodies.

| Host | Wrapper location | Prefix | Review wrappers or gap | Delegation boundary |
| --- | --- | --- | --- | --- |
| Codex | `.agents/llm-shared/skills/` | `$` | `review-requestor`, both family requestors, and both reviewers | Each `SKILL.md` reads the canonical root instruction |
| Claude Code | `.claude/skills/` | `/` | shared `review-requestor` is absent; use the existing family-specific requestor or reviewer | Each family `SKILL.md` reads the canonical root instruction |
| Antigravity | `.agent/workflows/` | `/` | `review-requestor`, both family requestors, and both reviewers | Each workflow locates and reads the canonical root instruction |

The missing Claude shared wrapper is recorded rather than hidden. Adding host
wrappers is outside this documentation effort.

## Focused procedures and policy owners

Use these task pages instead of deriving a procedure from the tables:

- [Activate or deactivate independent review mode](../how-to/enable-independent-review-mode.md)
- [Run specification review](../how-to/run-specification-review.md)
- [Run implementation code review](../how-to/run-implementation-code-review.md)
- [Inspect independent review status](../how-to/inspect-independent-review-status.md)
- [Read results and continue authorized work](../how-to/read-independent-review-results-and-continue.md)
- [Recover an independent review](../how-to/recover-an-independent-review.md)

The shared requestor instruction owns coordination and human recovery policy.
The family requestor instructions own writer-side specialization. The
specification and code reviewer instructions own independent assessment and
answer publication. Launchers and typed models remain authoritative for
machine-readable state and result shapes.

## Shipped sources

- [Review exchange models](../../tools/review_exchange_models.py)
- [Review exchange CLI](../../tools/review_exchange_cli.py)
- [Artifact-home configuration](../../tools/review_artifact_configuration.py)
- [Artifact registry](../../tools/review_artifact_registry.py)
- [Artifact migration](../../tools/review_artifact_migration.py)
- [Ownership service](../../tools/review_exchange_ownership.py)
- [Repository review status](../../tools/review_status.py)
- [Review status schema](../../tools/review_status_models.py)
- [Artifact path derivation](../../tools/review_exchange_paths.py)
- [Specification requestor instruction](../../instructions/spec-review-requestor.md)
- [Code requestor instruction](../../instructions/code-review-requestor.md)
- [Review request template](../../templates/review-request.template.md)
- [Review answer template](../../templates/review-answer.template.md)

Related: [pw launcher](pw-launcher.md),
[artifact files](artifact-files.md),
[aliases and launchers](aliases-and-launchers.md), and
[document templates](templates.md).

## Resume support operations

The public entry point is the [review-resume skill](../../instructions/review-resume.md),
invoked with the bare text `resume`. The existing shared launcher supplies
its internal operations; no shell resume launcher is installed.

| Operation | Scope | Result |
| --- | --- | --- |
| `migration-check` | Repository, before status or role inspection | Ready, migration-required, or blocked placement |
| `migrate-artifacts` | Safe recognized legacy set | Transactional move or recovery, followed by a required check |
| `resume-inspect` | Optional exact document, step and selected role | Typed candidate, role and next action, or a human ambiguity/conflict gate |
| `claim` | Exact selected document, role, round and occurrence | Automatic pickup or idempotent reuse of the supplied capability |
| `wait-any-request` | Identity-free reviewer wait in the configured home | One claimed request, ambiguity, cancellation, or operational failure |

The foreground global wait writes no idle output. Its final JSON has
`operation`, `outcome`, `identity`, `candidates`, and `diagnostic`.
Only `found` includes the session-only ownership generation and token.
Exit codes are 0 for `found`, 3 for `ambiguous` or `cancelled`, and 2
for invalid input or operational failure. Graceful interruption returns
`cancelled`; a hard process kill may return nothing. No waiter state is persisted.

A requestor remains on its exact exchange and immediately runs and follows
`pw skill` after release. A reviewer returns to the global wait after every
answer and never enters the requestor workflow.
