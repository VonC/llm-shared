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
2. Level selection: `ghog day` accepts a level through the `--full=pass|cov|speed`
   parameter or the `GHOG_FULL` environment variable. The parameter takes
   precedence over the variable. An unknown value is a setup error (exit 5),
   never a silent fallback to the default.
3. Level verdicts: at `pass`, a coverage gap and duration outliers do not fail
   the run. At `cov`, duration outliers do not fail it. At `speed`, the run
   keeps today's verdicts. At `pass`, the full suite runs without coverage
   collection or duration enforcement; any recorded durations are
   informational.
4. Closing instructions by level: the report ends with the instruction the
   LLM must act on, as listed in "Closing instructions for the LLM by level"
   below. It only asks for the work its level covers: no covg or
   coverage-gap request below `cov`, no slow-test request below `speed`.
   Every printed restart line names the level of the walk it restarts (for
   example `ghog day --full=cov`), whatever the source of that level, so an
   LLM following the line literally never drops back to the default walk. A
   default walk restarts with plain `ghog day`.
5. Noop snapshot records the level: `a.ghog.day.ok` stores the highest level
   the green walk proved (none, `pass`, `cov`, `speed`). A walk is a noop only
   when sources are unchanged and the recorded level is at least the requested
   one. A green default walk never turns a later `cov` or `speed` walk into a
   noop.
6. Direct `ghog full`: `ghog full` accepts the same level through the same
   selectors as `ghog day` (their precedence is settled by Q02) and keeps
   `speed` as its default when no selector is supplied, so a plain direct call
   behaves as today.
7. Development skills use the default walk: `implement-step.md`,
   `implement-missing-step.md`, `split-large-file.md`, and the plan command
   written by `write-plans.md` use `ghog day` with no level. Their wording no
   longer promises a full coverage pass.
8. The groundhog loop keeps the caller's level: `groundhog.md` restarts every
   fix with the same level the loop was started with, so a fix never raises or
   drops the objective. `fix_slow_test.md` applies only to a `speed` walk and
   restarts it at `speed`.
9. Requestor validation at `cov`: the code-review requestor project default
   becomes the `cov` walk (`DEFAULT_PROJECT_VALIDATION_COMMANDS` in
   `tools/code_review_validation.py`), run green before any request is
   published.
10. Prepare-release green gate at `cov`: the green-gate routine in
    `prepare-release.md` and both `run ghog day` operations in
    `prepare_release_plan_workflow.py` name the `cov` walk.
11. Requestor speed pass at convergence: when the requestor receives a
    commit-ready answer, it runs one `speed` walk before the human gate, then
    loops on it until exit 0:
    - if a green `speed` walk needed no change, or only changes within the
      test-only boundary (Q04) or a duration exclusion (Q07), the requestor
      stages those changes, amends `a.commit` when its groups no longer
      match, accepts the commit-ready answer, and presents the human gate
      (`Commit` or `Rework and review again`) with those changes listed in
      its evidence;
    - if any repair the walk needed falls outside that boundary, whatever
      failure triggered it (Q05), the requestor starts another review round
      covering that change, instead of presenting the human gate. This
      extends the current rule that the requestor cannot start a new round
      from convergence, for this case only.
12. Reviewer unchanged: the code reviewer and implementation-check still never
    run `ghog day` or `ghog full` at any level.
13. Documentation and tests: `GROUNDHOG.md`, `tools/Pytest reset specs.md`
    (new decision rows), the day walk docstrings, and the groundhog acceptance
    tests (AT11 day walk, AT16 day noop) cover the default walk, the three
    levels, the level precedence, the level-aware snapshot, and the closing
    instruction of every level and outcome, restart lines included.

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

## Open questions for the v0.13.0 full suite levels feature request

### Q01: What the `pass` level runs

Question description: the default walk (no level) already stops after check.bat and `ghog affected --no-cov`, without the full suite. The `pass` level is described as "full run just to check there is no error". The question is whether `pass` runs the whole test suite at all, and what it measures on the way.

#### BBQ for Q01

