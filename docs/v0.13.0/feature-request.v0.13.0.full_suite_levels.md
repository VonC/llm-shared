# Full suite levels for the ghog day walk

- Draft: docs/v0.13.0/draft.v0.13.0.full_suite_levels.md

## CDC revision that introduces full suite levels

Until v0.12.0, the groundhog objective was a single one: every `ghog day` walk
runs check.bat, then `ghog affected --no-cov`, then `ghog full`, and is meant
to be green only when the full suite passes, meets the coverage gate, and
shows no duration outlier (in a parallel project, the full run does not
actually measure durations; see "Current behavior in v0.12.0"). Every
development skill closes its work with that walk.

The revision keeps that objective for the final phases only. During
development, the walk stops after the affected tests. The full suite runs on
demand, at one of three levels chosen by the caller:

| Level | The full run fails on | The full run ignores |
| --- | --- | --- |
| `pass` | test failures (exit 2), suite crash (exit 4) | coverage gap (exit 3), duration outliers (exit 8) |
| `cov` | exits 2 and 4, coverage gap (exit 3) | duration outliers (exit 8) |
| `speed` | exits 2, 4, 3 and duration outliers (exit 8) | nothing (today's behavior) |

The prepare-release green gate asks for `cov`. Under the default requestor
validation policy, every code-review request, from round 1, is published
after a green `speed` walk, so each request enters review with `speed`
evidence, and every change made for speed (tests, production code, or a
duration exclusion) goes through ordinary review. An explicit project
validation declaration is governed by Q14. No `speed` walk runs at the
commit-ready answer.

Revision of 2026-09-30: the first consolidated version of this requirement
ran the `speed` pass after review, at the commit-ready answer, and needed a
test-only exception, a repair baseline, and a new requestor transition out of
the convergence gate to handle the repairs it made there. The requirement
was reopened to move `speed` before review instead; the superseded decisions
are marked in "Requirement clarifications for full suite levels". A recheck
of `speed` at the commit-ready answer was considered during the reopening and
dropped by the human: under the default validation policy, the last request
was already validated at `speed`, and only polishing edits may accompany a
commit-ready answer.

Revision of 2026-09-30, test groups: during an effort, the full suite can be
narrowed to a declared test group. A sentinel effort, for instance, runs only
the test files under `tests` folders whose name contains `sentinel`, and its
100% coverage gate applies to the group's declared source files, covered by
the group's tests only. Development walks, the requestor's default validation
before each review request (a project-declared validation set follows Q14),
and the review-off `speed` pass run the effort's group;
for a grouped effort, only prepare-release runs the whole suite, at `cov`.
Ungrouped efforts and explicit whole-suite commands still run everything.

Revision of 2026-09-30, group activation: the requirement said how a group is
declared, but not when an effort is asked about one, how a group is turned
on, changed or off partway through an effort (setting `GHOG_GROUP` cannot do
it for workflow walks, since an ungrouped effort uses the explicit whole-suite
selector), what an active code review learns of a scope change, or where the
current scope is shown. Gap 24 and questions Q22 to Q26 cover these.

## Current behavior in v0.12.0

- `run_day` in `tools/groundhog/day.py` always walks the three steps and
  always ends on the full run when the first two are green.
- The full run reports and stops on a coverage gap (exit 3) with a covg
  next step, and on a duration outlier (exit 8) with a request to shorten the
  flagged calls through `fix_slow_test.md`.
- A green walk writes the source snapshot `a.ghog.day.ok`; the next walk with
  unchanged sources is a noop, whatever reason the caller had to run it.
- These instructions end their work with a `ghog day` walk repeated until
  exit 0: `implement-step.md`, `implement-missing-step.md`,
  `split-large-file.md`, `groundhog.md`, and `fix_slow_test.md`.
- `write-plans.md` writes `ghog day` into every plan step as its
  ready-to-run command.
- The code-review requestor must run its validation set green before it
  publishes a request, and that set always holds the `ghog day` project
  default (`tools/code_review_validation.py`).
- The prepare-release green-gate routine runs `ghog day` after main is merged
  into an integration branch and after a feature `--onto` replay
  (`tools/prepare_release/prepare_release_plan_workflow.py`).
- At a commit-ready convergence, the requestor presents the human gate
  directly; it cannot start a new round from convergence.
- In a project with a `.ghog-parallel` marker (llm-shared included),
  `ghog full` runs on xdist workers without measuring durations; only the
  sequential `ghog timings` pass judges the duration gate there, and no
  instruction runs it, so no workflow judges speed in such a project today.
- The code reviewer and implementation-check never run `ghog day` or
  `ghog full`; they are limited to `ghog check` and `ghog affected --no-cov`.

## Gap to close in the implementation for full suite levels

1. Default walk without the full suite: when no level is supplied (neither
   `--full` nor `GHOG_FULL`), `ghog day` runs check.bat, then
   `ghog affected --no-cov`, and stops. Its closing lines state that the full
   suite was not run. A default invocation does not itself establish fresh
   coverage or speed proof; its report separately identifies any stronger
   valid saved proof it reuses.
2. Level selection: `ghog day` and a direct `ghog full` both accept a level
   through the `--full=pass|cov|speed` parameter or the `GHOG_FULL`
   environment variable, with one precedence rule (Q02): the explicit
   parameter, then `GHOG_FULL`, then the command default (`ghog day`: no full
   step; `ghog full`: `speed`). Development walks called with no level pick
   `GHOG_FULL` up. An unknown value is a setup error (exit 5), never a silent
   fallback to the default. Examples:
   - `GHOG_FULL` unset: `ghog day` stops after the affected tests; `ghog full`
     runs at `speed`;
   - `GHOG_FULL=cov`: `ghog day` and `ghog full` both run the full suite at
     `cov`;
   - `GHOG_FULL=cov` and `--full=speed`: both commands run at `speed`.
3. Level verdicts: at `pass`, every test of the selected scope (the whole
   suite, or a group, gap 20) runs and must pass without a suite crash; it runs without coverage collection or duration enforcement,
   and any recorded durations are informational (Q01). At `cov`, duration
   outliers do not fail the run. At `speed`, the run keeps today's verdicts,
   and the duration gate is judged by a run that measures call times without
   worker contention: in a parallel project, a `speed` walk includes the
   sequential timing pass.
4. Closing instructions by level: the report ends with the instruction the
   LLM must act on, as listed in "Closing instructions for the LLM by level"
   below. It only asks for the work its level covers: no covg or
   coverage-gap request below `cov`, no slow-test request below `speed`.
   Every printed restart line names the level of the walk it restarts (for
   example `ghog day --full=cov`), whatever the source of that level, so an
   LLM following the line literally never drops back to the default walk. A
   default walk restarts with plain `ghog day`.
5. Evidence reported by every walk (Q08): the closing report and
   `ghog status` state the selected objective and its source (parameter,
   variable, or default), the strongest valid saved proof, and whether each
   step ran or was reused. A detached walk keeps the level selected for its
   invocation. Field names and encoding are left to the design; compatibility
   with the supported consumers of the closing line is a requirement to
   verify.
6. Level-aware snapshot: `a.ghog.day.ok` stores the highest level the green
   walk proved (none, `pass`, `cov`, `speed`). A walk is a noop only when
   sources are unchanged and the recorded level is at least the requested
   one; a green default walk never turns a later `cov` or `speed` walk into a
   noop. A green full run at a lower level never proves a higher one.
7. Level upgrade on unchanged sources (Q03): a walk that requests a higher
   level than the recorded one may reuse the successful check and
   affected-test results of the same validated snapshot, runs the missing
   full-suite objective, and identifies the reused results in its report.
8. Snapshots without an established level (Q10): a saved result that cannot
   establish its achieved level (a snapshot written before this change, or
   missing or invalid level information) satisfies no requested level. The
   first requested walk after the upgrade revalidates its selected objective,
   which may be the lightweight default; the next successful walk records
   explicit evidence.
9. Direct `ghog full`: `ghog full` follows the selection rule of gap 2 and
   keeps `speed` as its default when no selector is supplied, so a plain
   direct call behaves as today. A direct run states only the objective it
   actually established: in a parallel project, a green direct run at
   `speed` discloses that durations were not measured and names
   `ghog day --full=speed` for that proof, and never claims that no
   unaccepted duration outlier remains.
10. Development skills use the default walk: `implement-step.md`,
    `implement-missing-step.md`, `split-large-file.md`, and the plan command
    written by `write-plans.md` use `ghog day` with no level. Their wording no
    longer promises a full coverage pass.
11. The groundhog loop keeps the caller's level: `groundhog.md` restarts every
    fix with the same level the loop was started with, so a fix never raises
    or drops the objective. `fix_slow_test.md` applies only to a `speed` walk
    and restarts it at `speed`.
12. Requestor validation at `speed`: the code-review requestor project
    default becomes the `speed` walk (`DEFAULT_PROJECT_VALIDATION_COMMANDS` in
    `tools/code_review_validation.py`). Under that default policy, every
    code-review request, round 1 and each replacement round (Q11), is
    published after a green `speed` walk, which may reuse valid `speed`
    evidence under the snapshot rules of gaps 6 to 8. Each request therefore
    enters review with `speed` evidence. Edits that lead to a replacement
    request are covered by that request's validation. If the answer is
    commit-ready, only the permitted polishing edits may accompany it, and no
    further `speed` walk runs. Every change the requestor
    makes to reach `speed` (a test, a production file, or a duration
    exclusion) is part of the work the reviewer assesses in that round. A
    project that declares its own `.review-validation` set keeps authority
    over it (Q14): when that set holds a `ghog day` without `--full`, every
    review request shows a migration notice recommending
    `ghog day --full=speed`. The notice makes no claim about other means of
    establishing `speed` (`GHOG_FULL=speed`, another declared command, valid
    saved proof); the workflow supplies no additional `speed` validation.
13. Prepare-release green gate at `cov`: the green-gate routine in
    `prepare-release.md` and both `run ghog day` operations in
    `prepare_release_plan_workflow.py` name the `cov` walk.
14. Duration exclusions before review (Q07, revised): accepting a genuinely
    slow call with `ghog exclude` is allowed during the requestor's `speed`
    validation, only after an attempted improvement. The review request names
    the excluded call, its measured time, the attempted improvement, and the
    reason for accepting the duration, so the reviewer judges the exclusion
    like any other change. An exclusion never covers unrelated configuration
    changes or the removal of correctness or coverage checks.
15. Speed pass without review mode (Q09, reopened as Q13): this gap applies
    only when review mode is disabled. There, no review exists, and the flow
    goes from implementation-check straight to the commit menu; the `speed`
    pass runs between the two, once implementation-check reports the step
    complete. Any change it makes (tests, production code, or a duration
    exclusion) sends the step back through implementation-check, then through
    a `speed` pass that must be green, possibly by valid snapshot reuse,
    before the menu. No test-only exemption and no review exchange exist on
    this path. The prepare-release gate stays at `cov`.
16. No post-review speed work: with review mode enabled, no `speed` walk runs
    at the commit-ready answer, and the requirement defines no test-only
    boundary and no requestor transition out of the convergence gate; every
    change made for speed in review mode is made before a request and
    reviewed. A project whose declared `.review-validation` set does not
    establish `speed` therefore gets no `speed` validation before commit; the
    migration notice of Q14 is the signal to change its declaration.
17. Reviewer unchanged: the code reviewer and implementation-check still never
    run `ghog day` or `ghog full` at any level.
18. Test group declaration: a versioned file at the project root (for
    example `.ghog-groups`) maps each group name to its test file patterns
    and its source file patterns, written as gitignore-style globs matched
    against normalized repository-relative paths (Q17): the sentinel example
    reads `**/tests/**/*sentinel*/**` for tests and, for instance,
    `tools/sentinel/**` for sources. A selected group is valid only when its
    patterns resolve to at least one existing test file and at least one
    existing source file (Q21).
19. Scope selection: `ghog day`, `ghog full` and the repair commands
    (`ghog check`, `ghog affected`, `ghog single`) accept `--group=<name>`
    and an explicit whole-suite selector (Q20), and read `GHOG_GROUP`, with
    the same precedence as the level: an explicit scope parameter (a group
    or the whole suite) wins, and is honored even when `GHOG_GROUP` holds an
    invalid name; otherwise `GHOG_GROUP`; otherwise the whole suite. A group
    name missing from the declaration, a declaration that cannot be read, or
    a group resolving to no test file or no source file is a setup error
    (exit 5), never a silent fallback to the whole suite. Every printed
    restart and repair line, default walks included, and every detached run
    carry the resolved scope as well as the level: plain `ghog day` means no
    `--full` selector, never the loss of the selected group, and a
    whole-suite restart names the whole-suite selector so an ambient
    `GHOG_GROUP` cannot narrow it. An effort declares its group with a
    `Test group: <name>` line in its feature request or issue; `pw` reads it,
    and every workflow-owned ghog command it prints carries that scope (Q16).
    An effort without the line uses the explicit whole-suite selector.
20. Group-scoped runs: with a group selected, the full-suite step of every
    level (`pass`, `cov`, `speed`, the timing pass included) runs only the
    test files matching the group's test patterns. At `cov` and `speed`, the
    coverage gate requires 100% of the group's declared source files,
    measured from the group's tests only, never from coverage accumulated by
    tests outside the group; a declared source file the group never executes
    counts as 0%. A grouped full or timing run that collects no test never
    establishes a green proof. With a group, the affected step runs only the
    testmon-selected tests inside the group (Q15); a valid group whose
    affected selection is empty completes that step under the existing
    no-work rules, and proves no full-suite level by itself.
21. Group scope in the workflow: workflow-owned commands use the effort's
    declared group, or the explicit whole-suite selector for an effort that
    declares none. This covers development walks, the requestor's default
    `speed` validation before each review request, the review-off `speed`
    pass, and the `ghog affected` checks run by implementation-check and by
    the code reviewer, whose permitted commands do not change. A project's
    declared `.review-validation` commands keep their authority (Q14): they
    are never rewritten or given selectors, and when they do not establish
    the effort's group proof, the request reports what they actually
    validate instead of claiming the group guarantee. The prepare-release
    green gate always uses the explicit whole-suite selector at `cov`, so
    `GHOG_GROUP` can never narrow it; manual commands with no explicit scope
    may still follow `GHOG_GROUP`.
22. Group trade-off: with a group, a change that breaks a test outside the
    group, or leaves code outside the group's sources uncovered, is not
    caught before review or commit; it surfaces at the prepare-release gate.
23. Group evidence: the closing line and `ghog status` name the selected
    scope (the group or the whole suite). A saved proof is valid only for the
    exact scope it was earned on: the same group name with the same test
    patterns, source patterns and effective file membership, or the whole
    suite, under the same gate configuration, timing floor included (Q18).
    Changing a group's patterns or membership invalidates its proof, for
    default-level noops and level upgrades as well as full levels. Group
    runs judge durations against the saved whole-suite floor, or its
    one-second fallback, without rewriting it (Q19).
24. Group activation and change: the effort records an explicit scope
    choice, a named group or the whole suite, when its draft is processed,
    and the requirement carries it (Q22, Q26). Once the requirement exists,
    it alone controls the effort's workflow scope; its absent `Test group:`
    line means the whole suite, and a draft is never a fallback. Selecting a
    group is distinct from editing its shared definition: activation adds the
    name to the requirement, switching replaces it, deactivation removes it,
    and none of them deletes or overwrites a group entry other efforts may
    use (Q23). A scope change is a change of selected group, a switch to or
    from the whole suite, or a change to the selected group's resolved
    definition (patterns or membership). It takes effect at the next eligible
    workflow boundary, never inside a published review round or a walk
    already started (Q24). No proof from a different scope is ever reused; a
    destination scope may reuse its own still-valid proof under Q18. The
    effort's declared scope, its source, and any change still pending for an
    active round are visible in `pw progress` (Q25).
25. Documentation and tests: `GROUNDHOG.md`, `tools/Pytest reset specs.md`
    (new decision rows), the day walk docstrings, and the groundhog acceptance
    tests (AT11 day walk, AT16 day noop) cover the default walk, the three
    levels, the level precedence, the level-aware snapshot, and the closing
    instruction of every level and outcome, restart lines included.
    Acceptance coverage exercises a default failure against a full-level
    failure, an environment-selected level restarted explicitly, a lower
    requested level backed by a stronger saved proof, ignored duration
    observations, and the permitted duration-exclusion path. It also
    exercises a default-policy request withheld until its `speed` walk is
    green, a repaired replacement request validated again, a valid unchanged
    `speed` snapshot reused, a declared validation set preserved with its
    migration notice, a review-disabled speed repair returning through
    implementation-check before the final green `speed` pass and the menu,
    the disclosure of a green direct parallel run at `speed`, and the
    absence of any `speed` walk at a commit-ready answer, including when a
    declared validation set supplies no `speed` proof. With groups, it also
    exercises a group walk running only the group's tests, the coverage gate
    over the group's declared sources (including a never-executed source at
    0%), an unknown or unreadable group as exit 5, restart lines carrying the
    group, and prepare-release running the whole suite at `cov`. It covers
    `GHOG_GROUP=sentinel` unable to narrow prepare-release or an ungrouped
    effort, the whole-suite selector overriding an invalid `GHOG_GROUP`, a
    grouped failure restarting in the same group and a whole-suite restart
    staying whole despite an ambient group, empty test matches, empty source
    matches and an empty affected selection as three distinct outcomes, a
    group proof invalidated by changed source patterns or changed test
    membership, a group proof never satisfying another group or the whole
    suite and a whole-suite `cov` proof never masking missing group coverage,
    a declared validation set preserved without a false group claim,
    implementation-check and reviewer affected calls staying in the group,
    group success lines naming their scope, and group runs leaving the saved
    timing floor unchanged. For activation, it covers initial selection of
    an existing group, creation of a new valid group, an explicit whole-suite
    answer never asked again, `write-requirement` asking only when no choice
    was recorded, activation after the effort started, switching groups and
    deactivation (with `GHOG_GROUP` unable to override the workflow choice), a
    stale draft not overriding a changed or removed requirement selection, a
    shared group entry surviving deactivation, a same-name definition change
    recognized as a scope change, a published round and a detached run keeping
    their bound scope, a replacement request carrying new-scope validation and
    the disclosure of the change, a commit-ready answer never admitting an
    unreviewed scope change as polishing, exact-scope proof reuse, and
    `pw progress` showing the declared scope, its source and any pending
    change. `GROUNDHOG.md` and the workflow documentation show how to choose,
    change and remove an effort's group, and how that differs from manual
    `--group` or `GHOG_GROUP` selection.

