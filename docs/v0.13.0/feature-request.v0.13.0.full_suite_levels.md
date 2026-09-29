# Full suite levels for the ghog day walk

- Draft: docs/v0.13.0/draft.v0.13.0.full_suite_levels.md

## CDC revision that introduces full suite levels

Until v0.12.0, the groundhog objective was a single one: every `ghog day` walk
runs check.bat, then `ghog affected --no-cov`, then `ghog full`, and is green
only when the full suite passes, meets the coverage gate, and shows no
duration outlier. Every development skill closes its work with that walk.

The revision keeps that objective for the final phases only. During
development, the walk stops after the affected tests. The full suite runs on
demand, at one of three levels chosen by the caller:

| Level | The full run fails on | The full run ignores |
| --- | --- | --- |
| `pass` | test failures (exit 2), suite crash (exit 4) | coverage gap (exit 3), duration outliers (exit 8) |
| `cov` | exits 2 and 4, coverage gap (exit 3) | duration outliers (exit 8) |
| `speed` | exits 2, 4, 3 and duration outliers (exit 8) | nothing (today's behavior) |

The code-review requestor and the prepare-release green gate ask for `cov`.
The code-review requestor also runs one `speed` walk when a review round
converges on a commit-ready answer, and that walk decides between another
review round and the human commit gate.

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
3. Level verdicts: at `pass`, the whole suite runs and must pass without a
   suite crash; it runs without coverage collection or duration enforcement,
   and any recorded durations are informational (Q01). At `cov`, duration
   outliers do not fail the run. At `speed`, the run keeps today's verdicts.
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
   direct call behaves as today.
10. Development skills use the default walk: `implement-step.md`,
    `implement-missing-step.md`, `split-large-file.md`, and the plan command
    written by `write-plans.md` use `ghog day` with no level. Their wording no
    longer promises a full coverage pass.
11. The groundhog loop keeps the caller's level: `groundhog.md` restarts every
    fix with the same level the loop was started with, so a fix never raises
    or drops the objective. `fix_slow_test.md` applies only to a `speed` walk
    and restarts it at `speed`.
12. Requestor validation at `cov`: the code-review requestor project default
    becomes the `cov` walk (`DEFAULT_PROJECT_VALIDATION_COMMANDS` in
    `tools/code_review_validation.py`), run green before any request is
    published.
13. Prepare-release green gate at `cov`: the green-gate routine in
    `prepare-release.md` and both `run ghog day` operations in
    `prepare_release_plan_workflow.py` name the `cov` walk.
14. Test-only boundary (Q04): a change qualifies as test-only only when every
    changed file is established to serve tests exclusively. Shared runtime
    code, configuration or tooling that can affect production behavior, and
    any file whose exclusive test use cannot be established, require another
    review. Path names and collection roots alone are insufficient evidence.
    How test-only use is established is left to the design.
15. Duration-exclusion exception (Q07): accepting a genuinely slow call with
    `ghog exclude` is a separate, narrow exception to gap 14, allowed only
    after an attempted improvement. The gate evidence names the excluded
    call, its measured time, the attempted improvement, and the reason for
    accepting the duration. The exception covers duration acceptance only,
    never unrelated configuration changes or the removal of correctness or
    coverage checks.
16. Requestor speed pass at convergence: when the requestor receives a
    commit-ready answer, it runs one `speed` walk before the human gate, then
    loops on it until exit 0. For repairable test, coverage, crash, or
    duration failures, it restores the `speed` objective, preserves test
    coverage and assertions, and classifies the complete repair delta with
    gaps 14 and 15, whatever failure triggered the repair (Q05). Existing
    operational stop and interruption rules still apply: this never
    authorizes weakening checks to reach exit 0, or retrying a setup error
    without end.
    - if a green `speed` walk needed no change, or only changes within the
      test-only boundary or a duration exclusion, the requestor stages those
      changes, amends `a.commit` when its groups no longer match, accepts the
      commit-ready answer, and presents the human gate (`Commit` or
      `Rework and review again`) with those changes listed in its evidence;
    - if any repair falls outside both the test-only boundary and the
      duration-exclusion exception, the requestor starts an ordinary
      replacement round for the same step, whose change summary and writer
      response name that change (Q06), instead of presenting the human gate.
      This extends the current rule that the requestor cannot start a new
      round from convergence, for this case only. At the next commit-ready
      answer, the `speed` validation is repeated, reusing an unchanged
      successful result.
17. Speed pass without review mode (Q09): with review mode disabled, the same
    speed pass runs before the ordinary human commit gate. Test-only changes
    and duration exclusions join the commit; any other change returns through
    the implementation check and the `speed` validation before that gate. No
    review exchange is created for this path. The prepare-release gate stays
    at `cov`.
18. Reviewer unchanged: the code reviewer and implementation-check still never
    run `ghog day` or `ghog full` at any level.
19. Documentation and tests: `GROUNDHOG.md`, `tools/Pytest reset specs.md`
    (new decision rows), the day walk docstrings, and the groundhog acceptance
    tests (AT11 day walk, AT16 day noop) cover the default walk, the three
    levels, the level precedence, the level-aware snapshot, and the closing
    instruction of every level and outcome, restart lines included.
    Acceptance coverage exercises a default failure against a full-level
    failure, an environment-selected level restarted explicitly, a lower
    requested level backed by a stronger saved proof, ignored duration
    observations, and the permitted duration-exclusion path.

## Closing instructions for the LLM by level

The last lines of a walk are the instruction an LLM acts on. For each level
and outcome, the report must carry the following instruction; `<level>`
stands for the level of the walk, and the wording itself is left to the
design.

| Level | Outcome | Required closing instruction |
| --- | --- | --- |
| default | green | The full suite was skipped on purpose (no level requested); the walk objective (check.bat and the affected tests) is met; do not run the full suite unless the calling instruction asks for a level; to ask for one, run `ghog day --full=pass`, `ghog day --full=cov`, or `ghog day --full=speed`; carry on with the calling instruction. |
| default | check or affected failure, including its crash diagnostics | Today's fix instruction, then, when the existing recovery rules permit a restart, restart with plain `ghog day`. |
| `pass` | green | Objective met at `pass`: the whole suite passes; coverage and duration gates are not required by the requested `pass` objective; carry on with the calling instruction. |
| `cov` | green | Objective met at `cov`: the whole suite passes and the coverage gate is met; the duration gate is not required by the requested `cov` objective; carry on with the calling instruction. |
| `speed` | green | Objective met at `speed`: the whole suite passes, the coverage gate is met, and no unaccepted duration outlier remains under the configured exclusions; carry on with the calling instruction. |
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
the resolved level as well; any suggested day-walk restart preserves that
level.

## Code references for full suite levels

- `tools/groundhog/day.py`: `run_day`, the three-step walk and the snapshot
  noop check.
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
| Q01 | `pass` runs the whole suite and requires it to pass without a crash, with no coverage collection and no duration enforcement; durations are informational. It proves what the default walk cannot: no test outside the affected set fails. | Gap 3; closing instructions (`pass` rows) | Skip the suite entirely at `pass` (the default walk under another name); collect coverage without enforcing it (costs time for a figure nobody acts on). |
| Q02 | One precedence rule for `ghog day` and direct `ghog full`: `--full`, then `GHOG_FULL`, then the command default (no full step, or `speed`). Development walks pick `GHOG_FULL` up. | Gaps 2 and 9 | `GHOG_FULL` for `ghog day` only (two rules to remember); variable for humans only with explicit levels in every skill (needs a "none" value and removes the human knob). |
| Q03 | A level upgrade on unchanged sources reuses the successful check and affected results of the same validated snapshot, runs only the missing full-suite objective, and names the reused results. | Gap 7 | Re-run all three steps on every upgrade (pays check and affected twice at review and release time). |
| Q04 | The test-only exception needs positive evidence that every changed file serves tests exclusively; shared, configuration, tooling or uncertain files go to review. Path names and collection roots are insufficient. | Gap 14; gap 16 | Collection root or file-name classifier (a broad root lets production code skip review); requestor judgement (not verifiable). |
| Q05 | Every repair the speed walk needs (failure, coverage gap, crash, duration) restores `speed`, preserves coverage and assertions, and is classified as a whole with gaps 14 and 15; operational stop rules still apply. | Gap 16 | Always start a round for non-speed failures (heavy for one missing test); escalate to the human (stops fixable automation). |
| Q06 | A repair outside both exceptions starts an ordinary replacement round for the same step, naming the change; `speed` validation repeats at the next convergence, reusing an unchanged successful result. | Gap 16 | A dedicated speed-review round limited to the diff (new protocol round type, reviewed without context). |
| Q07 | A duration exclusion is a narrow exception to Q04, allowed after an attempted improvement, with the call, measured time, attempt and reason in the gate evidence; it covers duration acceptance only. | Gap 15; closing instructions (`speed` outliers row) | Only a human may exclude (blocks the gate on every slow call); an exclusion starts a round (heavy for a configuration decision). |
| Q08 | Every walk reports the selected objective and its source, the strongest valid saved proof, and which steps ran or were reused; detached walks keep their level; consumer compatibility is verified. | Gaps 1 and 5; closing instructions (noop paragraph) | Keep the closing line unchanged (cannot tell the default walk from `pass`, nor a noop from a fresh run). |
| Q09 | With review mode disabled, the same speed pass runs before the ordinary human commit gate; other changes return through the implementation check; no review exchange is created. | Gap 17 | No speed pass without review mode (speed drifts unnoticed); `speed` at prepare-release instead (all slow calls surface at release time). |
| Q10 | A saved result that cannot establish its level satisfies no requested level; the first requested walk after the upgrade revalidates its selected objective. | Gap 8 | Treat a positively identified legacy green snapshot as `speed` (needs a compatibility guarantee that every legacy snapshot came from an all-gates walk). |