The default walk tastes the dishes that changed since the last service. `pass` should be the one where every dish on the menu is tasted once, only to check nothing is burnt: no weighing of portions, no stopwatch on the grill. If `pass` skipped tasting altogether, it would be the same as the default and the level would have no reason to exist.

In this picture: tasting the changed dishes is the affected run, tasting every dish is the full suite, burnt means a failure or a crash, weighing portions is the coverage measure, and the stopwatch is the duration-outlier verdict.

#### Options for Q01

- Option A: `pass` runs the whole suite with no coverage collection and no duration verdict; any recorded durations are informational only.
  - pro: it is the cheapest run that still proves the whole suite passes, which the default walk never proves;
  - pro: it keeps a distinct purpose for each level (default: affected only; `pass`: whole suite; `cov`: plus gate; `speed`: plus timing).
  - con: informational durations are bookkeeping nobody acts on at this level.
- Option B: `pass` skips the test suite entirely (check.bat and the affected tests only).
  - pro: fastest possible walk.
  - con: it is the default walk under another name, so the level adds nothing.
- Option C: `pass` runs the whole suite with coverage collected, but the gate is not enforced.
  - pro: the coverage figure stays visible in the report.
  - con: the measure costs run time at a level whose goal is to be fast, and a figure nobody acts on invites coverage work during development.

#### Recommended option for Q01 (with arguments for this choice)

Option A: the only thing the default walk cannot tell is whether a test outside the affected set now fails. `pass` answers exactly that, at the lowest cost, and leaves coverage and speed to the levels that act on them.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: `pass` executes the entire test suite and requires its tests to pass without a suite crash. It does not collect coverage or enforce duration thresholds; any recorded durations are informational. This gives `pass` a purpose the default walk lacks without paying for measures the level ignores.

### Q02: Level selection for `ghog day` and direct `ghog full`

Question description: the level comes from `--full=<level>` or from `GHOG_FULL`, the parameter winning. Two cases are open. First, the development skills call `ghog day` with no level: if a human sets `GHOG_FULL=speed` in their shell, do those walks pick it up? Second, a direct `ghog full` keeps `speed` as its default when no selector is supplied (settled), but with `GHOG_FULL=cov` set, it is not stated whether plain `ghog full` runs at `cov` or `speed`.

#### BBQ for Q02

The recipe cards for weekday cooking say nothing about the oven setting, and the special dinners say "high". A dial on the wall sets the oven for any card that says nothing. The chef also has a "full roast" button that has always meant the hottest setting. Either the dial governs the button too, or the button ignores the dial.

In this picture: the recipe cards are the skill instructions, the weekday cards are development walks with no level, the special dinners are the requestor and release walks with an explicit level, the dial is `GHOG_FULL`, and the "full roast" button is a direct `ghog full`.

#### Options for Q02

- Option A: one precedence rule for both commands: explicit `--full`, then `GHOG_FULL`, then the command default (`ghog day`: no full step; `ghog full`: `speed`). Development walks pick up `GHOG_FULL`.
  - pro: one predictable selector for every command, and one knob that lets the human raise every walk of a session with no instruction edit;
  - con: a variable left set in a shell silently changes both development walks and direct `ghog full` calls.
- Option B: `GHOG_FULL` applies to `ghog day` only; a direct `ghog full` without `--full` always runs at `speed`.
  - pro: a direct `ghog full` keeps one unconditional meaning.
  - con: the two commands follow different selection rules, which is easy to forget.
- Option C: `GHOG_FULL` only applies to human calls; skill instructions always pass an explicit level, including an explicit "none" for development walks.
  - pro: skill behavior never depends on the shell state.
  - con: needs a "none" value and edits every development instruction, and the human loses the knob for those walks.

#### Recommended option for Q02 (with arguments for this choice)

Option A: a single precedence rule is the easiest to predict and to document, and the variable exists precisely so the human can raise the objective without changing instructions. The risk of a forgotten setting is covered by the report stating the selected objective and where it came from (Q08). Examples:

- `GHOG_FULL` unset: `ghog day` stops after the affected tests; `ghog full` runs at `speed`.
- `GHOG_FULL=cov`: `ghog day` and `ghog full` both run the full suite at `cov`.
- `GHOG_FULL=cov` and `--full=speed`: both commands run at `speed`.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: both commands resolve an explicit level before `GHOG_FULL`. When neither is set, `ghog day` has no full step and `ghog full` uses `speed`. The lightweight default walk applies only when no level is supplied at all. This keeps one predictable rule while final-phase callers stay pinned by their explicit parameter.

### Q03: Level upgrade on unchanged sources

Question description: the level-aware snapshot makes a `cov` walk after a green default walk run again, even with unchanged sources. check.bat and the affected tests were already proven green for those exact sources. The question is whether the upgraded walk re-runs all three steps or goes straight to the full run.

#### BBQ for Q03

The inspector already signed the wiring and the plumbing of an unchanged house. Now the buyer asks for the full structural survey. Sending the wiring and plumbing inspectors back costs a morning for a verdict already on file; going straight to the survey relies on the signed sheet being about this exact house.

In this picture: the house is the source snapshot, the wiring and plumbing sign-offs are the green check.bat and affected steps, the structural survey is the full run at the requested level, and the signed sheet is `a.ghog.day.ok`.

#### Options for Q03

- Option A: reuse the successful check.bat and affected results when the snapshot proves them green on the same sources; run only the full step at the requested level.
  - pro: no step is paid twice, which is the whole point of the change;
  - pro: consistent with today's noop rule, which already trusts the snapshot.
  - con: the report must say clearly which results were reused, or a reader may think they ran (Q08).
- Option B: always re-run the three steps when the requested level is higher than the recorded one.
  - pro: every verdict in the report comes from this walk.
  - con: check.bat and the affected tests run again for nothing, at exactly the moment (review, release) where the full run is already the long part.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the snapshot is already trusted to skip a whole walk; trusting it to skip two thirds of one is the same rule, and the report stays honest by naming the reused results. A green full run at a lower level never counts as proof of a higher one.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: an upgrade may reuse successful check and affected-test results for the same validated snapshot, runs the missing full-suite objective, and identifies the reused results in its report. It saves those runs at every level upgrade with the same guarantee the noop already relies on.

### Q04: What counts as a test-only change in the requestor speed pass

Question description: at a commit-ready convergence, the requestor runs a `speed` walk. A test-only change goes to the human gate; any other change starts another review round. The boundary decides whether a change skips review, so an error in the wrong direction lets production code reach a commit unreviewed. Consuming projects lay out their tests differently, and a pytest collection root may even be the project root, holding application code.

#### BBQ for Q04

The tailor may shorten the fitting pins without calling the customer back, but touching the fabric means another fitting. Someone has to decide, for each piece in the workshop, whether it is a pin or fabric. If "everything on the pin table" counts as a pin, and the fabric was left on that table, the fabric gets cut with no fitting.

In this picture: the pins are files that serve tests exclusively, the fabric is production code, shared helpers and configuration, another fitting is a new review round, and the pin table is a test collection root or a test-like file name.

#### Options for Q04

- Option A: a change qualifies as test-only only when every changed file is established to serve tests exclusively. Shared runtime code, configuration or tooling that can affect production behavior, and any file whose test-only use cannot be established, require another review. Path names and collection roots alone are not sufficient evidence.
  - pro: when exclusive test use cannot be established, the change requires another review;
  - pro: the rule is stated as observable behavior, leaving how test-only use is established to the design.
  - con: helper files that really are test-only but cannot be positively identified cost an extra round.
- Option B: a path is test-side when it is under a pytest collection root, or has a test-like file name.
  - pro: simple and mechanical.
  - con: a collection root such as the project root makes every production file test-side, so production changes can bypass review.
- Option C: the requestor classifies by judgement and states its classification in the human gate evidence.
  - pro: handles every edge case.
  - con: not reproducible, and the decision to skip a review round becomes an unverifiable claim.

#### Recommended option for Q04 (with arguments for this choice)