## Closing instructions for the LLM by level

The last lines of a walk are the instruction an LLM acts on. For each level
and outcome, the report must carry the following instruction; `<level>`
stands for the level of the walk, and the wording itself is left to the
design.

Every command example in this table also carries the resolved scope required
by gap 19: the selected group or the explicit whole-suite selector. Commands
that request or restart a level preserve that same scope.

| Level | Outcome | Required closing instruction |
| --- | --- | --- |
| default | green | The full suite was skipped on purpose (no level requested); the walk objective (check.bat and the affected tests) is met; do not run the full suite unless the calling instruction asks for a level; to ask for one, run `ghog day --full=pass`, `ghog day --full=cov`, or `ghog day --full=speed`; carry on with the calling instruction. |
| default | check or affected failure, including its crash diagnostics | Today's fix instruction, then, when the existing recovery rules permit a restart, restart with plain `ghog day`. |
| `pass` | green | Objective met at `pass` for the selected scope (named: the whole suite or the group): every test of that scope passes; coverage and duration gates are not required by the requested `pass` objective; carry on with the calling instruction. |
| `cov` | green | Objective met at `cov` for the selected scope (named): every test of that scope passes and the coverage gate over that scope's sources is met; the duration gate is not required by the requested `cov` objective; carry on with the calling instruction. |
| `speed` | green | Objective met at `speed` for the selected scope (named): every test of that scope passes, the coverage gate over that scope's sources is met, and no unaccepted duration outlier remains under the configured exclusions; carry on with the calling instruction. |
| `pass`, `cov`, `speed` | check or affected failure | Today's fix instruction, then restart with `ghog day --full=<level>`. |
| `pass`, `cov`, `speed` | full-suite failure | `ghog single <failing test files>` until green, then restart with `ghog day --full=<level>`. |
| `pass`, `cov`, `speed` | suite crash | Act on the crash block, then restart with `ghog day --full=<level>`. |
| `pass` | coverage gap or duration outliers | Not judged: no coverage or slow-test request. |
| `cov`, `speed` | coverage gap | covg on the missing rows, add tests, `ghog affected` to the gate, `ghog check`, then restart with `ghog day --full=<level>`. |
| `cov` | duration outliers | Not judged: no slow-test request. |
| `speed` | duration outliers | Attempt to shorten the flagged calls through `fix_slow_test.md`; accept a genuinely slow call with `ghog exclude` only after the attempted improvement and with the evidence required by Q07; then restart with `ghog day --full=speed`. |

