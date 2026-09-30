# Design v0.13.0 -- full suite levels

Reference feature-request: [feature-request.v0.13.0.full_suite_levels.md](feature-request.v0.13.0.full_suite_levels.md)

---

## Context for v0.13.0 full suite levels

Every `ghog day` walk ends today with the full suite, a coverage gate and, in
a sequential project, a duration-outlier verdict. Development skills close
every step with that walk, so they pay for the full run and for coverage and
test-speed work while the code is still moving. The consolidated feature
request settles a default walk without the full suite, three on-demand levels
(`pass`, `cov`, `speed`), the evidence every walk reports, and where the full
objective is proven: before every code-review request under the default
validation policy, between implementation-check and the commit menu without
review mode, and at `cov` in the prepare-release gate. No `speed` walk runs at
a commit-ready answer. This design answers that requirement; it replaces an
earlier design, dropped with the post-review `speed` pass it was built for.

## Scope for v0.13.0 full suite levels

The v0.13.0 outcomes are:

1. `ghog day` stops after the affected tests unless a level is selected, and
   every groundhog command that runs or repairs the suite resolves one level
   from `--full`, `GHOG_FULL`, or its command default.
2. Each level has its own full-run shape, verdict, closing instruction, and
   restart line, and every walk reports its objective, its valid proof, and
   what ran or was reused, in the report and in `ghog status`.
3. The workflow phases ask for the right level: development walks stay on the
   default, the code-review requestor's default validation proves `speed`
   before each request (a declared `.review-validation` set stays
   authoritative), the review-less step proves `speed` before its commit
   menu, and the prepare-release gate proves `cov`.

Everything else is either supporting design context for those outcomes or explicitly deferred.

### In scope for v0.13.0 full suite levels

- A level value, its resolution rule, its error handling, and its
  propagation through the day walk, the repair commands, the detached walk,
  the status file, and the report.
- Level-shaped pytest runs and verdicts, including the sequential timing pass
  in parallel `speed` day walks.
- A level-aware source snapshot with step reuse on level upgrade, proof
  invalidation on contradicting results, and a conservative reading of legacy
  or unreadable markers.
- Closing instructions and restart lines by level and outcome.
- The requestor's default validation at `speed`, the migration notice for
  declared validation sets, and duration-exclusion evidence in the request.
- The review-less `speed` pass and its return path through
  implementation-check.
- Instruction, manual, specification and test updates for the above.

### Deferred from v0.13.0 full suite levels to v0.14.0 and beyond

- Making `ghog timings` part of a direct `ghog full` call in parallel
  projects: a direct call keeps its single-run shape (feature-request gap 9).
- Extending the snapshot digest beyond Python files and gate configuration
  (Markdown and other non-Python changes still do not invalidate it).
- Any change to the reviewer side: the code reviewer and implementation-check
  still never run `ghog day` or `ghog full`.
- Qualifying transcript headings of a second exchange on the same document
  with its exchange number, a renderer defect seen while reviewing this
  requirement; it belongs to the review tooling, not to this effort.

---

## Confirmed Technical Facts for v0.13.0 full suite levels

These facts were confirmed by inspecting the current codebase before writing this design.

**The day walk is three fixed steps**: `run_day` in `tools/groundhog/day.py`
calls `commands.run_check`, then `commands.run_tests` with `sub=affected,
no_cov=True`, then `commands.run_tests` with `sub=full, no_cov=False`, each
framed by `_timed_step` headers, and writes the snapshot only after a green
full step. The level must therefore change the walk's step list, not only a
verdict.

**The CLI has no level today**: `_build_arg_parser` in `tools/groundhog/cli.py`
gives `day` only `--force` and `--detach`, and `full` no option at all.
`Invocation` in `tools/groundhog/context.py` is a frozen dataclass with `sub`,
`files`, `no_cov`, `mode`, `root`, `force`, `detach`, `node`, and `seconds`,
and `day.py` derives each step with `dataclasses.replace`. A level field on
`Invocation` reaches every step and every next-step builder for free.

**argparse errors exit 2**: an invalid choice makes argparse print usage and
exit 2, which is groundhog's test-failure code. An invalid `--full` value
therefore needs its own handling to reach the setup-error code 5.

**Parallel projects move the duration gate to `ghog timings`**: a project with
a `.ghog-parallel` marker (llm-shared has one) runs `ghog full` on xdist
workers, with coverage but without `--testmon` or `--durations`
(`runner.pytest_command`). `durations_summary.measures_durations` derives the
verdict from the built command, so a parallel full run never judges speed.
The sequential `ghog timings` subcommand (`--no-cov --durations=0`) owns the
duration verdict there. No instruction file names `ghog timings`; only
`bin/ghog_cycle.bat` chains `day` then `timings` by default. Today, therefore,
no workflow judges speed in a parallel project.

**Verdicts are ordered and judged last for speed**: `commands.classify`
returns crash (4), setup error (5), failures (2), coverage gap (3), then
duration outliers (8) only on a run already green on tests and coverage; the
coverage gate is read only when `_measures_coverage` holds. Level verdicts can
reuse this order by choosing which measures a run carries.

**Next-step lines are fixed strings naming plain `ghog day`**:
`tools/groundhog/reporting_nextstep.py` holds `MSG_CHECK_FAIL`,
`MSG_AFFECTED_NOCOV_FAIL`, `MSG_SINGLE_RESTART`, `MSG_SINGLE_GREEN`,
`MSG_OUTLIERS` (all ending on `ghog day`), `MSG_AFFECTED_NOCOV_OK`
(`Next: ghog full`), `MSG_FULL_OK` (`Objective reached`) and
`MSG_DAY_NOOP`. Each restart and each success line must become
level-aware, including those printed by `ghog single`, `ghog check` and a
covered `ghog affected` outside a walk.

**The closing line and status line are key=value strings**:
`reporting.closing_line` prints `<project>: ghog <label> done fail= warn=
xfail= cov= outliers= excluded= exit=`, and `status.write_running` /
`write_done` print `<project>: ghog <label> state=... exit=...` into
`a.ghog.status`, read back through `_STATE_RE`. No tool outside
`tools/groundhog` parses the closing line; only groundhog's own status reader
and tests, plus LLM readers of `a.ghog.log`, consume these lines.

