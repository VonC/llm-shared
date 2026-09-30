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
    and its source file patterns, matched against normalized
    repository-relative paths (Q17). A selected group is valid only when its
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
    `GHOG_GROUP` cannot narrow it. The effort declares its group in its
    documents so workflow walks pass it (Q16).
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
24. Documentation and tests: `GROUNDHOG.md`, `tools/Pytest reset specs.md`
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
    timing floor unchanged.

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

## Open questions for the v0.13.0 full suite levels feature request (test groups)

### Q15: Which tests the affected step runs when a group is selected

Question description: gap 20 narrows the full-suite step to the group's tests. Before it, the walk runs `ghog affected --no-cov`, which lets testmon select every test whose covered code changed, across the whole suite. The human asked that a group effort run only the group's tests, not the rest. The question is whether that also applies to the affected step, which is cheap and could catch a breakage outside the group early.

#### BBQ for Q15

The pastry team only bakes its own menu this week. The quick morning check tastes every dish whose recipe changed. It can taste only the pastry dishes, or every changed dish in the kitchen, which costs a few bites and may catch a sauce the pastry change spoiled.

In this picture: the pastry menu is the group, the quick morning check is the affected step, a changed recipe is testmon's selection, and the spoiled sauce is a test outside the group broken by the effort.

#### Options for Q15

- Option A: with a group, the affected step runs only the testmon-selected tests that match the group's test patterns.
  - pro: follows the request literally: a group effort runs only its own tests;
  - pro: fully predictable run time during development.
  - con: a breakage outside the group waits for prepare-release even when testmon already knows which outside test it hits.
- Option B: the affected step keeps testmon's whole-suite selection; only the full-suite step is narrowed to the group.
  - pro: breakages outside the group are caught early, at the cost of the few outside tests testmon selects;
  - pro: the group narrows only the expensive step.
  - con: an effort touching shared code may run many outside tests at every walk.
- Option C: run the whole selection, but report failures outside the group as warnings that do not fail the walk.
  - pro: early signal without blocking the effort.
  - con: a warning that never blocks is easy to ignore until prepare-release.

#### Recommended option for Q15 (with arguments for this choice)

Option A: the human asked for a group effort to run only its tests, and gap 22 already accepts that outside breakages surface at prepare-release; option B remains the fallback if that trade-off proves too costly.

#### Answer to Q15: option A (with reason why it must be accepted as the answer)

Option A: a group walk runs only the group's tests in every step, which keeps its cost predictable and matches the accepted trade-off of gap 22. The same rule governs the group-selected `ghog affected` checks run by implementation-check and by the reviewer, whose permitted commands do not change. A valid group whose affected selection is empty is a normal no-work step, distinct from an invalid empty group (Q21).

### Q16: Where an effort declares its group

Question description: gap 19 says the effort declares its group so workflow walks pass it along. Development walks, the requestor's validation and the review-off pass are driven by instructions and `pw`, which need to find the group without the human typing it at every walk.

#### BBQ for Q16

The pastry team's orders must say "pastry only" so every cook applies it. The note can be written on the order itself, pinned on the kitchen door for the week, or inferred from the order's title.

In this picture: the order is the effort's documents, the note on the order is a group line in them, the door pin is `GHOG_GROUP` set in the shell, and the title is the effort slug.

#### Options for Q16

- Option A: the effort's feature request (or issue) carries a `Test group: <name>` line; `pw` reads it and every workflow-owned ghog validation command it prints carries the effort's resolved scope; project-declared `.review-validation` commands remain unchanged under Q14.
  - pro: versioned with the effort, visible in review, and the same for every session;
  - pro: an effort without the line runs the whole suite through the explicit whole-suite selector (Q20), as before.
  - con: `pw` and the instructions must carry the group through every printed command.
- Option B: the human sets `GHOG_GROUP` in the shell for the duration of the effort.
  - pro: no document or tool change.
  - con: lost in every new session or tool shell, and invisible to the reviewer.
- Option C: the group name is the effort slug when a group of that name is declared.
  - pro: no extra declaration.
  - con: couples naming to test layout, and several efforts cannot share one group.

#### Recommended option for Q16 (with arguments for this choice)

Option A: the group is a property of the effort, so it belongs in the effort's own versioned documents, where review sees it and every session finds it.

#### Answer to Q16: option A (with reason why it must be accepted as the answer)

Option A: a `Test group:` line in the effort's requirement, read by `pw`, makes every workflow-owned walk of the effort run its group without relying on shell state; a project's declared `.review-validation` commands keep their authority (Q14) and are never given selectors.