A default walk has no full-suite outcome. It never restarts with an invented
level such as `--full=default` or `--full=none`. Existing setup-error,
interruption and other operational stop rules still apply at every level: the
table never turns a stop into an automatic retry.

Rows marked "Not judged" describe observations outside the selected
objective; they are not failure outcomes. If no enforced failure remains, the
walk emits the requested level's green closing instruction and the calling
workflow continues. Otherwise it emits the applicable enforced-failure
instruction.

A noop walk states that the requested objective is met by valid saved
evidence, identifies the level that evidence achieved, and states that no
checks ran in this invocation (Q08). It never claims that a stronger saved
proof lacks coverage or speed merely because the current request is weaker.

For direct `ghog full` calls, the full-suite outcome instructions apply for
the resolved level as well, limited to the objective the run actually
established (gap 9); any suggested day-walk restart preserves that level and
the resolved scope (gap 19).

## Code references for full suite levels

- `tools/groundhog/day.py`: `run_day`, the three-step walk and the snapshot
  noop check.
- `tools/groundhog/runner.py`: `pytest_command`, the pytest command line of
  each subcommand, where a group narrows the collected test files.
- `tools/groundhog/gate.py`: the coverage gate read from the project
  configuration, which a group narrows to its declared sources.
- `tools/groundhog/commands.py`: `run_tests` verdicts, exit 3 and exit 8
  judgement, and next-step lines.