**The snapshot is a single digest line written in place**:
`snapshot.write_marker` writes `<sha digest>\n` to `a.ghog.day.ok` in the
artifact home with `write_text`, and `is_unchanged` compares it to a fresh
digest over Python file paths, sizes and mtimes plus the gate configuration
files, with every read failure biased toward a new walk. A failing walk
leaves the old marker in place today.

**The detached walk rebuilds its own command line**:
`status._detached_day_command` spawns `cli.py day --root <root> --llm
[--force]`, so any level given on the command line is lost today unless
forwarded; the survivor inherits the launching environment.

**Duration exclusions are local, ignored state**: `ghog exclude` writes the
`[exclusion]` section of `a.ghog.outliers` in the review artifact home, which
is Git-ignored. An exclusion therefore adds no tracked path to any delta; its
evidence lives in the ghog report (`excluded=` and the exclusion block).

**The requestor's mandatory validation comes from one tuple or one file**:
`DEFAULT_PROJECT_VALIDATION_COMMANDS = ("ghog day",)` in
`tools/code_review_validation.py`, overridable by a versioned
`.review-validation` file (llm-shared has none). Additions cannot remove a
project command. `code-review-requestor.md` requires the writer to run the
resolved set green before every request is published, so the validation runs
once per round.

**The convergence path needs no change**: at a commit-ready answer the
requestor presents the human gate; only a human `confirm` leaves
`convergence-gate`, and `consume-answer` never takes a convergence answer
(`tools/review_exchange_cli_parser.py`). With no `speed` walk at that point,
the exchange core needs no new operation.

**The step chain branches on review mode after `a.commit`**:
`implement-step.md` runs implement, `pw handoff check <x>` and the
implementation check, `pw handoff after-check <x>`, then `group-commits-msg`
(its `git add -A` variant) up to a reviewable root `a.commit`, and only then
samples review mode with `rvw_status.bat`: on, `pw skill code-review-requestor`
takes over; off, the ordinary commit gate (the group-commit menu) follows. The
same chain serves implement-missing-step and split-large-file. At that branch
point every change of the step is staged and implementation-check has passed.

**Prepare-release names the walk in two operation strings**:
`prepare_release_plan_workflow.py` lists `"run ghog day"` for the integration
sync and `"run git range-diff and ghog day"` for the feature `--onto` replay.

---

## Current Behavior for v0.13.0 full suite levels

```txt
ghog day
  snapshot unchanged? -> noop, exit 0
  check.bat            -> fail: "fix ..., re-run ghog day"
  affected --no-cov    -> fail: "fix ..., then ghog day"   ok: "Next: ghog full"
  full (cov gate)      -> 2: ghog single | 3: covg | 4: crash
                          sequential project only: 8: fix_slow_test, then ghog day
  green                -> write snapshot, "Objective reached"
  failing              -> old snapshot kept as is
parallel project: speed is never judged unless someone runs ghog timings
```

## Target Behavior for v0.13.0 full suite levels

```txt
level = --full | GHOG_FULL | default (day: none, full: speed); invalid -> exit 5
ghog day (level L)
  valid saved proof P on the same digest:
    P >= L                -> noop, "met by saved proof P, nothing ran"
    none <= P < L         -> reuse check + affected, run the full step(s) at L
  otherwise               -> check, affected --no-cov, then:
    L = none   -> stop: "full suite skipped on purpose ... carry on"
    L = pass   -> full --no-cov (no durations)
    L = cov    -> full with coverage gate (no durations)
    L = speed  -> sequential: full with coverage + durations (today)
                  parallel:   full with coverage, then timings on green
  every restart line -> "ghog day --full=L" (plain "ghog day" when L = none)
  end -> marker proof = highest level still valid (see invalidation);
         closing line and a.ghog.status: full=L src=... proof=... reused=...
```

---

## Level Model for v0.13.0 full suite levels

### Level value and ordering

A `FullLevel` value with four members ordered by the proof they establish:
`none < pass < cov < speed`. `none` is an internal value for the default
walk; it is never an accepted `--full` or `GHOG_FULL` value, so no restart
line can ever print `--full=none`. The ordering is what the snapshot, the
noop rule and the upgrade rule compare. `cov` implies `pass` because a
covered full run still requires every test to pass; `speed` implies `cov`.

A separate reporting value, `unproven`, means that no valid proof exists for
the current sources: no marker, a stale digest, an unreadable or legacy
marker, or a proof invalidated by this invocation. It is never a selector
and never written to the marker.

### Resolution rule

`ghog day`, `ghog full`, and the repair commands that print restart lines
(`ghog check`, `ghog affected`, `ghog single`) accept an optional `--full`
argument. Resolution happens once, in the CLI, before the lifecycle bracket:

1. an explicit `--full` wins (source `param`), and `GHOG_FULL` is then not
   read at all, so a valid parameter overrides an invalid environment value;
2. otherwise a non-empty `GHOG_FULL` (source `env`);
3. otherwise the command default (source `default`): `speed` for
   `ghog full`, `none` for every other command.

Accepted values are `pass`, `cov` and `speed`. Any other value, `none`
included, is a setup error with exit 5 and a line naming the accepted values,
for the parameter as well as the variable: the parameter is parsed as a free
string and validated by groundhog, never through argparse choices, so it can
never exit 2. The environment is read through an injectable seam on `Deps` so
tests never touch the process environment. `ghog timings`, `ghog status`,
`ghog init` and `ghog exclude` neither accept `--full` nor read `GHOG_FULL`.

### What a level means per command

For `ghog day` the level is the walk's objective: it chooses the steps and
the verdicts. For `ghog full` it chooses the single run's shape and verdict.
For the repair commands (`check`, `affected`, `single`) the level is only the
carried objective of the loop they belong to: it never changes what they run
or measure, and it only fills their restart lines.

### Propagation

`Invocation` gains `level` and `level_source`. `run_day` passes them to each
derived step through `replace`. Every restart line that sends the LLM to a
repair command carries `--full=<level>` (for example
`ghog single tests/test_x.py --full=cov`), and every repair command's own
restart line names `ghog day --full=<level>`, so the objective travels
through the whole loop. At the internal level `none`, every such line omits
the selector, on repair commands as on `ghog day`, so `--full=none` is never
printed:

```txt
ghog day --full=cov  -> full: 2  -> "Next: ghog single a b --full=cov"
ghog single a b --full=cov  -> green -> "Next: ghog day --full=cov"

GHOG_FULL=speed ghog day -> check fails -> "... re-run ghog day --full=speed"
```

The detached walk forwards `--full=<level>` when the source was `param`, and
relies on the inherited environment otherwise, so the child resolves the same
level and the same source.

---

## Level-Shaped Full Runs for v0.13.0 full suite levels

### Run shape per level

| Level | Full-run command shape | Coverage gate | Duration verdict |
| --- | --- | --- | --- |
| `pass` | today's full command with `--no-cov`, no `--durations` | not read | none |
| `cov` | today's covered full command, no `--durations` | enforced | none |
| `speed`, sequential project | today's full command (coverage and durations) | enforced | judged on the full run |
| `speed`, parallel project, day walk | today's parallel full command, then `ghog timings` on a green full run | enforced | judged on the timing pass |
| `speed`, parallel project, direct `ghog full` | today's parallel full command only | enforced | not measured |

The sequential full run keeps its `.testmondata` reset at every level; the
parallel run keeps leaving the affected run's database alone. Dropping
`--durations` below `speed` means the floor file is not rewritten by runs
that do not judge speed.

### Verdict mapping

The verdict reuses `classify` by construction: a `pass` run measures no
coverage, so `_measures_coverage` is false and no gate is read; a `cov` run
builds no `--durations`, so `measures_durations` is false and no outlier
verdict forms. Exit codes keep their meaning: 2, 3, 4, 5, 8 and 0. In a
parallel `speed` day walk, the timing pass runs only after a full run that
exited 0, as its own timed step, and its exit code becomes the walk's. A
failure inside the timing pass keeps today's `MSG_TIMINGS_FAILED` meaning: a
real failure, fixed with `ghog single` before any duration verdict.

### Direct `ghog full`

A direct `ghog full` resolves its level with the same rule, runs the single
run of the table above, and never reads or writes the snapshot. Its `proof=`
is what that run earned:

| Level | Green result | Failing result |
| --- | --- | --- |
| `pass` | `proof=pass`, `pass` success line | `unproven` |
| `cov` | `proof=cov`, `cov` success line | `pass` on a coverage gap only, else `unproven` |
| `speed`, sequential | `proof=speed`, `speed` success line | `cov` on outliers only, `pass` on a coverage gap only, else `unproven` |
| `speed`, parallel | `proof=cov`, and a line saying durations were not measured by the parallel run, so the speed objective is not established; prove it with `ghog day --full=speed` | as the `cov` row |

The parallel direct run never prints the `speed` success line, because it
never measured durations.

---

## Snapshot Evidence for v0.13.0 full suite levels

### Marker format and write

`a.ghog.day.ok` changes from one digest line to key=value lines:

```txt
digest=<sha>
proof=<none|pass|cov|speed>
```

The marker is written to a temporary file in the same directory, then moved
over the old one with an atomic replace, so a reader sees the old or the new
marker, never a mix. A marker without both lines, with an unknown value, or
unreadable for any reason (every marker written before v0.13.0 included)
establishes no proof and reads as `unproven`.

### Proof after a walk

A walk ends by computing the valid proof for the current digest, from what
it established and what it contradicted. Each gate a walk judges maps to the
level it guards:

| Gate that failed in this invocation | Lowest contradicted level |
| --- | --- |
| check.bat or the affected tests (including a crash there) | `none` |
| full-suite test failure or suite crash, including in the timing pass | `pass` |
| coverage gate | `cov` |
| duration outliers | `speed` |

The new proof is computed in two stages:

1. the accumulated proof is the highest of the level this invocation fully
   established (reused steps count, since their proof is on the same digest)
   and the saved proof on the same digest;
2. that accumulated proof is then capped just below the lowest level any
   gate of this invocation contradicted, whenever in the walk the
   contradiction happened (`unproven` when `none` was contradicted).

The cap applies to both sources of evidence, so a level earned early in a
walk and contradicted by a later step of the same walk never survives. A
stale digest or an unreadable marker contributes no saved proof. A setup
error (exit 5), a missing pytest suite (exit 9), an interrupted or lost run
judge no gate, so they contradict nothing: the saved proof stays as it was,
since they say nothing about the sources. When the result is `unproven`, the
marker is removed.

Examples: saved `pass`, `--full=cov`, coverage gap: proof stays `pass`. Saved
`cov`, `--full=speed`, outliers: proof `cov`. Saved `pass`, `--full=cov`, a
full test failure: proof `none`, and a following `ghog day --full=pass` is no
longer a noop. Parallel `--full=speed` with no saved marker: the covered full
run passes (earning `cov`), then the timing pass fails a test or crashes:
proof `none`, so a following `ghog day --full=cov` walks again; the same with
saved `speed`: proof `none` too. Parallel `--full=speed`, green full run, then
outliers only in the timing pass: proof `cov`. `--force` at `none` with saved
`speed` and a green walk: proof stays `speed`, since no full gate was judged.
`--force --full=cov` with saved `speed` and a coverage gap: proof `pass`.

### Noop and upgrade

With valid saved proof `P` on the current digest and requested level `L`:

- `L <= P`: noop. Nothing runs; the report states that the requested
  objective is met by saved evidence at `P`, and that no check ran;
- `L > P`: upgrade. check.bat and the affected step are reused (their step
  headers say `reused from snapshot`), and only the full step, plus the
  timing pass at `speed` in a parallel project, runs at `L`.

A digest mismatch, `unproven`, or `--force` walks the whole chain.

---

## Walk Reporting for v0.13.0 full suite levels

### Closing line keys

The day walk's closing line keeps every current key and appends four:

- `full=<none|pass|cov|speed>`: the selected objective;
- `src=<param|env|default>`: where it came from;
- `proof=<none|pass|cov|speed|unproven>`: the valid proof after this walk,
  per the snapshot rules;
- `reused=<none|check+affected|all>`: what this invocation took from the
  snapshot instead of running (`all` on a noop).