### Q17: Pattern syntax for group test and source files

Question description: the human's example, `**/tests/**/.*sentinel.*/**`, mixes glob (`**`) and regular-expression (`.*`) notation. The declaration needs one syntax for test and source patterns.

#### BBQ for Q17

The pastry team writes "every tray in any cold room whose label says pastry". The warehouse can read labels with its usual wildcards, or with a precise pattern language only some staff know.

In this picture: trays are files, cold rooms are `tests` folders, the usual wildcards are gitignore-style globs, and the precise pattern language is regular expressions.

#### Options for Q17

- Option A: gitignore-style globs matched against normalized repository-relative paths, where the example becomes `**/tests/**/*sentinel*/**`.
  - pro: the syntax contributors already use for Git and most tooling;
  - pro: easy to read, and the same for test and source patterns.
  - con: less expressive than a regular expression.
- Option B: Python regular expressions matched against repository-relative paths.
  - pro: fully expressive.
  - con: easy to get wrong (escaping dots and slashes), hard to read in review.
- Option C: accept both, with a prefix marking regular expressions.
  - pro: flexible.
  - con: two syntaxes to document, test and read.

#### Recommended option for Q17 (with arguments for this choice)

Option A: globs cover the stated need (a folder name containing `sentinel` anywhere under `tests`), read naturally in review, and match how paths are declared elsewhere in the repository.

#### Answer to Q17: option A (with reason why it must be accepted as the answer)

Option A: group patterns use gitignore-style globs, so the sentinel example reads `**/tests/**/*sentinel*/**` and its sources, for example, `tools/sentinel/**`.

### Q18: Whether a proof for one scope satisfies another

Question description: gap 23 records proof per scope (a group or the whole suite). A green whole-suite `cov` walk runs every test and covers every source, but its coverage of the group's sources may come from tests outside the group, while a group gate requires coverage by the group's own tests. A group proof, in turn, says nothing about tests outside the group.

#### BBQ for Q18

A full restaurant inspection passed yesterday. Today the pastry corner asks for its own certificate, which requires that the pastry staff alone keep their corner clean. Yesterday's certificate saw a clean corner, but maybe the main kitchen staff cleaned it.

In this picture: the full inspection is a whole-suite proof, the pastry certificate is a group proof, the pastry staff are the group's tests, and the main kitchen staff are tests outside the group.

#### Options for Q18

- Option A: proofs never cross scopes: a group request needs a group proof, a whole-suite request a whole-suite proof.
  - pro: each proof means exactly what its gate checked;
  - pro: simple to state and to test.
  - con: a whole-suite walk right after a group walk re-runs the group's tests.
- Option B: a whole-suite proof satisfies a group request at `pass` only (every group test passed in it), never at `cov` or `speed`.
  - pro: saves a group `pass` walk after a whole-suite walk.
  - con: a special case for a level the workflow rarely requests.
- Option C: a whole-suite proof satisfies any group request.
  - pro: fewest walks.
  - con: can accept group coverage that the group's own tests do not provide.

#### Recommended option for Q18 (with arguments for this choice)

Option A: a group gate and a whole-suite gate check different things, so neither proof should stand in for the other; the rare extra walk is cheaper than an ambiguous proof.

#### Answer to Q18: option A (with reason why it must be accepted as the answer)

Option A: a proof is valid only for the exact scope it was earned on, meaning the same group name with the same test patterns, source patterns and effective file membership (or the whole suite), under the same gate configuration; changing a group's patterns or membership invalidates its proof, which keeps every noop and reuse decision exact.

### Q19: Which timing floor group runs judge against

Question description: the `speed` verdict flags calls far above a floor derived from the suite's median call time (the auto floor, rewritten by timing runs in `a.ghog.outliers`), with a one-second minimum. A group's calls can have a very different median from the whole suite, so a group run that recomputes and saves the floor would shift the floor the whole suite is judged against, and the reverse.

#### BBQ for Q19

The bakery sets its "too slow" line from the median bake time of the whole menu. The pastry team times only its own items this week. If it resets the line from pastry alone, the bread is judged against a pastry line next week; if it uses the bakery line, a slow pastry is judged against bread.

In this picture: the "too slow" line is the auto floor, the whole menu is the whole suite, the pastry items are the group's tests, and resetting the line is rewriting the floor in `a.ghog.outliers`.

#### Options for Q19