- `tools/groundhog/snapshot.py`: `a.ghog.day.ok` marker, `is_unchanged` and
  `write_marker`.
- `tools/groundhog/parser.py`: subcommand options, where the level
  parameter is parsed.
- `tools/groundhog/reporting_nextstep.py`: next-step messages per run state.
- `tools/code_review_validation.py`: `DEFAULT_PROJECT_VALIDATION_COMMANDS`,
  the requestor's mandatory `ghog day` default.
- `tools/prepare_release/prepare_release_plan_workflow.py`: the `run ghog day`
  operations of the integration sync and the feature `--onto` replay.
- `instructions/implement-step.md`, `instructions/implement-missing-step.md`,
  `instructions/split-large-file.md`, `instructions/write-plans.md`: the
  development walks.
- `instructions/groundhog.md`, `instructions/fix_slow_test.md`: the fixing
  loop and the slow-test fix.
- `instructions/code-review-requestor.md`: validation set before publishing,
  commit-ready convergence, and human gate.
- `instructions/prepare-release.md`: the green-gate routine.
- `GROUNDHOG.md`, `tools/Pytest reset specs.md`: the groundhog manual and
  specification.

## Requirement clarifications for full suite levels

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | `pass` runs every test of the selected scope (whole suite or group) and requires it to pass without a crash, with no coverage collection and no duration enforcement; durations are informational. It proves what the default walk cannot: no test in the selected scope outside the affected set fails. | Gap 3; closing instructions (`pass` rows) | Skip the suite entirely at `pass` (the default walk under another name); collect coverage without enforcing it (costs time for a figure nobody acts on). |
| Q02 | One precedence rule for `ghog day` and direct `ghog full`: `--full`, then `GHOG_FULL`, then the command default (no full step, or `speed`). Development walks pick `GHOG_FULL` up. | Gaps 2 and 9 | `GHOG_FULL` for `ghog day` only (two rules to remember); variable for humans only with explicit levels in every skill (needs a "none" value and removes the human knob). |
| Q03 | A level upgrade on unchanged sources reuses the successful check and affected results of the same validated snapshot, runs only the missing full-suite objective, and names the reused results. | Gap 7 | Re-run all three steps on every upgrade (pays check and affected twice at review and release time). |
| Q04 | Superseded on 2026-09-30: `speed` now runs before review, so every speed change is reviewed and no test-only exception exists (gap 16). The earlier decision required positive evidence that every changed file serves tests exclusively. | Gap 16 | Collection root or file-name classifier; requestor judgement. |
| Q05 | Superseded on 2026-09-30: no speed work happens at the commit-ready answer (gap 16); repairs happen before publication and are reviewed. The earlier decision classified every post-review repair delta with the test-only boundary. | Gaps 12 and 16 | Always start a round for non-speed failures; escalate to the human. |
| Q06 | Superseded on 2026-09-30: no round is started from convergence by the requestor (gap 16). The earlier decision started an ordinary replacement round for a production speed repair made after review. | Gap 16 | A dedicated speed-review round limited to the diff. |
| Q07 | Revised on 2026-09-30: a duration exclusion is allowed during the requestor's `speed` validation, after an attempted improvement, and the review request names the call, measured time, attempt and reason so the reviewer judges it; it covers duration acceptance only. | Gap 14; closing instructions (`speed` outliers row) | Only a human may exclude (blocks validation on every slow call); exclusion accepted without being shown to the reviewer. |
| Q08 | Every walk reports the selected objective and its source, the strongest valid saved proof, and which steps ran or were reused; detached walks keep their level; consumer compatibility is verified. | Gaps 1 and 5; closing instructions (noop paragraph) | Keep the closing line unchanged (cannot tell the default walk from `pass`, nor a noop from a fresh run). |
| Q09 | Reopened on 2026-09-30 as Q13: with review mode disabled, where the `speed` pass runs. The earlier decision ran it before the ordinary human commit gate, with test-only changes joining the commit. | Gap 15 | No speed pass without review mode; `speed` at prepare-release instead. |
| Q10 | A saved result that cannot establish its level satisfies no requested level; the first requested walk after the upgrade revalidates its selected objective. | Gap 8 | Treat a positively identified legacy green snapshot as `speed` (needs a compatibility guarantee that every legacy snapshot came from an all-gates walk). |
| Q11 | Under the default validation policy, every code-review request (round 1 and each replacement round) is published after a green `speed` walk, which may reuse valid saved proof; with no walk at the commit-ready answer, the last request carries the final `speed` proof. | Gap 12 | Round 1 at `speed` and replacement rounds at `cov` (a speed regression introduced during review reaches the commit unnoticed); replacement rounds on the default walk (neither coverage nor speed proven for review-round changes). |
| Q12 | Withdrawn on 2026-09-30: the human dropped the `speed` recheck at the commit-ready answer, so the question of a failing recheck no longer exists. | Gap 16 | A recheck shown at the human gate with a rework recommendation; a requestor repair and automatic new round; a gate offering only rework. |
| Q13 | Only with review mode disabled: the `speed` pass runs between implementation-check and the commit menu; any change it makes goes back through implementation-check, then a green `speed` pass (possibly by snapshot reuse), with no test-only exemption and no review exchange. | Gap 15 | `speed` at the end of implement-step (speed work back in the development loop); no `speed` pass without review mode (speed never judged there). |
| Q14 | A declared `.review-validation` set keeps authority; a `ghog day` without `--full` in it triggers a migration notice on every request; the workflow supplies no additional `speed` validation, so a set that establishes no `speed` reaches commit without that proof. | Gaps 12 and 16 | Always adding `ghog day --full=speed` on top of a declaration (overrides project policy); reading plain `ghog day` as `--full=speed` in a declaration (same command, two meanings). |
| Q15 | With a group, the affected step runs only the testmon-selected tests inside the group, including the `ghog affected` checks of implementation-check and the reviewer; an empty affected selection on a valid group is a normal no-work step. | Gaps 20 and 21 | Whole-suite affected selection with only the full step narrowed (runs outside tests at every walk); outside failures as non-blocking warnings (easy to ignore). |
| Q16 | An effort declares its group with a `Test group: <name>` line in its feature request or issue; `pw` carries the scope in every workflow-owned ghog command; declared `.review-validation` commands stay unchanged (Q14). | Gaps 19 and 21 | `GHOG_GROUP` set by hand for the effort (lost in new shells, invisible to review); group inferred from the effort slug (couples naming to layout). |
| Q17 | Group patterns are gitignore-style globs on normalized repository-relative paths; the sentinel example reads `**/tests/**/*sentinel*/**`. | Gap 18 | Python regular expressions (hard to read, easy to get wrong); both syntaxes with a prefix (two languages to maintain). |
| Q18 | A proof is valid only for the exact scope it was earned on: same group name, patterns and effective membership, or the whole suite, under the same gate configuration and timing floor; changes invalidate it. | Gaps 20 and 23 | Whole-suite proof accepted for a group at `pass` (special case for a rare request); whole-suite proof accepted for any group request (can hide missing group coverage). |
| Q19 | Group runs judge durations against the saved whole-suite floor, or the one-second fallback, and never rewrite it; no automatic whole-suite `speed` run seeds the floor. | Gap 23 | One floor per group (lenient standards per group); group runs rewriting the shared floor (floor depends on the last scope run). |
| Q20 | An explicit whole-suite selector wins over `GHOG_GROUP`, even an invalid one; prepare-release, ungrouped efforts, whole-suite restarts and detached runs use it. | Gaps 19 and 21 | Wrappers clearing `GHOG_GROUP` (standalone restarts and new shells inherit the group again); environment decides even for release (breaks the whole-suite release gate). |
| Q21 | A selected group whose patterns resolve to no test file or no source file is a setup error (exit 5) naming the empty side. | Gaps 18 and 19 | Empty group as a green success (vacuous proof); silent fallback to the whole suite (scope and cost change unnoticed). |