A direct `ghog full` appends `full=`, `src=` and `proof=` (its earned proof).
The keys are appended, never inserted, so a reader that matches the current
keys by name keeps working; the groundhog tests that assert the closing line
are updated, and no other tool parses it.

### Status evidence

`a.ghog.status` keeps its label and `state=` grammar and gains the same keys.
The running line carries `full=`, `src=` and `proof=pending`; the done line
carries `full=`, `src=`, `proof=`, `reused=` and `exit=`. `ghog status`
replays the done line as today, so a detached walk's completion reports the
same evidence as a foreground one.

### Closing instructions and restart lines

Every restart line is rendered from the carried level by one helper:
`ghog day --full=<level>`, or plain `ghog day` at `none`. Repair commands
that the report sends the LLM to receive `--full=<level>` the same way. The
fixed restart strings of `reporting_nextstep.py` become templates filled by
that helper, which covers check, affected, `ghog single`, coverage-gap,
outlier and timing-failure paths. Success lines become one line per level:

| Level | Success line content |
| --- | --- |
| `none` | full suite skipped on purpose (no level requested); check.bat and the affected tests are green; do not run the full suite unless the calling instruction asks for a level: `ghog day --full=pass`, `ghog day --full=cov`, or `ghog day --full=speed`; carry on with the calling instruction |
| `pass` | objective met at `pass`; coverage and duration gates are not required by this objective; carry on with the calling instruction |
| `cov` | objective met at `cov`; the duration gate is not required by this objective; carry on with the calling instruction |
| `speed` | objective met at `speed`; no unaccepted duration outlier remains under the configured exclusions; carry on with the calling instruction |

Inside a walk, the green affected step no longer prints `Next: ghog full`;
at `none` the walk's success line replaces it, and at a level the walk simply
proceeds. A standalone `ghog affected --no-cov` with no carried level keeps
its current line. The noop line states the requested level, the saved proof
level, and that no check ran in this invocation. The outlier line at `speed`
keeps the `fix_slow_test.md` procedure and the `ghog exclude` hint, and
states that an exclusion is accepted only after an attempted improvement.

---

## Requestor Validation at Speed for v0.13.0 full suite levels

### Default validation command

`DEFAULT_PROJECT_VALIDATION_COMMANDS` becomes `("ghog day --full=speed",)`.
The requestor already runs its resolved validation set green before every
`publish-request`, round 1 and each replacement round, so this one change
makes every request under the default policy enter review with `speed`
evidence. A replacement round whose changes leave the snapshot proof valid
reuses it (noop or upgrade), and pays a full `speed` walk only when its
changes invalidated that proof. The requestor follows the walk's restart and
repair lines while repairing, preserving assertions and coverage; every
change it makes to reach `speed` is part of the work the reviewer assesses in
that round.

### Duration exclusions in the request

When the requestor accepts a genuinely slow call with `ghog exclude` during
that validation, after an attempted improvement, its implementation report
names each excluded call, its measured time, the attempted improvement, and
the reason. The exclusion itself lives in the ignored `a.ghog.outliers` of the
artifact home, which the reviewer can read on the same machine; the report is
what makes it visible in the request and the transcript. The reviewer judges
it like any other change of the round.

### Declared validation sets

A project with a `.review-validation` file keeps its declared commands. When
the request renderer resolves a declared `ghog day` that carries no `--full`,
it adds a migration notice to the rendered validation section: plain
`ghog day` now proves only check.bat and the affected tests, and the project
should declare `ghog day --full=speed` to keep a full-suite proof before
review. The notice states only that fact about that command; it makes no
claim about other declared commands, `GHOG_FULL`, or saved proof, any of which
can still establish `speed`. The workflow adds no validation of its own.

### Nothing at the commit-ready answer

The requestor's convergence path is unchanged: at a commit-ready answer it
presents the human gate, runs no `speed` walk, and starts no round. The
exchange core needs no new transition.

---

## Review-Off Speed Pass for v0.13.0 full suite levels

### Placement in the step chain

The step chain is implement, check, after-check, group-commits, `a.commit`,
then the review-mode sample. With review mode off, the ordinary commit gate
follows that sample. The `speed` pass runs right there, before the menu is
presented: the step has passed implementation-check, and every change of the
step is staged by the `git add -A` variant of `group-commits-msg`.

### Change detection

Before the pass, the implementing agent stages every change (`git add -A`) and records
the index tree with `git write-tree`. It runs `ghog day --full=speed`,
following restart and repair lines until exit 0. After the green walk, it
stages again and records the tree once more:

- same tree: the pass changed nothing; the commit menu is presented as today;
- different tree: the pass changed tests, production code, or both; the step
  goes back through implementation-check (`pw handoff check <x>`), then the
  rest of the chain, and reaches this pass again, where the walk is a noop or
  an upgrade when the proof is still valid.

A duration exclusion changes no tracked file, so it never changes the tree;
the agent lists it, with its measured time, attempt and reason, in the
commit-gate summary instead. No test-only exemption and no review exchange
exist on this path.

---

## Workflow Instructions for v0.13.0 full suite levels

- `implement-step.md`, `implement-missing-step.md`, `split-large-file.md`,
  and the plan command of `write-plans.md` keep plain `ghog day`, and their
  wording describes check plus affected tests instead of a full coverage pass.
- `implement-step.md`'s review-off branch gains the `speed` pass and its
  tree comparison before the commit menu.
- `groundhog.md` states that the loop always follows the restart and repair
  lines the report prints, which carry the level, and that the loop's
  objective is the level it started with; exit 8 appears only at `speed`.
- `fix_slow_test.md` applies to `speed` walks and restarts with
  `ghog day --full=speed`.
- `code-review-requestor.md` names the `speed` validation before every
  request, the exclusion evidence in the implementation report, the migration
  notice, and the absence of any walk at the commit-ready answer.
- `prepare-release.md` and both operation strings of
  `prepare_release_plan_workflow.py` name `ghog day --full=cov`.
- `bin/ghog_cycle.bat` keeps sharing one activation; its no-argument default
  becomes `day` alone (Q02).
