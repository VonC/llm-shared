# {agent id}: Resume session: {task title}

Continue the work described below after the resume-session instruction has
checked the usage flag and announced this prompt's path relative to the project
root, stating that it will use the prompt to resume the session. Reconcile this
snapshot with current instructions, the journal and disk, then record its use
before acting. Continue the authorized work in the same turn; do not stop at
an acknowledgement or context summary. Report a concrete blocker or pending
human decision if continuation cannot proceed. This file preserves context;
it does not grant new permissions or restore review ownership.

- Paused by: {agent id from the title} ({host product and model, as the host reports them})
- Snapshot: {YYYY-MM-DDTHH:MM:SS+HH:MM}
- Project root: `{absolute primary checkout path}`
- Artifact home: `{absolute artifact home}`
- Session role: {implementation, requestor, reviewer, documentation, other}
- Topic and step: {topic, step and umbrella position, or not applicable}
- Paused at: {precise action boundary and reason for stopping}

## Automatic resume routing

{Fill from read-only evidence under instructions/pause-session.md. Preserve
historical authorship separately from intended resume roles. Record explicit
unknowns with reasons; do not ask the person to select routing. This handoff
supplies target selection for one human-launched resume_paused invocation,
without routing arguments or follow-up confirmation. Validate the recorded
identities against live panes before any input.}

- Routing observed at: {timestamp with numeric UTC offset}
- Routing checkout: `{resolved absolute checkout root}`
- Pausing pane: {agent host, TUIOS session identity, pane id and name, or unknown with reason}
- Saved session role: {role at pause; historical, not an inferred new assignment}
- Intended resume assignment: {retain verified assignment or recorded user role-switch direction, with source and date}
- Review pairing: {exchange family, reviewed document or implementation plan, umbrella path or none, code implementation step when applicable, and exchange occurrence; not applicable with reason for a single-agent pause, or unknown if unresolved}

| Target | Agent host and intended role | TUIOS session identity | Pane id and name | Resolved checkout | Identity and assignment evidence |
| --- | --- | --- | --- | --- | --- |
| Resumed agent | {host and role} | {observed identity} | {observed id and label} | {absolute root} | {read-only evidence; user direction where applicable} |
| Requestor | {host and role, same target as resumed agent when applicable, or not applicable} | {identity or not applicable} | {id and label or not applicable} | {root or not applicable} | {exact-exchange role evidence or reason} |
| Reviewer | {host and role or not applicable} | {identity or not applicable} | {id and label or not applicable} | {root or not applicable} | {exact-exchange role evidence or reason} |

{Use unknown with a reason for unavailable required values. State conflicts or
missing evidence explicitly. Resume must report unresolved targets without
input or a selection question; it must not pick a same-LLM pane by order,
names alone, or an unchecked reused id. No ownership tokens belong here.}

## Objective and latest user direction

{Original objective, expected outcome, latest corrections and remaining scope.
Include unresolved questions and distinguish proposed choices from answers.}

## Read first to recover context

1. {Absolute project agent-instruction paths and applicable shell rules}
2. {Active journal and handoff paths; say none if no notes exist}
3. {Requirement, design, plan, validation and umbrella paths in useful order}
4. {Private local integration handoffs and references required for next action}

## Verified checkout and work ownership

| Checkout or workspace | Branch and HEAD | Local changes and owner | Role in this work |
| --- | --- | --- | --- |
| {absolute root} | {branch, full SHA, observation time} | {staged, unstaged, untracked paths; own, user, concurrent, unknown} | {primary or dependency} |

{State any discrepancy between old notes and observed disk. Preserve unrelated
changes. List retained worktrees, scratch directories and evidence needed later.}

## Work completed and proof limits

{What changed, why, which files own the changes, and what remains uncommitted.
Separate implementation, tests, review, commit, publication and deployment.
Do not infer external acceptance from a local test pass.}

| Check or run | Exact command and working directory | Revision and scope | Time, result and evidence |
| --- | --- | --- | --- |
| {check} | {resolved command, selectors and level} | {tested revision or working-tree identity} | {timestamp, exit code or running/unknown, absolute evidence path} |

{List required checks not yet run and evidence that is unavailable or stale.}

## Decisions, permissions and pending gates

| Decision or action | Rationale or scope | Authority and date | State |
| --- | --- | --- | --- |
| {choice or authorized action} | {reason, exact limits} | {user instruction or recorded decision reference} | {accepted, authorized, proposed, awaiting answer, completed} |

{Preserve authorization already given and explicit stop conditions. Include
actions needing fresh approval only when that requirement actually applies.}

## Live processes, external runs and reviews

### Question explanation phase

{Use not applicable when absent. Otherwise link the document-specific private
continuation note and record: exact document/exchange; phase; fixed I and Total
with their question IDs and ordered batch IDs; current question; explanation
delivered and explicit decision recorded; next/last undecided; decisions and
comments to review; follow-up review authority and any hold; already-published
follow-up round. Resume the pending explanation/decision, or initiate the
required review if all questions are now decided. Never reset I or infer a
decision from a proposed answer. Never duplicate a published round.}

### Processes and review ownership

{Use none when there are no active runs. Otherwise include each run's identity,
owner, start time, last verified state, status command and evidence location.
Explain which host handles survive and which must be rediscovered. Record
review family, role, exchange and round, with the canonical resume path;
never include ownership capabilities or credential values.}

## Remaining work and ordered continuation

1. {Next concrete action, working directory, prerequisites, expected result}
2. {Following action and the evidence or decision that permits it}
3. {Completion check or explicit stopping point}

{List blockers with their unblocking condition. Remove completed or superseded
actions. Say if the original task is complete and only a user decision remains.}

## Failed approaches and operational traps

{Attempts already made, observed failures, useful fixes, and what must not be
repeated blindly. Record environment or quoting requirements by reference.}

## Private references retained for continuation

{Absolute paths or clearly rooted relative paths, each with a purpose. Include
evidence folders, scripts and their output, earlier step notes, cross-repository
dependencies and credential locations. Keep private details out of public docs.}