## Open questions for the v0.13.0 full suite levels feature request (group activation)

### Q22: When an effort is asked about its group, and how the entry is created

Question description: Q16 settled that the requirement's `Test group:` line drives workflow scope. Nothing says when the author is asked, nor who creates or checks the group file entry. An effort whose author never thinks of it silently runs the whole suite. Which document controls scope once a requirement exists, and how a deliberate whole-suite answer is remembered, is Q26.

#### BBQ for Q22

A catering order can say "pastry only". The customer can be asked when the order is first taken, when it is written up in detail, or never, leaving it to whoever remembers to add a note later.

In this picture: the order first taken is the draft (`process-draft`), the detailed write-up is the requirement (`write-requirement`), the note is the recorded scope choice, and the kitchen's list of what "pastry" covers is the group file entry.

#### Options for Q22

- Option A: `process-draft` asks for the effort's scope (an existing group, a new group, or the whole suite) and records the answer; `write-requirement` carries it into the requirement and asks only when no answer was recorded. An existing group's entry is validated and reused; a new group's test and source patterns are obtained and a valid entry is created before the first grouped walk. An unknown, unreadable or empty group keeps Q21's setup failure.
  - pro: the question is asked once, at the start, when the author knows the effort's scope;
  - pro: the entry exists and resolves before the first walk needs it.
  - con: two skills change.