- `GROUNDHOG.md` and `tools/Pytest reset specs.md` document levels, the
  resolution rule, the marker format and invalidation, the closing and status
  keys, the success and restart lines, the parallel timing step, and the
  `.review-validation` migration note, as new decision rows and acceptance
  tests.

---

## Acceptance Cases for v0.13.0 full suite levels

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| `ghog day`, `GHOG_FULL` unset, all green | check and affected run, no full run, skip success line, `full=none src=default proof=none` | default walk |
| `GHOG_FULL=cov`, `ghog day` | full run with coverage gate, restart lines `ghog day --full=cov`, `src=env` | environment selection, explicit restart |
| `GHOG_FULL=speed`, `ghog_cycle.bat` with no argument | one `speed` day walk, timing pass inside it in a parallel project | cycle follows the level rule |
| `GHOG_FULL=cov`, `ghog full --full=pass` | single run at `pass`, `src=param proof=pass` | parameter wins |
| `GHOG_FULL=fast`, `ghog day` | exit 5 naming `pass`, `cov`, `speed` | invalid variable |
| `ghog day --full=fast` or `--full=none` | exit 5, never argparse exit 2 | invalid or reserved parameter |
| `GHOG_FULL=fast`, `ghog day --full=cov` | walk runs at `cov`, `src=param` | valid parameter overrides invalid variable |
| `--full=pass`, a coverage gap and slow calls | exit 0, `pass` success line, no covg or slow-test line | not judged below their level |
| `--full=cov`, parallel project, green | no timing pass, `cov` success line | speed not required |
| `--full=speed`, parallel day walk, outlier in timings | exit 8 with the outlier line and `ghog day --full=speed` | timing pass owns speed |
| direct `ghog full`, parallel project, green | exit 0, `proof=cov`, line saying speed was not measured | no false speed claim |
| direct `ghog full --full=pass`, test failure | exit 2, `proof=unproven`, `ghog single ... --full=pass` | earned proof per outcome |
| `--full=cov` full fails, then `ghog single` green | single prints `Next: ghog day --full=cov` | objective survives the loop |
| `GHOG_FULL=speed`, check fails | restart line `ghog day --full=speed` | env objective restarted explicitly |
| default walk fails in the affected step | today's fix line, restart with plain `ghog day`, `proof=unproven` | no invented level |
| saved `speed`, unchanged sources, `ghog day` | noop, `full=none proof=speed reused=all`, no check ran | lower request, stronger proof |
| saved `none`, unchanged sources, `--full=cov` | check and affected reused, full run only, `reused=check+affected` | level upgrade |
| saved `pass`, `--full=cov`, coverage gap | exit 3, `proof=pass` kept | higher-gate-only failure |
| saved `pass`, `--full=cov`, full test failure | exit 2, `proof=none`; next `--full=pass` walks again | contradicted lower proof |
| parallel `--full=speed`, no marker, green full run, timing pass fails a test | exit 2, `proof=none`; next `--full=cov` walks again | later contradiction caps earned proof |
| parallel `--full=speed`, no marker, green full run, timing pass crashes | exit 4, `proof=none`; next `--full=pass` walks again | crash contradicts `pass` |
| parallel `--full=speed`, saved `speed`, timing pass fails a test | exit 2, `proof=none` | cap applies to saved proof too |
| parallel `--full=speed`, green full run, outliers only in timings | exit 8, `proof=cov` | outlier-only failure keeps `cov` |
| legacy one-line marker, unchanged sources, `ghog day` | whole default walk runs, marker rewritten with `proof=none` | no established level |
| `--detach --full=cov` | survivor runs at `cov`; `ghog status` shows `full=cov src=param proof=pending`, then the done line with `proof=` and `reused=` | detached keeps level and evidence |
| review mode on, default policy, round 1 | request published only after a green `speed` walk | speed before review |
| review mode on, replacement round changed no Python file | `speed` validation is a noop on the saved proof, request published | snapshot reuse |
| review mode on, replacement round changed Python code | `speed` walk runs before the replacement request | every request validated |
| requestor needs `ghog exclude` to reach `speed` | request's implementation report lists the call, measured time, attempt and reason | exclusion reviewed |
| commit-ready answer | human gate presented, no `speed` walk, no new round | nothing at convergence |
| `.review-validation` declares plain `ghog day` | accepted, migration notice in the rendered validation section, no workflow-added walk | project authority kept |
| review mode off, `speed` pass changes nothing | tree unchanged, commit menu presented | no change, no recheck |
| review mode off, `speed` pass changes a test or production file | tree differs, step goes back through implementation-check, then the pass again | every speed change checked |
| review mode off, `speed` pass needs only `ghog exclude` | tree unchanged, commit menu with the exclusion listed | ignored file, disclosed |

## Open questions for the v0.13.0 full suite levels design

### Q01: How `speed` is proven in a parallel project

Question description: a project with `.ghog-parallel` runs its full suite on xdist workers without `--durations`, and the sequential `ghog timings` pass owns the duration verdict. No instruction runs `ghog timings` today, so no workflow judges speed in llm-shared. The design adds the timing pass as an extra step of a `speed` day walk, after a green full run. The question is where the timing pass belongs.

#### BBQ for Q01

The kitchen cooks every dish on several stoves at once to finish faster, but a stopwatch on a crowded kitchen measures the queue, not the cook. The chef can time each dish afterwards on one quiet stove, cook the whole service on one stove when timing matters, or leave timing to whoever remembers.

In this picture: the several stoves are the xdist workers, the quiet stove is the sequential `ghog timings` pass, cooking on one stove is a sequential full run with `--durations`, and whoever remembers is today's `ghog_cycle.bat` default.

#### Options for Q01

- Option A: a `speed` day walk in a parallel project runs the parallel full run with coverage, then `ghog timings` as its own timed step on a green full run; a direct `ghog full` keeps its current single run.
  - pro: keeps the fast parallel run for failures and coverage, and times calls without contention;
  - pro: `speed` day walks mean the same thing in every project.
  - con: the suite runs twice at `speed` in a parallel project.
- Option B: a `speed` walk forces a sequential full run with coverage and `--durations`, ignoring `.ghog-parallel`.
  - pro: one run, one verdict.
  - con: covered call times are inflated by instrumentation, which is why `ghog timings` runs uncovered; and it loses the parallel speed-up at the one level where the suite is already the long part.