Option A: the only acceptable failure mode for a review-skipping rule is an unnecessary review. Positive evidence is required to use the exception; uncertainty must lead to another review. B lets a broad collection root exempt production code, and C cannot be checked. The duration-exclusion case is a separate, narrow exception (Q07), not part of this classification.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: the post-review delta qualifies for the test-only exception only when every changed file is established to serve tests exclusively. Shared runtime code, configuration or tooling that can affect production behavior, and uncertain files require another review. Path names and collection roots alone are insufficient evidence. The duration-exclusion exception of Q07 stays separate.

### Q05: Other failures found by the requestor speed pass

Question description: the reviewer never runs the full suite, and the reviewer may stage repairs. So the `speed` walk at convergence can fail for a reason other than slowness: a test failure (exit 2), a coverage gap (exit 3), or a crash (exit 4) introduced by those repairs. The feature request only defines the outcome for duration outliers.

#### BBQ for Q05

The final dress rehearsal is meant to check the show runs on time. If an actor forgets a line, the stage manager still has to decide: fix it backstage and carry on to opening night, or call the director back for another rehearsal.

In this picture: the dress rehearsal is the `speed` walk, running on time is the duration verdict, a forgotten line is a failure, coverage gap or crash, fixing backstage is a test-only fix before the human gate, and calling the director back is another review round.

#### Options for Q05

- Option A: apply the same rule to every repair the speed walk needs: restore the `speed` objective, then classify the complete repair delta with Q04 and Q07; test-only changes go to the human gate, anything else starts another round.
  - pro: one rule for every outcome of the walk, easy to follow;
  - pro: a production repair is always reviewed, whatever triggered it.
  - con: a coverage gap closed with new tests reaches the human gate without review of those tests.
- Option B: any failure other than duration outliers starts another review round, whatever the repair touches.
  - pro: the reviewer sees every correction of a reviewed step.
  - con: a round for a single missing test is heavy, and it reopens the review loop the change is meant to shorten.
- Option C: any failure other than duration outliers escalates to the human.
  - pro: the human knows the reviewed work was not green.
  - con: stops automation for problems the requestor can fix itself.

#### Recommended option for Q05 (with arguments for this choice)

Option A: the dividing line that matters is what the repair changed, not why it was needed. New tests are still listed in the human gate evidence, where the human can choose `Rework and review again`.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: for repairable test, coverage, crash, or duration failures, the requestor restores the selected `speed` objective, preserves test coverage and assertions, and classifies the complete repair delta using Q04 and Q07 before the gate. Existing operational stop and interruption rules still apply: this never authorizes weakening checks to reach exit 0, or retrying a setup error without end.

### Q06: Scope of the review round started by the speed pass

Question description: when a repair made during speed validation falls outside both the test-only boundary (Q04) and the narrow duration-exclusion exception (Q07), the requestor starts another review round instead of presenting the human gate. The question is what that round asks the reviewer to look at, and what happens when it converges again.

#### BBQ for Q06

After the final inspection, the builder moved a load-bearing wall to make the hallway faster to walk through. The inspector comes back. Either they walk the whole house again with the moved wall flagged on the plan, or they look only at the wall and sign. Then, before handing the keys over, someone times the hallway again.

In this picture: the moved wall is the production-code speed repair, the whole house is the implementation step, the flag on the plan is the writer response naming the speed change, and timing the hallway again is the next `speed` walk at the new convergence.

#### Options for Q06

- Option A: an ordinary replacement round for the same step, whose change summary and writer response name the speed change; at its next commit-ready answer, the requestor runs the `speed` validation again.
  - pro: reuses the existing round mechanism with no new round type;
  - pro: the reviewer sees the speed change in the context of the whole step.
  - con: the reviewer reads the whole step again, even if only one function changed.
- Option B: a dedicated speed-review round limited to the diff of the speed repair.
  - pro: shorter review.
  - con: a new round type in the exchange protocol, and a repair reviewed without its context.

#### Recommended option for Q06 (with arguments for this choice)