- Option B: only `write-requirement` asks and creates the entry.
  - pro: one skill changes.
  - con: the draft cannot state the intended scope.
- Option C: no prompt; the author adds the line and the entry by hand.
  - pro: no workflow change.
  - con: easy to forget, and a missing entry only shows as an exit 5 at the first walk.

#### Recommended option for Q22 (with arguments for this choice)

Option A: the scope of an effort is known when the draft is processed; asking there, validating or creating the entry at once, and carrying the answer forward makes the scope a deliberate choice.

#### Answer to Q22: option A (with reason why it must be accepted as the answer)

Option A: the effort's scope is asked once when the draft is processed, carried into the requirement, and backed by a valid group entry before the first grouped walk.

### Q23: Turning a group on, switching it, or turning it off mid-effort

Question description: an effort may start without a group and later need one, or switch or drop it. `GHOG_GROUP` cannot do it for workflow walks (Q20). A group entry is shared: other efforts may select the same name, so changing an effort's selection must not change or delete the entry, and changing the entry itself is a different kind of scope change.

#### BBQ for Q23

Halfway through the catering order, the customer decides only the pastry needs a tasting. The kitchen can accept a note on this order at any time, require the whole order to be re-approved, or refuse any change once cooking started. Crossing "pastry" off the kitchen's shared list to stop this order's tasting would also stop every other order's.