- Option C: also make a direct `ghog full --full=speed` add the timing pass.
  - pro: `ghog full` and `ghog day` agree on what `speed` runs.
  - con: changes the settled behavior of a plain direct `ghog full`.

#### Recommended option for Q01 (with arguments for this choice)

Option A: A and C both keep the duration verdict uncontended and uncovered; A is chosen because it respects the settled compatibility boundary of a direct `ghog full`, which keeps its single run. The day walk is the command the workflow phases call, so placing the timing pass there covers every workflow `speed` walk. A direct parallel `ghog full --full=speed` reports `proof=cov` and says speed was not measured, instead of claiming the speed objective.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: it gives a `speed` day walk a real duration verdict in parallel projects without weakening the timing measure, and it leaves a plain direct `ghog full` unchanged while reporting honestly what that run did not measure.

### Q02: Default sequence of `ghog_cycle.bat`

Question description: `bin/ghog_cycle.bat` runs `day` then `timings` when called with no argument. With Q01, a `speed` walk already runs the timing pass in a parallel project, and a default walk runs no full suite at all. The cycle default would then run timings after a walk that never ran the full suite, or run it twice after a `speed` walk.

#### BBQ for Q02

A shortcut button on the oven runs "cook, then time". Now the cook step itself times the dish when asked, and the everyday cook step does not cook the whole menu. Pressing the old button either times a dish nobody cooked or times it twice.

In this picture: the shortcut button is the no-argument `ghog_cycle.bat`, "cook, then time" is `day` then `timings`, and the cook step that times when asked is a `speed` day walk.

#### Options for Q02

- Option A: the no-argument cycle runs `day` only; the level comes from `GHOG_FULL` as for any walk, and explicit sequences are unchanged.
  - pro: no duplicate or meaningless timing pass;
  - pro: the cycle follows the same level rule as every other caller.
  - con: a human used to the default gets no timing pass unless `GHOG_FULL=speed` is set.
- Option B: keep `day` then `timings`.
  - pro: no change for existing habits.
  - con: times an untested suite after a default walk, and times twice after a `speed` walk.
- Option C: run `timings` after `day` only when the resolved level is below `speed`.
  - pro: keeps a timing pass for humans by default.
  - con: the batch file must resolve the level itself, duplicating the CLI rule.

#### Recommended option for Q02 (with arguments for this choice)

Option A: once the walk owns the timing pass, the cycle only needs to share one activation; its default should not bring back the behavior the levels remove.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: the cycle becomes a pure activation-sharing wrapper whose default follows the level rule, with no duplicated or orphaned timing pass.

### Q03: Durations below `speed` in a sequential project

Question description: a sequential full run carries `--durations` today and rewrites the floor lines of `a.ghog.outliers` on every green run. The design drops `--durations` at `pass` and `cov`, so only `speed` walks feed the floor. The feature request allowed informational durations at lower levels.

#### BBQ for Q03

The bakery records how long each loaf took, and uses the median to set the "too slow" line. If every quick practice bake also writes to that log, the line moves with bakes nobody judged.

In this picture: the log is the floor lines of `a.ghog.outliers`, practice bakes are `pass` and `cov` full runs, and the "too slow" line is the auto floor.

#### Options for Q03

- Option A: no `--durations` below `speed`; the floor is only rewritten by walks that judge speed.
  - pro: the floor file stays a record of speed walks only;
  - pro: a slightly shorter command, and no timing output nobody acts on.
  - con: no informational durations at `pass` or `cov`.
- Option B: keep `--durations` and print informational durations below `speed`, without rewriting the floor.
  - pro: timings stay visible during development.
  - con: output nobody acts on, and a second path through the duration code that only reports.
- Option C: keep today's behavior (durations measured and floor rewritten) and only skip the verdict.
  - pro: smallest change.
  - con: the floor drifts with runs that were never judged.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the levels exist to keep speed work out of development; measuring and reporting durations there invites exactly that work, and rewriting the floor from unjudged runs makes the `speed` verdict less stable.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it keeps the floor file honest and the lower levels quiet about speed, as the feature request allows but does not require.

### Q04: Marker format and the default walk's proof

Question description: `a.ghog.day.ok` holds one digest line today, written in place. The design writes `digest=` and `proof=` key=value lines through a temporary file and an atomic replace, and writes a marker after a green default walk too (`proof=none`), so the development noop keeps working and a later upgrade can reuse check and affected. Which proof survives a failing walk is Q08.

#### BBQ for Q04

The inspection sticker used to carry one stamp. The new sticker needs to say which inspection was passed, including the quick one, or the quick daily check could never be skipped on an unchanged car.

In this picture: the sticker is `a.ghog.day.ok`, the stamp is the digest, the inspection level is `proof=`, and the quick daily check is the default walk.

#### Options for Q04

- Option A: key=value lines (`digest=`, `proof=`), written by every green walk including the default one, through a temporary file and an atomic replace; any unreadable or incomplete marker reads as `unproven`.
  - pro: same grammar as the closing and status lines, readable by eye;
  - pro: keeps the noop for repeated development walks and allows upgrade reuse.
  - con: a new parser for the marker.
- Option B: JSON marker.
  - pro: extensible.
  - con: a second grammar in groundhog files for two values.
- Option C: keep the digest line and write the proof in a second marker file.
  - pro: the digest reader does not change.
  - con: two files can disagree, and a partial write leaves a digest with a stale proof.

#### Recommended option for Q04 (with arguments for this choice)

Option A: one file, one grammar already used by groundhog, and the default walk's marker is what keeps development loops cheap.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: it records the proof with its digest in one file replaced atomically, in the grammar groundhog already uses, keeps the noop for default walks, and reads any damaged marker in the safe direction.

### Q05: Evidence keys on the closing line

Question description: the design appends `full=`, `src=`, `proof=` and `reused=` to the day walk's closing line (and `full=`, `src=`, `proof=` to a direct `ghog full`, where `proof=` is what that single run earned). `proof=` takes `none|pass|cov|speed` or `unproven` (no valid evidence), so a successful default walk (`none`) is never confused with a failed or stale one. `a.ghog.status` carries the same keys, with `proof=pending` while running. The closing line already carries seven keys and is the line an LLM reads first.