Option A: the exchange already knows how to replace a round. When the reviewer stages no further repair, the unchanged, already successful `speed` result can be reused at the next convergence; further reviewer repairs can legitimately require another validation or round.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: it changes only when the requestor may start a round, not what a round is. The speed change is reviewed in the context of its step, and the `speed` validation is repeated at each new convergence, reusing an unchanged successful result.

### Q07: Slow calls accepted with `ghog exclude` during the speed pass

Question description: today a slow call can be shortened or, when it is genuinely slow, accepted with `ghog exclude` after a real attempt to shorten it. An exclusion changes neither tests nor production code, but it changes what the `speed` level accepts, and the file it writes may not serve tests exclusively in the sense of Q04. The question is how the requestor treats an exclusion at convergence.

#### BBQ for Q07

The race marshal can either make a slow runner faster or write "medical exemption" next to their name. The exemption changes no runner, but it changes what finishing on time means for this race, and the race director may want to know.

In this picture: the slow runner is a flagged test call, making them faster is a test or production change, the exemption is `ghog exclude`, and the race director is the human at the commit gate.

#### Options for Q07

- Option A: a duration exclusion is an explicit, narrow exception to Q04: allowed at convergence after an attempted fix, it goes to the human gate with evidence naming the excluded call, its measured time, the attempted improvement, and the reason for accepting the duration. The exception covers duration acceptance only.
  - pro: the human sees and can reject it through `Rework and review again`;
  - pro: no review round for a decision that touches no code, with a boundary narrow enough to review.
  - con: the requestor can take the easy way out on a call it could have shortened.
- Option B: the requestor may not exclude at convergence; only a human can add an exclusion.
  - pro: no silent acceptance of slowness.
  - con: every genuinely slow call blocks the gate until a human steps in.
- Option C: an exclusion starts another review round.
  - pro: the reviewer judges whether the exemption is legitimate.
  - con: a round for a one-line configuration decision.

#### Recommended option for Q07 (with arguments for this choice)

Option A: `fix_slow_test.md` already demands a real attempt before excluding. Requiring the attempt and the measured time in the gate evidence gives the human the final say without a round, and keeping the exception to duration acceptance stops it from covering unrelated configuration changes.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: a duration exclusion is an explicit exception to Q04, limited to accepting a measured duration after an attempted fix. The gate evidence states the excluded call, its measured time, the attempted improvement, and the reason. It never covers unrelated configuration changes or the removal of correctness or coverage checks.

### Q08: What a walk reports about its objective and evidence

Question description: after the change, `exit=0` can mean affected tests green, whole suite green, coverage gate met, or speed met. With a level-aware snapshot (gap 5) and reused results (Q03), a single walk also involves three distinct facts: the objective selected for this invocation (and where it came from, Q02), the strongest valid saved proof, and which steps actually ran or were reused. For example, after a green `speed` walk, an unchanged default walk is a noop: no suite ran, the requested objective is none, and the saved proof is `speed`.

#### BBQ for Q08

A pass stamp on a car could mean "the lights work" or "the full road test passed". A stamp dated today may also just copy last week's road test result. A useful stamp says what was asked today, what the car holds on file, and what was actually checked this morning.

In this picture: the stamp is the green closing report, the lights check is the default walk, the road test is the `speed` level, last week's result is the saved snapshot proof, and this morning's checks are the steps run in this invocation.

#### Options for Q08

- Option A: the closing report and `ghog status` state the selected objective and its source (parameter, variable, or default), the strongest valid saved proof, and whether each step ran or was reused; a default walk states that the full suite did not run; a detached walk keeps the level selected for its invocation. Supported consumers of the closing line keep working.
  - pro: every green result names what it proves, for humans and for the tools that branch on the output;
  - pro: a forgotten `GHOG_FULL`, and a noop backed by a stronger proof, both become visible.
  - con: the closing report grows, and its consumers must be checked for compatibility.
- Option B: keep the closing report unchanged and rely on `cov=skipped` and the absence of a full step header.
  - pro: no report change.
  - con: `cov=skipped` does not distinguish the default walk from `pass`, the level is never stated, and a noop cannot say what it relies on.

#### Recommended option for Q08 (with arguments for this choice)