- Option A: a group run judges its calls against the saved whole-suite floor (or the one-second default when none exists) and never rewrites it; only whole-suite `speed` runs update the floor.
  - pro: one floor for the project, and group runs cannot distort it;
  - pro: a slow group call is judged by the project-wide standard.
  - con: a group run in a fresh project has only the one-second default until a whole-suite `speed` run happens.
- Option B: each group keeps its own floor, computed and saved from its own runs.
  - pro: each group is judged against its own typical call time.
  - con: several floors to store and explain, and a slow group sets itself a lenient standard.
- Option C: group runs recompute and save the shared floor, as today's runs do.
  - pro: no change.
  - con: the floor then depends on which scope ran last.

#### Recommended option for Q19 (with arguments for this choice)

Option A: the floor is a project-wide standard for "far outside the norm"; letting a narrower scope rewrite it, or keep its own, would make the `speed` verdict depend on scope rather than on the call.

#### Answer to Q19: option A (with reason why it must be accepted as the answer)

Option A: group runs are judged against the project's saved floor without changing it, so the `speed` standard stays the same for every scope. A project working only through groups and the `cov` release gate may never set a whole-suite floor; group runs then use the one-second fallback, and no automatic whole-suite `speed` run is added to compensate.

### Q20: How the whole suite is selected explicitly

Question description: a group comes from `--group` or `GHOG_GROUP`, and absence of both means the whole suite. Absence cannot protect a whole-suite command from an ambient `GHOG_GROUP`: prepare-release, an effort that declares no group, and a whole-suite restart line would all be narrowed by a variable left in the shell.

#### BBQ for Q20

The pastry team hangs a "pastry only" sign on the kitchen door for the week. The annual inspection must cover the whole kitchen whatever sign hangs on the door; saying nothing about scope lets the sign decide.

In this picture: the door sign is `GHOG_GROUP`, the annual inspection is the prepare-release gate, and saying "whole kitchen" out loud is the explicit whole-suite selector.

#### Options for Q20

- Option A: an explicit whole-suite selector that overrides `GHOG_GROUP`, used by prepare-release, by efforts with no declared group, and in whole-suite restart lines and detached runs.
  - pro: one reproducible scope choice carried through commands, repair lines and detached runs;
  - pro: an ambient group can never narrow a release gate.
  - con: one more selector value to document.
- Option B: workflow wrappers clear `GHOG_GROUP` before whole-suite commands.
  - pro: no new selector.
  - con: standalone restart commands and new shells can inherit the group again.
- Option C: let the environment decide, even for release.
  - pro: simplest.
  - con: breaks the settled whole-suite release gate.

#### Recommended option for Q20 (with arguments for this choice)

Option A: only an explicit selector makes the whole-suite scope as reproducible as a group scope; its exact spelling belongs to the design.

#### Answer to Q20: option A (with reason why it must be accepted as the answer)

Option A: an explicit whole-suite selector, winning over `GHOG_GROUP` even when the variable is invalid, guarantees that prepare-release and ungrouped efforts always run everything.

### Q21: What happens when a group resolves to no files

Question description: a declaration can be readable yet contain a misspelled pattern that matches no test file or no source file. Such a group could produce an empty green run or a vacuous 100% coverage over zero sources.

#### BBQ for Q21

The pastry team's list names a tray that does not exist. The inspector can refuse the list, sign it because nothing on it was dirty, or quietly inspect the whole kitchen instead.

In this picture: the list is the group declaration, the missing tray is a pattern matching no file, signing is an empty green result, and inspecting the whole kitchen is a silent whole-suite fallback.

#### Options for Q21

- Option A: a selected group whose patterns resolve to no test file or no source file is a setup error (exit 5).
  - pro: a typo can never produce an empty success or a vacuous coverage proof;
  - pro: the failure names the empty side, so the fix is obvious.
  - con: declarations must be kept current as files move.
- Option B: accept it as a successful empty group.
  - pro: allows placeholder groups.
  - con: green no longer means the requested tests and sources were checked.
- Option C: fall back to the whole suite.
  - pro: tests still run.
  - con: silently changes scope and cost.

#### Recommended option for Q21 (with arguments for this choice)

Option A: a group exists to prove something about specific tests and sources; if it resolves to nothing, there is nothing to prove, and saying so is the only honest outcome. A valid group whose testmon affected selection is empty is a different case: a normal no-work step.

#### Answer to Q21: option A (with reason why it must be accepted as the answer)

Option A: an empty group is rejected with exit 5 naming the empty side, while an empty affected selection on a valid group stays a normal no-work step.