#### BBQ for Q05

The receipt already lists the total and the payment. Adding what was ordered, who ordered it, and what came from the fridge instead of the stove can go on the same line, on a second line, or on a separate slip.

In this picture: the receipt line is the closing line, what was ordered is `full=`, who ordered it is `src=`, the fridge is the snapshot proof reused, and the separate slip is a new evidence line.

#### Options for Q05

- Option A: append the four keys to the existing closing line.
  - pro: one line holds the whole verdict, and the LLM tail read already includes it;
  - pro: appended keys leave existing key lookups working.
  - con: a longer line.
- Option B: a separate `evidence:` line just before the closing line.
  - pro: the closing line keeps its current shape.
  - con: two lines to read for one verdict, and a tail read may split them.
- Option C: move all keys into a structured JSON closing line.
  - pro: machine-friendly.
  - con: breaks the established key=value grammar and every current reader.

#### Recommended option for Q05 (with arguments for this choice)

Option A: the closing line is already the contract every caller branches on; appending keeps it the single place to read, and no tool outside groundhog parses it.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: it keeps one verdict line, compatible with key-based readers, and puts the new evidence where the LLM already looks; the same keys in `a.ghog.status` give a detached walk's completion the same evidence as a foreground one.

### Q06: How a detached walk keeps its level and source

Question description: `_detached_day_command` rebuilds the child command line. The design forwards `--full` only when the level came from the parameter, and relies on the inherited environment for `GHOG_FULL`, so the child reports the same `src=`.

#### BBQ for Q06

A courier carries an order to another kitchen. The order either travels written on the ticket, or the second kitchen reads the same wall dial as the first. Writing the dial's value on the ticket makes the order look customer-written.

In this picture: the courier is the detached spawn, the ticket is the child command line, the wall dial is `GHOG_FULL`, and "customer-written" is `src=param`.

#### Options for Q06

- Option A: forward `--full` only for a `param` source; the child inherits the environment for `env`.
  - pro: the child resolves the same level and the same source;
  - pro: no hidden option.
  - con: relies on the survivor spawn inheriting the environment.
- Option B: always forward the resolved level as `--full`.
  - pro: the child level never depends on the environment.
  - con: `src=` becomes `param` for a walk the human selected through `GHOG_FULL`.
- Option C: forward the level and a hidden `--full-source` option.
  - pro: exact level and source, independent of the environment.
  - con: a hidden CLI option only the detach path uses.

#### Recommended option for Q06 (with arguments for this choice)

Option A: the survivor spawn already inherits the environment (it relies on it for the project `PATH` and venv), so the same resolution rule gives the same answer with no extra option.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: the detached child applies the one resolution rule to the same inputs, so level and source match the launching walk, including an explicit parameter overriding an invalid environment value; its running and done lines in `a.ghog.status` carry the same evidence keys as a foreground walk.

### Q07: Scope of the level-aware restart helper

Question description: the design renders every restart line through one helper from the walk's level. Some next-step lines live outside a walk: `ghog single` green or failing after a leveled full run, `ghog check`, and a standalone covered `ghog affected` in the coverage branch. Those runs are not walks, so they carry no level of their own. In the design, the carried level never changes what these commands run or measure; it only fills their restart lines.

#### BBQ for Q07

A cook fixing one dish at a side counter must be told which service to rejoin. If the side-counter ticket does not say, the cook rejoins the everyday service by default and the gala dinner loses its table.

In this picture: the side counter is `ghog single` or a covered `ghog affected`, the service is the walk's level, and the ticket is the restart line printed by that side run.

#### Options for Q07

- Option A: repair commands (`check`, `affected`, `single`) resolve a carried level with the same rule as `ghog day` (`--full`, then `GHOG_FULL`, else none), and every line that sends the LLM to them passes `--full=<level>` along; the carried level fills restart lines only.
  - pro: the level survives the whole fix loop, even through side runs;
  - pro: one rule for every command that prints a restart line.
  - con: `ghog single` and `ghog affected` accept an option they only use for the restart line.
- Option B: side runs always print plain `ghog day`, and `groundhog.md` tells the LLM to add the level it started with.
  - pro: no option on side runs.
  - con: relies on the LLM remembering the level, which is exactly what the restart rule was meant to avoid.
- Option C: side runs read the last walk's level from `a.ghog.status`.
  - pro: no option to pass.
  - con: hidden coupling to a lifecycle file, and wrong when a human ran another walk in between.

#### Recommended option for Q07 (with arguments for this choice)

Option A: the feature request requires every printed restart line to carry the level so an LLM following it literally never drops back; passing the level through the side runs is the only way their printed lines can do that.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: the level travels with every command of the loop, so every restart line printed anywhere in it names the level the loop is proving.

### Q08: Which saved proof survives a failing walk

Question description: today a failing walk leaves the old marker untouched. With levels, a later result can contradict saved proof: a saved `pass` followed by an upgrading `cov` walk whose full run fails a test cannot still make the next `pass` walk a noop. A failure confined to a newly requested higher gate, on the other hand, leaves lower proof intact. The design maps each failed gate to the lowest level it contradicts, accumulates the higher of the level this walk established and the saved proof, then caps that accumulated proof below the lowest contradicted level, so a level earned early in a walk and contradicted later in the same walk never survives; setup errors, missing suites and interrupted or lost runs judge no gate and contradict nothing.

#### BBQ for Q08

The car had a valid lights certificate. The owner asks for a brake test, and the car fails on the brakes: the lights certificate still holds. If the car fails on the lights during the brake test, keeping the old lights certificate would be a lie. If the test centre loses power, nothing was learned about the car.

In this picture: the lights certificate is a lower saved proof, the brake test is an upgrade to a higher level, failing on the brakes is a failure of the new gate only, failing on the lights is a failure that contradicts the saved proof, and the power cut is a setup error or a lost run.

#### Options for Q08

- Option A: keep proof, saved or earned in this walk, only when no result of this walk contradicts it; a failed gate caps the accumulated proof below the level it guards; runs that judge no gate keep the saved proof.
  - pro: keeps legitimate upgrade reuse and never lets a noop rest on contradicted evidence;
  - pro: one small mapping from failed gate to level.
  - con: the rules must be tested per gate and per outcome.