In this picture: the note on this order is the requirement's `Test group:` line, re-approval is reopening the requirement's review, "cooking started" is the first implemented step, and the kitchen's shared list is the group file.

#### Options for Q23

- Option A: activation adds the group name to the requirement, switching replaces it, deactivation removes it, at any point of the effort and without reopening the requirement's review; none of these deletes or overwrites a group entry. Changing a group's patterns is a separate edit of the shared entry, and counts as a scope change for every effort selecting it. A change takes effect at the next eligible workflow boundary (Q24). No proof from a different scope is reused; a destination scope may reuse its own still-valid proof under Q18.
  - pro: the scope follows the effort's needs without a review cycle for a one-line change;
  - pro: shared entries are never damaged by one effort's choice, and the existing proof rules keep the switch safe.
  - con: a reviewed requirement can change its test scope without a review of that change (Q24 keeps an active code review informed).
- Option B: any change of the selection reopens the requirement's review.
  - pro: every scope change is reviewed.
  - con: a full review cycle for a one-line change, in the middle of implementation.
- Option C: the selection can only change before the first plan step is implemented.
  - pro: every step of the effort shares one scope.
  - con: an effort that discovers its scope late cannot adopt a group.

#### Recommended option for Q23 (with arguments for this choice)

Option A: the selection changes which tests run, not what the effort delivers; separating it from the shared definition protects other efforts, and Q18 already decides which proof stays valid.

#### Answer to Q23: option A (with reason why it must be accepted as the answer)

Option A: an effort turns its group on, switches it or turns it off by editing its requirement's `Test group:` line, never by editing or deleting the shared entry, with no proof carried across scopes.

### Q24: A scope change while a code review is active

Question description: a scope change can happen between two rounds, while a request or an answer is pending, or just before a commit-ready answer, where no replacement request follows. A published round was validated and reviewed on its scope; its evidence must keep that meaning. A walk already started, detached included, runs on its invocation scope. A scope change also includes a changed definition under the same group name.

#### BBQ for Q24

The taster is tasting today's plate, checked against the full menu. The chef decides, mid-tasting, that from now on plates are checked against the pastry list only. Today's plate stays checked against the full menu; the next plate follows the new rule and says so; and a plate already approved cannot pick up the new rule on its way out of the kitchen.

In this picture: the taster is the reviewer, today's plate is the published round, the next plate is the replacement request, the approved plate is a commit-ready answer, and the rule change is the scope change.

#### Options for Q24