Option A: the closing report is the branching signal of every caller; it must say what was proven, what was reused, and what was requested. The field names and their encoding belong to the design.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: without these three facts, a green default walk can be mistaken for a proven coverage or speed objective, and a noop can hide that it rests on an earlier, stronger proof. Compatibility with the supported consumers of the closing line is a requirement to verify, not an assumption.

### Q09: Speed pass when review mode is disabled

Question description: the `speed` walk only happens at a code-review convergence. When review mode is disabled, the requestor keeps the ordinary human commit gate and creates no exchange, so a project working without review mode would never run a `speed` walk before a commit, and prepare-release only proves `cov`.

#### BBQ for Q09

The bakery times every loaf only when the quality inspector visits. On days without an inspector, the loaves go out untimed, and the release to the shops only checks their weight.

In this picture: timing a loaf is the `speed` walk, the inspector's visit is a code-review convergence, days without an inspector are commits with review mode disabled, and the weight check at the shop is the `cov` gate of prepare-release.

#### Options for Q09

- Option A: without review mode, run the same speed pass before the ordinary human commit gate; test-only changes (Q04) and duration exclusions (Q07) join the commit, and any other change returns through the implementation check and the `speed` validation before that gate. No review exchange is created for this path.
  - pro: every committed step meets the speed objective, with or without review mode;
  - pro: same boundary in both workflows.
  - con: adds the one slow walk to the non-review path as well.
- Option B: no speed pass without review mode; speed is proven only on reviewed steps or when a human asks for it.
  - pro: the non-review path stays as fast as possible.
  - con: suite speed can drift across a whole release without any walk noticing.
- Option C: prepare-release proves `speed` instead of `cov` when the project has no review mode.
  - pro: one speed check per release.
  - con: all slow calls surface at once at release time, far from the steps that introduced them.

#### Recommended option for Q09 (with arguments for this choice)

Option A: the commit gate is the final phase of a step in both workflows; the speed objective should not depend on whether a reviewer was involved. The agreed release `cov` gate stays unchanged.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: with review mode disabled, the speed pass runs before the ordinary human commit gate. Changes outside the test-only and exclusion scope return through the implementation check and the `speed` validation before that gate, and no review exchange is created. Suite speed stays guarded at every commit.

### Q10: What an existing snapshot without a level may prove

Question description: snapshots written before this change (`a.ghog.day.ok`) record no level. A legacy green walk did prove the equivalent of `speed`, but a file with missing or unreadable level information cannot be told apart from a damaged one. The first walk after the upgrade needs one defined outcome.

#### BBQ for Q10

The garage switches to a new inspection form that has a box for the level of inspection. Old certificates have no such box. The garage can either inspect once more and fill in the new form, or read every old certificate as a full inspection, trusting that the old process always did one.

In this picture: the old certificates are legacy snapshots, the level box is the recorded level, inspecting once more is re-running the walk, and reading them as a full inspection is treating a legacy snapshot as `speed`.

#### Options for Q10

- Option A: a saved result that cannot establish its achieved level satisfies no requested level; the next successful walk records explicit evidence.
  - pro: every reuse rests on explicit, inspectable evidence;
  - pro: one rule for legacy, missing, and invalid level information.
  - con: the first requested walk after the upgrade must revalidate its selected objective instead of reusing evidence with no established level, even when sources did not change.
- Option B: a positively identified legacy all-green snapshot counts as `speed`; missing or invalid level information in any other form satisfies nothing.
  - pro: saves one run per project after the upgrade.
  - con: needs an explicit compatibility guarantee that every legacy green snapshot really came from a full walk with all gates.

#### Recommended option for Q10 (with arguments for this choice)

Option A: the first requested walk after the upgrade revalidates its selected objective, which may be the lightweight default; later level upgrades still follow Q03. The benefit is that no result is ever reused on an assumption, and a single rule covers every snapshot that cannot state its level.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: a saved result that cannot establish its achieved level must not satisfy a requested level, and the next successful walk records explicit evidence. Revalidating the selected objective once after the upgrade is a small price for evidence that never rests on an assumption.