- Option B: keep every saved marker on failure, as today.
  - pro: simplest.
  - con: a lower-level walk can noop right after the same gate just failed.
- Option C: remove the marker after any failed walk.
  - pro: conservative and simple.
  - con: throws away valid lower proof on a failure confined to the newly requested gate, making every failed upgrade re-run check and affected.

#### Recommended option for Q08 (with arguments for this choice)

Option A: the snapshot exists to skip work that is still proven; keeping exactly the uncontradicted part of the proof is what makes both the noop and the upgrade reuse trustworthy. Option C remains an acceptable conservative fallback if the mapping proves hard to maintain.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: every saved proof then holds only while no newer result on the same sources contradicts it, which covers failed upgrades, `--force`, stale digests and unreadable markers with one rule.

### Q09: How the review-off speed pass detects that it changed the step

Question description: with review mode off, the `speed` pass runs after `a.commit` is ready and before the commit menu. If it changed anything, the step must go back through implementation-check (feature-request gap 15). The design stages everything and compares `git write-tree` before and after the green walk. Other signals exist.

#### BBQ for Q09

After the quality check, the baker times the loaf and sometimes tweaks the recipe to make it bake faster. Before the loaf ships, someone must know whether the recipe card changed. They can photograph the card before and after, trust the baker to say so, or only look at whether the oven settings changed.

In this picture: the recipe card is the staged tree, the two photographs are the `git write-tree` ids before and after the walk, the baker's own account is the agent's report, and the oven settings are the snapshot digest.

#### Options for Q09

- Option A: stage everything and record `git write-tree` before the pass, stage again after the green walk, and compare the two tree ids.
  - pro: exact and cheap, covering tests, production code, Markdown and new or deleted files alike;
  - pro: needs no new tool, only two Git commands the instruction runs.
  - con: any change, even a comment, sends the step back through implementation-check.
- Option B: compare the snapshot digest of `a.ghog.day.ok` before and after.
  - pro: already computed by groundhog.
  - con: the digest covers Python files and gate configuration only, so a changed data file or non-Python fixture would go unnoticed.
- Option C: rely on the agent stating whether it changed anything.
  - pro: no machinery.
  - con: not verifiable, and easy to forget in a long repair loop.

#### Recommended option for Q09 (with arguments for this choice)

Option A: the question is only "did the tree change", and two tree ids answer it exactly for every kind of file; a change that is only cosmetic costs one implementation check, which is cheap next to an unchecked production change.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: comparing the staged tree before and after the green walk tells the agent, exactly and verifiably, whether the step must go back through implementation-check.

### Q10: How duration exclusions reach the reviewer

Question description: the requestor may accept a genuinely slow call with `ghog exclude` while validating at `speed`, and the reviewer must judge it (feature-request gap 14). The exclusion lives in the ignored `a.ghog.outliers`, so it appears in no diff. The design has the requestor's implementation report name each excluded call, its measured time, the attempted improvement and the reason.

#### BBQ for Q10

A runner got a medical exemption from the time limit. The exemption is written in the marshal's private notebook, not on the results board. The race committee only sees the board, unless the marshal copies the exemption onto the report they send, or the committee is handed the notebook itself.

In this picture: the private notebook is the ignored `a.ghog.outliers`, the results board is the diff, the marshal's report is the implementation report of the request, and handing over the notebook is the renderer reading the exclusion file.

#### Options for Q10

- Option A: the requestor's implementation report lists each exclusion made for this round, with measured time, attempt and reason; the reviewer can check it against `a.ghog.outliers`.
  - pro: no tool change: the implementation report already carries the requestor's evidence;
  - pro: the reason and attempt, which no file records, are written by the one who knows them.
  - con: relies on the requestor to list every exclusion.
- Option B: the request renderer reads the `[exclusion]` section of `a.ghog.outliers` and lists the entries added since the last request.
  - pro: no exclusion can be forgotten.
  - con: the renderer needs to know which entries are new, and still cannot supply the attempt and reason.
- Option C: both: the renderer lists the current exclusions, and the report explains the new ones.
  - pro: complete and explained.
  - con: a renderer change and duplicated information for a rare event.

#### Recommended option for Q10 (with arguments for this choice)

Option A: exclusions are rare and need an explanation only the requestor has; the implementation report is where that explanation already belongs, and the reviewer can verify it on disk.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: the exclusion reaches the reviewer with its reason and attempt in the request's own implementation report, without a renderer change for a rare case.

### Q11: Where the `.review-validation` migration notice is produced

Question description: a declared validation set that holds `ghog day` without `--full` must trigger a migration notice on every request (feature-request gap 12). The design produces it in the request renderer's validation section. The notice could come from elsewhere.

#### BBQ for Q11

The restaurant's own checklist says "cook the dish", which no longer includes timing. The warning can be printed on every order ticket, taped once to the kitchen wall, or left to the chef's memory.

In this picture: the checklist is `.review-validation`, every order ticket is every rendered review request, the kitchen wall is a one-time warning when the file is loaded, and the chef's memory is the requestor instruction alone.

#### Options for Q11

- Option A: the request renderer adds the notice to the rendered validation section whenever the resolved set holds a declared `ghog day` without `--full`.
  - pro: the notice is in every request and transcript, visible to requestor, reviewer and human;
  - pro: produced by code from the resolved set, so it cannot be forgotten.
  - con: repeated on every request until the project edits its file.
- Option B: `load_project_validation_commands` logs a warning when it reads such a declaration.
  - pro: one place, no rendering change.
  - con: a log line is easy to miss and never reaches the reviewer or the transcript.
- Option C: the requestor instruction tells the agent to mention it.
  - pro: no code change.
  - con: depends on the agent remembering, on every request.

#### Recommended option for Q11 (with arguments for this choice)

Option A: the feature request asks for the notice on every request; only the renderer, which builds every request from the resolved set, can guarantee that.

#### Answer to Q11: option A (with reason why it must be accepted as the answer)

Option A: the renderer puts the notice in every request built from a weakened declaration, so it reaches every reader of the exchange without relying on memory.