- Option A: the change waits for the next eligible boundary. A published round keeps its validation scope, reviewer affected commands and evidence; a started walk keeps its scope. A replacement request resolves the new scope, satisfies the applicable validation on it (by default a green `speed` walk; a declared `.review-validation` set stays authoritative, Q14), and states the previous scope, the new scope and the reason. At a commit-ready answer, a pending scope change is never treated as polishing and never reuses the old round's proof: the gate evidence names it, and if deferred until after the commit, the pending selection or definition edits stay outside the approved commit, whose reviewed scope remains unchanged; otherwise the human uses the existing `Rework and review again` choice so a replacement round validates it. A pending change is the difference between the effort's currently resolved scope (the requirement selection and the selected group's patterns and effective membership) and the scope bound to the active round. No new exchange operation and no automatic transition out of convergence.
  - pro: every round's evidence keeps its meaning, and the reviewer sees each change;
  - pro: uses only existing rounds and the existing human gate.
  - con: a change made during a round takes effect one round later.
- Option B: a scope change is refused while a code-review exchange is active.
  - pro: every exchange has one scope.
  - con: blocks a legitimate change until a possibly long review ends.
- Option C: a scope change restarts the exchange from round 1.
  - pro: clean evidence per exchange.
  - con: discards review progress for a change in test selection.

#### Recommended option for Q24 (with arguments for this choice)

Option A: binding each round to its scope and moving changes to the next boundary keeps evidence honest without blocking or restarting reviews, and the existing human gate covers the commit-ready case.

#### Answer to Q24: option A (with reason why it must be accepted as the answer)

Option A: a scope change never alters a published round or a started walk; the next replacement request validates and discloses it, and at a commit-ready answer it waits or goes through the human's rework choice.

### Q25: Where the effort's scope is shown

Question description: the scope decides which tests every workflow walk runs, yet a user or an agent can only find it by reading the requirement and the group file. With Q24, the declared scope can also differ from the scope bound to an active review round.

#### BBQ for Q25

The catering order's "pastry only" note is on page three. The kitchen can also write it on the board every cook reads at the start of the shift, including "changing to pastry after this tasting", or on every ticket too.

In this picture: page three is the requirement's line, the board is `pw progress`, the pending note is a scope change waiting for its boundary, and every ticket is every handoff prompt.

#### Options for Q25

- Option A: `pw progress` shows the effort's declared scope (group name or whole suite) and the document it comes from; when an active round is bound to another scope, it shows both, marking the declared one as pending. The ghog reports keep showing the actual run scope. The declared effort scope alone never implies group proof; the request reports what the custom validation commands actually established, and claims group proof only when their evidence establishes that exact scope and level.
  - pro: visible at the decision point, before any walk runs;
  - pro: makes a pending change or an unexpected scope obvious.
  - con: one or two more lines in the progress report.
- Option B: the scope appears only in the ghog closing lines and `ghog status`.
  - pro: no `pw` change.
  - con: only visible after a walk ran.
- Option C: both `pw progress` and every handoff prompt name the scope.
  - pro: impossible to miss.
  - con: repeats the same line in every prompt.

#### Recommended option for Q25 (with arguments for this choice)

Option A: `pw progress` is where a user or agent looks before the next step; showing the declared scope, its source and any pending change there makes the scope known before it matters.

#### Answer to Q25: option A (with reason why it must be accepted as the answer)

Option A: `pw progress` names the declared scope, its source and any pending change, while the ghog reports keep naming the scope each run actually used.

### Q26: Remembering a whole-suite answer, and which document controls scope

Question description: an absent `Test group:` line means the whole suite (Q16, Q20), but during authoring it cannot tell a deliberate whole-suite answer from an author who was never asked. Q22 also records the answer in the draft first; once the requirement exists, a stale draft must not bring back a group the requirement removed.

#### BBQ for Q26

The order form has an empty "tasting" box. It may mean "taste the whole menu" or "nobody asked". And once the kitchen copy of the order exists, the customer's first scribbled note must not override later changes to the kitchen copy.

In this picture: the empty box is an absent `Test group:` line, the customer's first note is the draft, the kitchen copy is the requirement, and "taste the whole menu" is an explicit whole-suite answer.

#### Options for Q26

- Option A: authoring records an explicit choice, a named group or the whole suite, and asks only while no choice is recorded. Once the requirement exists, it alone controls workflow scope; its absent `Test group:` line still means the whole suite. The draft is an input to requirement creation, never a fallback, and regenerating from it never overwrites a later requirement selection.
  - pro: no repeated question, one runtime authority, and a deactivation survives a stale draft;
  - pro: the runtime meaning of an absent line does not change.
  - con: authoring must distinguish "unanswered" from "whole suite".
- Option B: absence always means the whole suite, and `write-requirement` never asks when the draft has no line.
  - pro: no extra state.
  - con: an effort never asked is never asked.
- Option C: absence means unanswered at every authoring stage, and the draft stays a fallback.
  - pro: little explicit state.
  - con: asks a settled question again, and can resurrect a group removed from the requirement.

#### Recommended option for Q26 (with arguments for this choice)

Option A: a deliberate answer must be remembered as such, and one document must control the effort once it exists; how the choice is encoded is left to the design, without inventing a group named "none".

#### Answer to Q26: option A (with reason why it must be accepted as the answer)

Option A: the authoring workflow remembers an explicit whole-suite or group answer, and from the requirement onward only the requirement controls the effort's scope.
