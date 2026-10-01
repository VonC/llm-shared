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
The requirement then gained test groups and their activation (gaps 18 to 25,
clarifications Q15 to Q26): an effort can narrow its walks, its coverage gate
and its proof to a declared group, and only prepare-release then runs the
whole suite. This revision adds them.

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
4. A versioned `.ghog-groups` declaration and a scope selector (`--group`,
   `--whole-suite`, `GHOG_GROUP`) narrow every leveled run, its coverage gate
   and its proof to one test group, and the workflow carries each effort's
   declared scope, read from its requirement, into every ghog command it
   owns, with prepare-release always on the whole suite.

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
- The review-less `speed` pass, its staged-tree and exclusion comparisons
  (`ghog exclude --list`), and its return path through implementation-check.
- The `.ghog-groups` declaration, its gitignore-style matching, its
  validation, and a `ghog groups` listing.
- Scope resolution, errors and propagation beside the level; captured
  scopes (`--scope-file`) for detached walks and reviewer evidence;
  group-scoped full, timing and affected runs; group coverage collection and
  gate; duration judging in a group without rewriting the floor file.
- One snapshot marker per scope, carrying scope and timing fingerprints.
- The effort scope: the `Test group:` line, its recording when a draft is
  processed, its resolution and display by `pw`, scope-carrying workflow
  commands and request evidence, the bound scope the review exchange keeps
  for a published round, and scope changes at eligible boundaries.
- Instruction, manual, specification and test updates for the above.

### Deferred from v0.13.0 full suite levels to v0.14.0 and beyond

- Making `ghog timings` part of a direct `ghog full` call in parallel
  projects: a direct call keeps its single-run shape (feature-request gap 9).
- Extending the snapshot digest beyond Python files and gate configuration
  (Markdown and other non-Python changes still do not invalidate it).
- Narrowing the snapshot digest to a group's own files: a change to any
  Python file of the project still invalidates the proof of every scope.
- One timing floor per group, and any automatic whole-suite `speed` run that
  seeds the floor for groups (both rejected by the feature request's Q19).
- Any change to the reviewer side beyond the captured scope on its
  `ghog affected --no-cov`: the code reviewer and implementation-check still
  never run `ghog day` or `ghog full`.
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
Each entry is `<node id> = <recorded seconds>`, and `ghog exclude` sets or
replaces one entry (`cli.run_exclude`).

**Runs that measure durations rewrite the floor file**: `durations_summary`
rewrites line 1 of `a.ghog.outliers` (the auto floor, a write-only record the
gate never reads), keeps line 2 (the gate floor, default one second), and
rewrites the `[exclusion]` section: a baseline is lowered after an improvement
of more than two seconds, a stale, below-floor or fast-again entry is
removed, and a baseline is never raised (`durations.apply_exclusions`). A
node absent from the run counts as stale. The tolerant reader
`exclusions.read_exclusions` reads a missing, unreadable or malformed file as
no exclusions.

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

**The coverage verdict comes from one parsed line over a project-wide
measure**: llm-shared's pytest `addopts` carry `--cov=tools` and
`--cov-fail-under=100`, and `[tool.coverage.run]` declares
`source = ["tools"]` with an `omit` list (thin wrappers, `__init__.py`,
protocols). `commands.classify` judges the gate from the `TOTAL` percentage
parsed out of pytest-cov's term-missing report (`RunStats.cov_percent`)
against `gate.read_coverage_gate`; pytest's exit 1 from `--cov-fail-under`
plays no part, since failures come from the parsed failed count. A group's
coverage figure therefore cannot come from that line.

**The pytest commands name no test paths**: `runner.pytest_command` builds
the `full`, `affected` and `timings` commands without positional paths, so
pytest collects from the configured `testpaths`; only `single` passes files.
Positional paths are where a group can narrow collection.

**An empty run is a setup error except for affected**:
`commands._classify_no_tests` maps a `full` or `single` run that collected
nothing to exit 5, and an `affected` run with nothing affected to a green
step.

**The outlier rule has two conditions**: `durations.summarize` flags a call
at or above the active floor and far out by a modified z-score computed over
the run's own calls (median and MAD), and falls back to the floor alone when
the MAD collapses to zero.

**A full run rewrites the failure baseline**: `run_tests` writes the failing
node ids of every non-crashed full run to `a.ghog.failures`, which
`ghog single` reads to compare focus results with the last full run.

**The interpreter allows a stdlib glob matcher**: the llm-shared venv runs
Python 3.13 (`requires-python = ">=3.13, <3.14"`), whose `glob.translate`
turns recursive `**` globs into regular expressions; no `pathspec` package is
installed.

**No group concept exists yet**: no `.ghog-groups` file, `GHOG_GROUP`
variable or `--group` option appears in code, launchers or tests.

**pw reads no header line from a requirement**: `steps.compute_state`
locates the requirement through `document_lookup.select_document` (role
`requirement` covers `feature-request` and `issue` documents) and exposes it
as `WorkflowState.requirement`; from its content pw only tests for open
questions and consolidated decisions. The one metadata line pw parses,
`- Umbrella: <path>`, comes from the draft, in three separate readers
(`prompt_workflow_progress`, `prompt_workflow_code_review`,
`prompt_workflow_review`).

**pw prints no ghog command today**: no `tools/prompt_workflow*.py` module
and no step definition contains a ghog command. Ghog commands come from
instructions and templates (`write-plans.template.md` "Ready-to-run command
templates", the step-handoff "Last gate" line), from
`code_review_validation.DEFAULT_PROJECT_VALIDATION_COMMANDS`, and from the
two prepare-release operation strings.

**The request renderer resolves the validation set in code**:
`code_review_request._render_from_arguments` calls
`resolve_code_review_validation(load_project_validation_commands(root), ...)`
and renders the result as the `resolved_validation_set` of the request's
"Code review evidence" JSON, one `- <command> (sources: ...)` line each.

**`pw progress` already holds the requirement path**:
`prompt_workflow_progress._topic_lines` prints `branch`, `topic`, `umbrella`,
`phase`, `step` and `journal`, after calling `steps.compute_state`, so
`state.requirement` is at hand there; `review_lines` and the `next` line
follow.

**Draft metadata is a dash line near the top**: `process-draft.md` records
`- Type: ...` and, for an umbrella child, `- Umbrella: <path>` near the top of
the draft, and asks its setup menus one at a time (title, slug, version,
documentation layout, branch layout). `write-requirement.md` and its
template write no metadata line into the requirement.

**Reviewer-side commands are fixed**: `code-reviewer.md` lets the reviewer
run `ghog check` and `ghog affected --no-cov` at most once each per round,
never `ghog day` or `ghog full`; `implementation-check.md` gives a reviewer
check the same two commands, and a writer-side check runs none.

**The code-review gate labels are fixed**: `code-review-requestor.md` passes
`--another-round-label "Rework and review again"` and
`--continue-owning-workflow-label "Commit"`, and shows both at a
commit-ready answer.

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
scope = one explicit selector (--group=G | --whole-suite | --scope-file=capture)
        else GHOG_GROUP else whole suite; invalid or unusable -> exit 5
ghog day (level L, scope S)
  valid saved proof P of scope S on the same digest:
    P >= L                -> noop, "met by saved proof P, nothing ran"
    none <= P < L         -> reuse check + affected, run the full step(s) at L
  otherwise               -> check, affected --no-cov inside S, then:
    L = none   -> stop: "full suite skipped on purpose ... carry on"
    L = pass   -> full --no-cov over S (no durations)
    L = cov    -> full over S with coverage gate (group: 100% of G's sources)
    L = speed  -> sequential: full over S with coverage + durations
                  parallel:   full over S with coverage, then timings over S
                  group: durations judged on the saved floor, file untouched
  every restart line -> "ghog day --full=L <S selector>" (no --full at none)
  end -> marker of S: proof = highest level still valid (see invalidation);
         closing line and a.ghog.status: full=L src=... proof=... reused=...
         scope=S
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
`ghog init`, `ghog exclude` and `ghog groups` neither accept `--full` nor
read `GHOG_FULL`.

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
the level selector, on repair commands as on `ghog day`, so `--full=none` is
never printed. Every line also carries the scope selector (see "Scope
propagation"):

```txt
ghog day --full=cov  -> full: 2  -> "Next: ghog single a b --full=cov --whole-suite"
ghog single a b --full=cov --whole-suite  -> green -> "Next: ghog day --full=cov --whole-suite"

GHOG_FULL=speed ghog day -> check fails -> "... re-run ghog day --full=speed --whole-suite"
ghog day --group=sentinel -> affected fails -> "... then ghog day --group=sentinel"
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
`--durations` below `speed` means runs that do not judge speed rewrite
neither the auto-floor record nor the managed exclusion section.

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

`a.ghog.day.ok` changes from one digest line to key=value lines, and each
scope gets a marker of its own (see "Group Evidence"):

```txt
scope=<whole|group:<name>>
fingerprint=<sha>
timing=<sha>
digest=<sha>
proof=<none|pass|cov|speed>
```

The marker is written to a temporary file in the same directory, then moved
over the old one with an atomic replace, so a reader sees the old or the new
marker, never a mix. A marker missing any of these lines, with an unknown
value, or unreadable for any reason (every marker written before v0.13.0
included) establishes no proof and reads as `unproven`.

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
marker of the walk's scope is removed; otherwise it is rewritten with that
proof, after a failing walk as after a green one.

Examples: saved `pass`, `--full=cov`, coverage gap: proof stays `pass`. Saved
`cov`, `--full=speed`, outliers: proof `cov`. Saved `pass`, `--full=cov`, a
full test failure: proof `none`, and a following `ghog day --full=pass` is no
longer a noop. Parallel `--full=speed` with no saved marker: the covered full
run passes (earning `cov`), then the timing pass fails a test or crashes:
proof `none`, so a following `ghog day --full=cov` walks again; the same
with `--force` and saved `speed` (without `--force`, saved `speed` on
unchanged sources makes the walk a noop): proof `none` too. Parallel
`--full=speed`, green full run, then
outliers only in the timing pass: proof `cov`. `--force` at `none` with saved
`speed` and a green walk: proof stays `speed`, since no full gate was judged.
`--force --full=cov` with saved `speed` and a coverage gap: proof `pass`.

### Noop and upgrade

With valid saved proof `P` for the walk's scope on the current digest (see
"Exact-scope proof") and requested level `L`:

- `L <= P`: noop. Nothing runs; the report states that the requested
  objective is met by saved evidence at `P`, and that no check ran;
- `L > P`: upgrade. check.bat and the affected step are reused (their step
  headers say `reused from snapshot`), and only the full step, plus the
  timing pass at `speed` in a parallel project, runs at `L`.

A digest mismatch, `unproven`, or `--force` walks the whole chain.

---

## Walk Reporting for v0.13.0 full suite levels

### Closing line keys

The day walk's closing line keeps every current key and appends five:

- `full=<none|pass|cov|speed>`: the selected objective;
- `src=<param|env|default>`: where it came from;
- `proof=<none|pass|cov|speed|unproven>`: the valid proof after this walk,
  per the snapshot rules;
- `reused=<none|check+affected|all>`: what this invocation took from the
  snapshot instead of running (`all` on a noop);
- `scope=<whole|group:<name>>`: the scope the walk ran and proved.

A direct `ghog full` appends `full=`, `src=`, `proof=` (its earned proof) and
`scope=`; `ghog check`, `ghog affected` and `ghog single` append `scope=`.
The keys are appended, never inserted, so a reader that matches the current
keys by name keeps working; the groundhog tests that assert the closing line
are updated, and no other tool parses it.

### Status evidence

`a.ghog.status` keeps its label and `state=` grammar and gains the same keys.
The running line carries `full=`, `src=`, `scope=` and `proof=pending`; the
done line carries `full=`, `src=`, `proof=`, `reused=`, `scope=` and `exit=`. `ghog status`
replays the done line as today, so a detached walk's completion reports the
same evidence as a foreground one.

### Closing instructions and restart lines

Every restart line is rendered from the carried level and scope by one
helper: `ghog day --full=<level> <scope selector>`, or `ghog day <scope
selector>` at `none`, where the selector is `--group=<name>` or
`--whole-suite` (see "Scope propagation"). Repair commands that the report
sends the LLM to receive `--full=<level>` and the selector the same way. The
fixed restart strings of `reporting_nextstep.py` become templates filled by
that helper, which covers check, affected, `ghog single`, coverage-gap,
outlier and timing-failure paths. Success lines become one line per level,
each naming its scope (`for the whole suite`, `for group <name>`):

| Level | Success line content |
| --- | --- |
| `none` | full suite skipped on purpose (no level requested); check.bat and the affected tests of the scope are green; do not run the full suite unless the calling instruction asks for a level: `ghog day --full=pass`, `ghog day --full=cov`, or `ghog day --full=speed`, each with the same scope selector; carry on with the calling instruction |
| `pass` | objective met at `pass` for the named scope: every test of that scope passes; coverage and duration gates are not required by this objective; carry on with the calling instruction |
| `cov` | objective met at `cov` for the named scope: every test of that scope passes and the coverage gate over that scope's sources is met; the duration gate is not required by this objective; carry on with the calling instruction |
| `speed` | objective met at `speed` for the named scope: every test of that scope passes, the coverage gate over its sources is met, and no unaccepted duration outlier remains under the configured exclusions; carry on with the calling instruction |

Inside a walk, the green affected step no longer prints `Next: ghog full`;
at `none` the walk's success line replaces it, and at a level the walk simply
proceeds. A standalone `ghog affected --no-cov` with no carried level keeps
its current line. The noop line states the requested level, the scope, the
saved proof level, and that no check ran in this invocation. The outlier line at `speed`
keeps the `fix_slow_test.md` procedure and the `ghog exclude` hint, and
states that an exclusion is accepted only after an attempted improvement.

---

## Test Group Declaration for v0.13.0 full suite levels

### The `.ghog-groups` file

A versioned `.ghog-groups` file at the project root declares the groups, in
the INI grammar groundhog already reads for coverage settings (Q12): one
section per group name, with a `tests` key and a `sources` key, each holding
one pattern per line.

```ini
[sentinel]
tests =
    **/tests/**/*sentinel*/**
sources =
    tools/sentinel/**
```

A group name starts with a lowercase letter and holds only lowercase
letters, digits, `-` and `_`, so it fits a file name and a key=value line.
The file is read only when a group is selected: a whole-suite run never reads
it, so a damaged declaration cannot block the whole suite.

### Pattern matching for groups

Patterns follow gitignore matching on normalized repository-relative paths
with forward slashes (feature-request Q17): `*` and `?` stay inside one path
segment, `**` spans segments, a pattern without a slash matches a name at
any depth, a trailing `/**` matches everything below a folder, and a leading
`!` removes earlier matches, the last matching pattern winning. The matcher
is built on Python 3.13's `glob.translate`, with no new dependency.

### Resolved group membership

Patterns are matched against the file walk of the snapshot digest: the
project tree without the excluded folders and the artifact home.

- test side: matched `.py` files whose names fit the project's pytest
  `python_files` setting (pytest's `test_*.py` and `*_test.py` when none is
  declared); conftest and data files under a matched folder stay out of the
  list, and pytest still loads the conftest files of the folders it collects
  from;
- source side: matched `.py` files, minus those the project's coverage
  `omit` setting excludes (Q14); a source outside the project's configured
  coverage `source` is accepted, and grouped runs measure it (see "Group
  coverage gate").

A selected group whose test side or source side resolves to no file is a
setup error (exit 5) whose line names the empty side (feature-request Q21).
The group's name, its normalized patterns and its two sorted file lists form
its scope fingerprint (see "Group Evidence").

### `ghog groups`

A read-only `ghog groups` subcommand lists each declared group with its
patterns and its resolved test and source file counts; `ghog groups <name>`
validates one group with the rules a run applies and exits 5 on any of the
errors above. It is the check `process-draft` and `write-requirement` run
before they record a group, and the one `pw scope` runs before it prints a
group selector. Like `ghog exclude`, it accepts no level and no scope
selector.

---

## Scope Selection for v0.13.0 full suite levels

### Scope resolution rule

`ghog day`, `ghog full`, `ghog check`, `ghog affected` and `ghog single`
accept `--group=<name>` and `--whole-suite` (Q13), and a captured scope,
`--scope-file=<capture>` (see "Captured scope"). Resolution happens once, in
the CLI, beside the level and with the same shape:

1. an explicit `--group=<name>`, `--whole-suite` or `--scope-file` wins, and
   `GHOG_GROUP` is then not read, so an explicit selector is honored even
   when the variable holds an invalid name;
2. otherwise a non-empty `GHOG_GROUP` names the group;
3. otherwise the whole suite.

Two explicit selectors at once, a malformed or unknown group name, an
unreadable `.ghog-groups`, an empty test or source side, and an unusable
capture are setup errors (exit 5) with a line naming the cause; none falls
back to the whole suite. The selectors are parsed as free options and
validated by groundhog, never by argparse, so none can exit 2. `GHOG_GROUP` is read through the same
injectable environment seam as `GHOG_FULL`. `ghog timings`, `ghog status`,
`ghog init`, `ghog exclude` and `ghog groups` take no scope, so a
standalone `ghog timings` always runs the whole suite. Grouped runs never
write the floor file (see "Durations in a group"); whole-suite runs that
measure durations keep their writes: a sequential full run at `speed`,
direct or inside a walk, the timing pass of a parallel `speed` walk, and
`ghog timings`.

### What a scope means per command

For `ghog day` and `ghog full`, the scope narrows the runs (see "Group-Scoped
Runs"). For `ghog affected`, it narrows the affected selection to the
group's test files. For `ghog check` and `ghog single`, it changes nothing
they run, since check.bat is project-wide and `ghog single` runs the files it
is given: as with the level, the scope only fills their restart lines.

### Scope propagation

`Invocation` gains `scope`: the whole suite, or a group with its name, its
resolved file lists and its fingerprint. `run_day` passes it to each derived
step. Every restart and repair line carries the resolved scope selector
after the level selector, default walks included: `ghog day --group=sentinel`,
`ghog single tests/x.py --full=cov --whole-suite`,
`ghog day --full=speed --whole-suite`. A whole-suite line always names
`--whole-suite`, so an ambient `GHOG_GROUP` cannot narrow a restart; "plain
`ghog day`" in the closing instructions means a line without `--full`, never
a line without the scope. A restart line names the group, not a capture: a
restart is a new walk, which is the next eligible boundary for a scope
change.

The detached walk always passes its resolved scope explicitly, whatever its
source (feature-request Q20), and keeps the level forwarding rule of Q06: a
whole-suite walk forwards `--whole-suite`; a grouped walk writes its
resolution to `a.ghog.day.scope.json` in the artifact home before spawning,
and forwards `--scope-file` to that capture, so an edit of `.ghog-groups`
between launch and the child's start cannot change what the child runs.

### Captured scope

A capture is the validated resolution of a scope, not its name: a JSON file
holding the scope kind (`whole` or `group`), the group name, its normalized
test and source patterns, its resolved test and source file lists, the
scope fingerprint over those values, and where they came from (the
requirement and `.ghog-groups` paths). Groundhog writes one through the same
resolver a `--group` run uses, for the detached child; the code-review
request renderer writes one for a review round (see "Bound scope of a review
round").

A run given `--scope-file` validates the capture before anything runs: it is
readable and complete, the fingerprint recomputed from its content matches
the recorded one, and every listed file still exists in the project. It then
runs exactly the listed test files and judges the gate over exactly the
listed sources: it never matches the patterns again, never reads
`.ghog-groups`, and never looks the name up. When any check fails, the run
stops with exit 5 and a `bound scope unusable: <reason>` line before running
any test; it never resolves the name again and never falls back to the whole
suite. Later edits of the declaration therefore show as a pending change
(see "Scope display in pw progress") and apply only at the next eligible
boundary.

---

## Group-Scoped Runs for v0.13.0 full suite levels

### Narrowed collection

With a group, groundhog passes the group's resolved test files to pytest as
positional paths:

- the full step of every level and a direct `ghog full` run only those
  files, in today's parallel or sequential shape;
- the parallel `speed` timing pass runs only those files;
- the affected step runs `--testmon` over those files, so testmon selects
  affected tests inside the group only (feature-request Q15), the
  `ghog affected` calls of a reviewer included.

A grouped full or timing run that collects no test is a setup error, exit
5 under today's empty-run rule, and establishes no proof. A grouped affected
step with nothing selected is a green no-work step under the same rule, and
proves no full-suite level by itself. A grouped full run refreshes the
failure baseline `a.ghog.failures` with the group's failures, which is what
the following `ghog single` compares against.

### Group coverage gate

At `cov` and `speed`, a grouped run judges the group gate instead of the
parsed `TOTAL` line (Q14), in three parts.

Collection: a grouped covered run measures every resolved group source.
Groundhog adds one `--cov=<folder>` for each folder in the smallest set of
folders holding the resolved source files, on top of the project's own
`--cov` options, so a source outside the project's configured coverage
`source` (such as `lib/widget.py` when the project collects `tools`) is
measured too. The rest of the project's coverage configuration still applies
(`omit`, `branch` and the other run settings). The child writes its data to
a scope-owned file in the artifact home, `a.ghog.coverage.<group>`, set
through `COVERAGE_FILE`, so no stale or foreign data file is ever read as
this run's measurement. A grouped full run starts that file fresh, so the
data comes from the group's tests only; a covered grouped `ghog affected` in
the coverage-gap loop appends to it, judges the group gate as an
intermediate check, and records no proof, and the walk that closes the loop
judges the gate again on fresh data. A grouped run also passes
`--cov-fail-under=0`, so pytest-cov reports no whole-project threshold
failure for a partial run; that change alone measures nothing more.

Analysis: after the run, groundhog reads that data file through coverage's
reporting API, restricted to the resolved source set and under the project's
coverage settings, so the figure counts statements and, when the project
measures branches, branches, exactly as the `TOTAL` line does for the whole
suite. A resolved source that valid data does not mention counts as
unexecuted, every statement and branch missed, and shows at 0%. The gate
requires 100% over that set (feature-request gap 20), whatever `fail_under`
the project declares for the whole suite. The coverage-gap block lists the
group's source files below 100% with their missing lines and branches, in
the term-missing shape covg already reads.

Data errors: a data file that is missing after a run that collected tests,
unreadable, or older than the run's start is an evidence error, never a gap
and never a success: exit 5 with a line naming the data problem. Like any
setup error, it judges no gate, so it contradicts no saved proof and earns
none.

### Durations in a group

A grouped `speed` run judges its calls against the saved gate floor (line 2
of `a.ghog.outliers`, or the one-second fallback) by the floor alone (Q15),
then applies the recorded exclusions as today (an excluded call is spared,
a slower drift still fails). It writes nothing to the floor file: neither
line 1 nor the exclusion section, whose stale-entry rule would otherwise
remove the exclusion of every test outside the group (feature-request Q19).
A grouped sequential full run at `speed` and a grouped timing pass follow
the same rule.

### Trade-off of a grouped effort

With a group, a change that breaks a test outside the group, or leaves code
outside the group's sources uncovered, is not caught before review or commit;
it surfaces at the prepare-release gate, which always runs the whole suite at
`cov` (feature-request gap 22). No gate of a grouped effort judges the speed
of tests outside its group.

---

## Group Evidence for v0.13.0 full suite levels

### One marker per scope

The snapshot keeps one marker per scope (Q16): `a.ghog.day.ok` for the whole
suite and `a.ghog.day.<group>.ok` for a group, each in the marker format of
"Snapshot Evidence":

- `fingerprint` is the scope fingerprint: the group name, its normalized
  test and source patterns and its two resolved file lists, or a fixed value
  for the whole suite;
- `timing` is the duration gate fingerprint: the active gate floor and the
  effective exclusion entries, line 1 left out, computed after the walk's own
  writes, so a whole-suite `speed` walk that ratchets an exclusion does not
  invalidate its own proof.

### Exact-scope proof

A walk reads only the marker of its own scope. Its saved proof is valid when
`scope`, `fingerprint` and `digest` all match; a `timing` mismatch alone
caps that saved proof at `cov`, since only the duration verdict depends on
the floor and the exclusions (feature-request Q18). The timing inputs live
in `a.ghog.outliers` in the artifact home, which the digest leaves out, so a
timing change never moves the digest, and a digest or scope change still
invalidates the whole proof. A changed pattern or a
changed membership therefore invalidates a group's proof for default noops
and upgrades alike, a proof never satisfies another group or the whole suite,
and a whole-suite `cov` proof never stands in for missing group coverage.
After a scope change, the destination scope reuses its own still-valid
marker; nothing is copied between scopes. The rules of "Proof after a walk"
(accumulation, cap, removal) apply to each scope's marker.

### Scope in reports

The closing line, `a.ghog.status` and the success and noop lines name the
scope (see "Walk Reporting"). A noop names the scope of the saved proof it
used, which is always the walk's own.

---

## Requestor Validation at Speed for v0.13.0 full suite levels

### Default validation command

`DEFAULT_PROJECT_VALIDATION_COMMANDS` becomes `("ghog day --full=speed",)`.
The request renderer completes that project default, and only that default,
with the effort's scope selector from the shared effort-scope reader (see
"Group Scope in the Workflow"): `ghog day --full=speed --group=sentinel` for
a grouped effort, `ghog day --full=speed --whole-suite` otherwise. Plan and
request additions are rendered as given.
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
it adds a migration notice to the rendered validation section: when no full
level is selected, plain `ghog day` now runs only check.bat and the affected
tests itself, and the project should declare `ghog day --full=speed` to keep
a full-suite proof before review. The notice distinguishes the work that
command does from stronger proof it may meet: `GHOG_FULL` can select a level
for it, another declared command can establish `speed`, and valid saved
proof can make it a noop that reports `speed`. It claims nothing about any of
those. The workflow adds no validation of its own.

A declared set is never rewritten and never given a selector
(feature-request gap 21). For a grouped effort, the request claims the group
proof only when a declared command is a `ghog day` walk naming
`--full=speed` and the effort's exact `--group=<name>`; otherwise its
validation section lists what the declared commands run and states that they
establish no `speed` proof for group `<name>` (feature-request Q25).

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

Duration exclusions are ignored Git state, so the staged-tree comparison is
supplemented by a comparison of effective exclusion entries. A change to
either sends the step back through implementation-check.

Before the pass, the implementing agent stages every change (`git add -A`),
records the index tree with `git write-tree`, and saves the output of
`ghog exclude --list` as a step artifact
(`a.<slug>.step<x>.tmp.exclusions.txt` in the artifact home). It runs
`ghog day --full=speed` with the effort's scope selector (see "Group Scope in
the Workflow"), following restart and repair lines until exit 0. After the
green walk, it stages again, records the tree once more, and runs
`ghog exclude --list --since=<saved listing>`.

### Exclusion listing and comparison

`ghog exclude --list` prints one `<node id> = <seconds>` line per effective
entry, sorted by node id, then `exclusions=<count>`. A missing floor file or
a file without an `[exclusion]` section is the empty listing,
`exclusions=0`. Unlike the tolerant reader the gate uses, the listing is
strict: a floor file that exists but cannot be read, or a section holding a
malformed entry, prints `exclusions=unreadable` and exits 5. The floor lines
are not part of the listing.

With `--since=<saved listing>`, the command compares exclusion semantics,
not the file:

- a node added, or a baseline raised, is a newly accepted duration
  exception: it prints `exclusions=changed` and those entries with their
  seconds;
- a lowered baseline or a removed entry is the tool tightening the gate after
  a measuring run, so a normal timing run that only ratchets or drops entries
  prints `exclusions=unchanged`;
- when either side cannot be read (a saved listing that is missing, damaged
  or records `exclusions=unreadable`, or a current section that is
  unreadable), it prints `exclusions=unverified` and exits 5. An unverified
  comparison never counts as unchanged.

The comparison reuses the existing entry parsing of `exclusions.py`; only its
failure handling differs from the gate's tolerant read.

### Outcome of the review-off pass

- same tree and `exclusions=unchanged`: the pass changed nothing relevant,
  and the commit menu is presented as today;
- a different tree, `exclusions=changed`, or `exclusions=unverified`: the
  step goes back through implementation-check (`pw handoff check <x>`).
  Before that handoff, the agent records in the step journal and handoff
  each accepted exclusion (call, measured time, attempted improvement,
  reason) and, when the comparison was unverified, that the exclusion state
  could not be compared, so the checker assesses the ignored policy change
  with the tracked one.

After implementation-check, the ordinary chain refreshes the commit material
(`group-commits-msg` and `a.commit`) and reaches the pass again with new
reference points: the tree and the exclusion listing recorded at the start of
that pass. An exclusion already rechecked therefore does not trigger a second
recheck, and the walk is a noop or an upgrade when its proof is still valid.
The commit menu is reached only after the required recheck has completed and
a final green pass leaves both the tree and the exclusions unchanged. The
commit-gate summary still names each exclusion accepted during the step, with
its measured time, attempt and reason. No test-only exemption and no review
exchange exist on this path.

---

## Group Scope in the Workflow for v0.13.0 full suite levels

### The effort's declared scope

An effort declares its scope in a metadata line near the top of its
requirement (feature request or issue), in the dash form of the draft's
`- Type:` and `- Umbrella:` lines:

```md
- Test group: sentinel
```

The value is a group name or the literal `whole suite`. Once the requirement
exists, it alone controls the effort's workflow scope: a missing line means
the whole suite, and the draft is never read as a fallback (feature-request
Q26). Two `Test group:` lines are an error, never a choice between them.

A shared reader, `tools/effort_scope.py`, reads that line from
`WorkflowState.requirement`, validates a named group with groundhog's group
resolver (the rules of `ghog groups <name>`), and returns the selector, the
group fingerprint and the source document. pw and the code-review request
renderer both use it. A named group that fails validation is an error naming
the requirement and the cause; no reader falls back to the whole suite.
Without a requirement, the reader returns the whole suite and says that no
requirement exists yet; it does not read the draft.

### Scope-carrying workflow commands

`pw scope` prints the effort's selector (`--group=sentinel` or
`--whole-suite`), and `pw scope <ghog arguments>` prints the complete command
with the selector appended: `pw scope day --full=speed` prints
`ghog day --full=speed --group=sentinel` (Q17). Every instruction that runs a
workflow-owned ghog command takes it from `pw scope` when it runs it: the
development walks of implement-step, implement-missing-step and
split-large-file, the plan's ready-to-run command, and the review-off `speed`
pass. Plans keep the command without a selector and point to `pw scope`, so a
later scope change never leaves a stale plan command. After the first
command, groundhog's restart and repair lines carry the selector through the
loop.

The requestor's default validation is completed by the renderer through the
same reader (see "Requestor Validation at Speed"). The code reviewer and a
reviewer-side implementation check run `ghog affected --no-cov
--scope-file=<paths.scope>`, the round's captured scope, never `pw scope`
and never the group name, so a published round keeps its scope. Prepare-release
names `ghog day --full=cov --whole-suite` in both operation strings and never
reads the effort scope, so `GHOG_GROUP` cannot narrow it.

### Bound scope of a review round

A bound scope is the validated resolution used at publication, not merely
its group name (Q18). The code-review request renderer resolves the effort's
scope once, builds the default validation command from it, and writes that
same resolution as a capture (see "Captured scope") to a caller-owned
`--scope-capture-output` in the artifact home. It records `test_scope` in the
request evidence, beside `resolved_validation_set`, and in the request's
JSON envelope: the scope, the group name, the fingerprint, the source
requirement, and the proof the scope's marker holds for that fingerprint
and the current digest, so a declaration edited between the validation walk
and rendering shows as missing proof instead of passing unnoticed.

`publish-request` takes the capture through `--scope-capture-file`, as it
takes content through `--content-file`: the core checks that the capture is
complete and that its fingerprint equals the envelope's `test_scope`, then
copies it to a core-owned protocol artifact, `paths.scope`, records the
fingerprint in the coordination record, and returns both from `status` as
`bound_scope`. Each publication replaces that artifact, and `complete`
removes it with the coordination record. No transition changes: the capture
travels with publication.

- Reviewer evidence: the reviewer runs
  `ghog affected --no-cov --scope-file=<paths.scope>`, so it executes the
  captured test files even when the same group's patterns have changed since
  publication. A capture groundhog refuses (exit 5, `bound scope unusable`)
  is missing evidence under the reviewer's existing rule, never a reason to
  run another selector.
- Legacy request: a live code-review request published before this change
  carries no `test_scope`; `status` reports `bound_scope: missing` and no
  `paths.scope`. The reviewer treats that as missing evidence and requests a
  replacement, whose publication binds a capture; no scope is guessed for it,
  the whole suite included.
- Replacement request: the renderer compares the effort's current scope with
  `bound_scope`. When they differ (another group, a switch to or from the
  whole suite, or the same group with another fingerprint), it requires a
  `--scope-change-file` holding the requestor's reason and renders a "Scope
  change" block with the previous scope, the new scope and that reason;
  without the file it stops with exit 2, naming both scopes. The replacement
  is validated in the new scope, and its publication binds the new capture.
- Commit-ready answer: when the effort's current scope differs from
  `bound_scope`, the requestor names the pending change in the gate evidence
  (bound scope, current scope, and the edit behind it). With `Commit`, that
  edit (the requirement line and any `.ghog-groups` change) stays out of the
  approved commit; with `Rework and review again`, the replacement round
  validates the new scope as above. A scope change is never admitted as a
  polishing edit.

### Scope display in pw progress

`pw progress` gains a `scope` line after `step`: the effort's scope and its
source, such as `group sentinel (docs/v0.13.0/feature-request.v0.13.0.x.md)`,
`whole suite (no Test group line in <requirement>)`, or
`whole suite (no requirement yet)`. With an active code-review exchange, a
`bound` line shows the round's bound scope, marked `pending change` when it
differs from the effort's scope. The declared scope alone never implies
group proof: only ghog reports show proof, each for its own scope
(feature-request Q25).

---

## Group Activation and Change for v0.13.0 full suite levels

### Recording the scope when a draft is processed

`process-draft` adds a test-scope menu after its branch-layout menu, and
beside the branch-layout choice in umbrella continuation mode, so every
child draft gets one: `Whole suite`, one entry per group that `ghog groups`
lists as valid, `New group`, and `Type something else`. An existing group is
validated with `ghog groups <name>` before it is recorded. `New group` asks
for the name, the test patterns and the source patterns, adds a section to
`.ghog-groups` without touching any other one, and records the group only
once `ghog groups <name>` validates it. The choice is recorded in the draft as
`- Test group: <name>` or `- Test group: whole suite`, next to `- Type:`. An
umbrella draft records no scope of its own: each child effort carries one.

`write-requirement` copies a recorded draft choice into the requirement's
`- Test group:` line, validating a group again, and asks the same menu only
when the draft records no choice, such as a draft processed before this
change (feature-request Q22 and Q26). A whole-suite answer is recorded as
`- Test group: whole suite` and never asked again. A reopened requirement
keeps its own line; the draft is not read again.

### Activation, switching and deactivation

After the requirement exists, the effort's scope changes only through its
`- Test group:` line (Q19), at any time and without reopening the
requirement's review (feature-request Q23):

- activation adds the line with a group name;
- switching replaces the name;
- deactivation sets the value to `whole suite` or removes the line.

A new group's entry is added to `.ghog-groups` first, as `process-draft`
does. None of these edits deletes or rewrites an existing group entry, which
other efforts may select; editing an entry's patterns is a separate act, and
a scope change for every effort that selects that group. The next `pw scope`
validates the edited line and refuses an invalid group instead of falling
back. `GHOG_GROUP` cannot override the effort scope, since every
workflow-owned command carries an explicit selector.

### When a scope change takes effect

A scope change takes effect at the next eligible workflow boundary
(feature-request Q24):

- a walk already started keeps the scope it resolved, a detached walk
  included through its capture;
- a published review round keeps its bound scope until its answer, since its
  reviewer evidence runs the round's capture;
- the next workflow-owned command after the edit uses the new scope: the next
  development walk, the review-off `speed` pass, or the validation of the next
  request, which then states the change.

The destination scope reuses only its own still-valid proof (see
"Exact-scope proof").

---

## Workflow Instructions for v0.13.0 full suite levels

- `implement-step.md`, `implement-missing-step.md`, `split-large-file.md`,
  and the plan command of `write-plans.md` keep `ghog day` without a level,
  run it with the selector `pw scope` prints, and describe check plus
  affected tests instead of a full coverage pass; the write-plans template's
  ready-to-run command, shared gate loop and completion criteria point to
  `pw scope`, and the step-handoff "Last gate" line records the command with
  its selector.
- `process-draft.md` gains the test-scope menu and the `- Test group:` draft
  line; `write-requirement.md` and its template carry that line and ask only
  when no choice was recorded.
- `run-pw.md` lists `pw scope`, and `pw progress` documentation shows the
  `scope` and `bound` lines.
- `implement-step.md`'s review-off branch gains the `speed` pass before the
  commit menu, with its staged-tree and exclusion-listing comparisons, the
  step-journal record of each accepted exclusion, and the return through
  implementation-check on a changed or unverified comparison.
- `groundhog.md` states that the loop always follows the restart and repair
  lines the report prints, which carry the level and the scope, and that the
  loop's objective is the level and scope it started with; exit 8 appears
  only at `speed`.
- `fix_slow_test.md` applies to `speed` walks and restarts with
  `ghog day --full=speed`.
- `code-review-requestor.md` names the `speed` validation before every
  request in the effort's scope, the exclusion evidence in the implementation
  report, the migration notice, the declared-set group statement, the scope
  capture passed from the renderer to `publish-request`, the
  `--scope-change-file` for a replacement request, the pending
  scope change in the gate evidence, and the absence of any walk at the
  commit-ready answer.
- `code-reviewer.md` and the reviewer evidence setup of
  `implementation-check.md` keep their two commands, run
  `ghog affected --no-cov --scope-file=<paths.scope>`, and treat a missing
  or refused capture as missing evidence.
- `review-requestor.md` names the `--scope-capture-file` input of a code
  `publish-request` and the core-owned `paths.scope` artifact.
- `prepare-release.md` and both operation strings of
  `prepare_release_plan_workflow.py` name `ghog day --full=cov --whole-suite`.
- `bin/ghog_cycle.bat` keeps sharing one activation; its no-argument default
  becomes `day` alone (Q02).
- `GROUNDHOG.md` and `tools/Pytest reset specs.md` document levels, the
  resolution rule, the marker format and invalidation, the closing and status
  keys, the success and restart lines, the parallel timing step, the
  `.review-validation` migration note, `ghog exclude --list`, and for groups
  the declaration, matching, scope selection, grouped runs and gate, floor
  handling, per-scope markers, the trade-off, and how to choose, change and
  remove an effort's group as opposed to a manual `--group` or `GHOG_GROUP`,
  as new decision rows and acceptance tests.

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
| parallel `--force --full=speed`, saved `speed`, timing pass fails a test | exit 2, `proof=none` | cap applies to saved proof too |
| parallel `--full=speed`, green full run, outliers only in timings | exit 8, `proof=cov` | outlier-only failure keeps `cov` |
| legacy one-line marker, unchanged sources, `ghog day` | whole default walk runs, marker rewritten with `proof=none` | no established level |
| `--detach --full=cov` | survivor runs at `cov`; `ghog status` shows `full=cov src=param proof=pending`, then the done line with `proof=` and `reused=` | detached keeps level and evidence |
| review mode on, default policy, round 1 | request published only after a green `speed` walk | speed before review |
| review mode on, replacement round, unchanged validated digest, readable marker recording `speed` for the same scope | `speed` validation is a noop on the saved proof, request published | snapshot reuse |
| review mode on, replacement round, marker unreadable, legacy, or proving only `cov` | `speed` walk runs (whole chain, or upgrade from `cov`) before the request | no reuse without valid `speed` proof |
| review mode on, replacement round changed only a gate configuration file | digest differs, whole `speed` walk runs before the request | gate configuration invalidates proof |
| review mode on, replacement round changed Python code | `speed` walk runs before the replacement request | every request validated |
| requestor needs `ghog exclude` to reach `speed` | request's implementation report lists the call, measured time, attempt and reason | exclusion reviewed |
| commit-ready answer | human gate presented, no `speed` walk, no new round | nothing at convergence |
| `.review-validation` declares plain `ghog day` | accepted, migration notice in the rendered validation section, no workflow-added walk | project authority kept |
| review mode off, `speed` pass changes nothing | tree unchanged, `exclusions=unchanged`, commit menu presented | no change, no recheck |
| review mode off, `speed` pass changes a test or production file | tree differs, step goes back through implementation-check, then the pass again | every speed change checked |
| review mode off, `speed` pass needs only `ghog exclude` | tree unchanged, `exclusions=changed`; the journal records call, time, attempt and reason; step goes back through implementation-check, then a final green pass with unchanged tree and exclusions before the menu, which lists the exclusion | ignored exclusion still rechecked |
| review mode off, pre-existing exclusions untouched, the walk only lowers a baseline or drops a stale entry and rewrites line 1 | `exclusions=unchanged`, commit menu presented | tool tightening is no new exception |
| review mode off, second pass after an exclusion recheck | listing compared to the start of that pass, `exclusions=unchanged`, commit menu presented | no repeated recheck |
| review mode off, `--since` cannot read the saved or current listing | `exclusions=unverified`, exit 5, step goes back through implementation-check with the failure stated | unverifiable is never unchanged |
| `ghog exclude --list`, floor file absent or without a section | `exclusions=0`, exit 0 | absent data is the empty listing |
| commit-ready answer, declared set that establishes no `speed` | gate presented, no `speed` walk added | project authority, nothing at convergence |
| `ghog day --full=cov --group=sentinel` | full step collects only the group's test files, gate at 100% over the group's sources, `scope=group:sentinel` | group run and gate |
| group source file never executed by the group's tests | exit 3, the file listed at 0% in the gap block | never executed counts 0% |
| whole-suite `cov` proof on unchanged sources, then `--full=cov --group=sentinel` | the group walks, no noop | whole-suite proof never masks group coverage |
| saved `sentinel` proof, then `--full=cov --group=other` | `other` walks, nothing reused | no proof across groups |
| `--group=nope`, or `.ghog-groups` unreadable with `--group=sentinel` | exit 5 naming the cause | unknown or unreadable declaration |
| `.ghog-groups` unreadable, whole-suite walk | walk runs, file not read | whole suite never blocked by groups |
| group whose test patterns match no test file | exit 5 naming the test side | empty test side |
| group whose source patterns match no source file | exit 5 naming the source side | empty source side |
| valid group, nothing affected, default walk | affected step green with no work, `proof=none` for the group | empty affected selection |
| valid group whose test files hold no test, `--full=pass` | exit 5, no proof | empty grouped run never green |
| `GHOG_GROUP=nope`, `ghog day --whole-suite` | whole-suite walk runs | explicit selector over invalid variable |
| `GHOG_GROUP=sentinel`, prepare-release green gate | `ghog day --full=cov --whole-suite`, `scope=whole` | release never narrowed |
| `GHOG_GROUP=sentinel`, ungrouped effort, development walk | `pw scope day` prints `ghog day --whole-suite` | effort scope over ambient variable |
| grouped `--full=cov` walk fails a test | `ghog single ... --full=cov --group=sentinel`, then `ghog day --full=cov --group=sentinel` | restart in the same group |
| whole-suite walk fails with `GHOG_GROUP=sentinel` set | restart line names `--whole-suite` | whole-suite restart stays whole |
| saved group proof, a test file added under the group folder | fingerprint differs, the group walks again, default noop included | membership change invalidates |
| saved group proof, the group's source patterns edited | fingerprint differs, the walk runs | pattern change invalidates |
| grouped `--full=speed`, a call above the floor | exit 8 on the floor alone, `a.ghog.outliers` unchanged | group runs leave the floor file alone |
| grouped `speed` walk, an exclusion recorded for a test outside the group | the entry survives | no stale removal from a group run |
| saved group `speed` proof, then `ghog exclude` adds an entry | `timing` differs, saved proof capped at `cov`, next `--full=speed` upgrades | timing fingerprint |
| `--detach --group=sentinel` | survivor runs in the group, `ghog status` shows `scope=group:sentinel` | detached keeps its scope |
| detached grouped walk running, requirement switched to another group | survivor keeps `sentinel` | started walk keeps its scope |
| reviewer evidence in a grouped round | `ghog affected --no-cov --scope-file=<paths.scope>`, selection inside the captured test files | reviewer stays in the bound scope |
| grouped effort, default policy | validation `ghog day --full=speed --group=sentinel`, `test_scope` in the request evidence | validation in the effort scope |
| grouped effort, `.review-validation` declares `ghog day --full=speed` | command unchanged, the request states no group proof is claimed | no false group claim |
| process-draft, existing valid group chosen | `ghog groups sentinel` passes, draft gets `- Test group: sentinel` | initial selection |
| process-draft, new group | `.ghog-groups` gains one validated section, then the draft line | new valid group |
| process-draft whole suite, then write-requirement | requirement gets `- Test group: whole suite`, no question asked | explicit answer never asked again |
| write-requirement on a draft without the line | the scope menu is asked once | asks only when nothing was recorded |
| requirement line added after step 2 | the next `pw scope` prints `--group=sentinel`, later walks use it | activation after the effort started |
| requirement switched to another group, or set to `whole suite` | the next workflow command uses the new scope, `GHOG_GROUP` cannot override it | switch and deactivation |
| draft still names `sentinel`, requirement line removed | `pw scope` prints `--whole-suite` | stale draft never a fallback |
| deactivation of `sentinel` | its `.ghog-groups` entry unchanged | shared entry survives |
| same group name, patterns edited while a round is published | `pw progress` marks `pending change` | definition change is a scope change |
| scope changed while a round is published | reviewer keeps the bound scope; the replacement needs `--scope-change-file`, states previous scope, new scope and reason, and is validated in the new scope | replacement carries the change |
| replacement request rendered after a scope change without `--scope-change-file` | renderer exit 2 naming both scopes | change never silent |
| commit-ready answer with a pending scope change | gate evidence names it; `Commit` keeps the scope edit out of the commit; `Rework and review again` validates the new scope | never admitted as polishing |
| scope switched back to a group whose marker is still valid | its proof reused (noop or upgrade) | exact-scope reuse |
| `pw progress`, grouped effort with an active round | `scope` line with its source, `bound` line, `pending change` when they differ | scope visible |
| `pw scope`, requirement naming an unknown group | error naming the requirement and the cause, no selector printed | no silent fallback |
| round published for `sentinel` with tests under `tests/old/**`, then the same group's patterns edited to `tests/new/**` before reviewer evidence | `--scope-file` runs only the captured `tests/old` files against the captured source list; no `tests/new` file runs; `pw progress` marks `pending change` | published round keeps its resolution |
| same, with a captured test file deleted before reviewer evidence | exit 5 `bound scope unusable`, no test runs, evidence reported missing | refusal, never a different scope |
| capture edited after publication (fingerprint no longer matches its content) | exit 5 `bound scope unusable` before any test runs | capture integrity |
| live code-review request published without `test_scope` | `status` reports `bound_scope: missing`, no `paths.scope`; reviewer reports missing evidence and requests a replacement | no guessed scope, whole suite included |
| `--scope-file` together with `--group` or `--whole-suite` | exit 5 naming both selectors | one explicit scope |
| detached grouped walk, `.ghog-groups` edited between launch and the child's start | child runs the launch capture's test and source lists | detached keeps its resolution |
| group source `lib/widget.py` outside the project's coverage `source`, fully exercised by the group's tests | measured through the added `--cov` folder, gate met at 100% | accepted sources are measured |
| same source never executed by the group's tests | exit 3, `lib/widget.py` at 0% in the gap block | never executed counts 0% |
| group source pattern matching a file the project's `omit` excludes | file outside the group's source set, gate unaffected | project omit kept |
| grouped covered run whose data file is missing, unreadable or older than the run | exit 5 naming the data problem, no gap, no proof earned, saved proof unchanged | invalid data never proves coverage |
| project measuring branches, group source with every line run but a branch missed | exit 3, the missed branch listed | branch coverage kept |
| saved `cov` proof, only line 2 of `a.ghog.outliers` or an exclusion changed, `--full=cov` | noop on the saved `cov` proof, nothing ran | timing change keeps lower proof |
| saved `speed` proof, only an exclusion changed, `--full=speed` | upgrade: check and affected reused, full run at `speed` | timing change caps at `cov` |
| saved `speed` proof, a Python file changed, `--full=cov` | digest differs, whole chain runs | ordinary digest change still invalidates |

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

Question description: a sequential full run carries `--durations` today, and every run that captures durations rewrites `a.ghog.outliers`: line 1 (the auto-floor record, never read by the gate) and the managed `[exclusion]` section (baselines lowered, stale and fast-again entries removed). The gate floor on line 2 is never rewritten by a run. The design drops `--durations` at `pass` and `cov`, so only whole-suite runs that judge speed touch that file (a `speed` walk, a direct sequential `ghog full` at `speed`, and `ghog timings`); grouped runs never write it (Q15). The feature request allowed informational durations at lower levels.

#### BBQ for Q03

The bakery keeps a list of loaves allowed to bake slowly, each with its accepted time, and tightens or strikes an entry whenever a timed bake comes in faster. If every quick practice bake also updates that list, the allowances move with bakes nobody judged.

In this picture: the list is the `[exclusion]` section of `a.ghog.outliers`, practice bakes are `pass` and `cov` full runs, and updating the list is the ratchet each measuring run applies.

#### Options for Q03

- Option A: no `--durations` below `speed`; only whole-suite runs that judge speed rewrite the floor file.
  - pro: the auto-floor record and the exclusion baselines change only with whole-suite speed runs;
  - pro: a slightly shorter command, and no timing output nobody acts on.
  - con: no informational durations at `pass` or `cov`.
- Option B: keep `--durations` and print informational durations below `speed`, without rewriting the floor file.
  - pro: timings stay visible during development.
  - con: output nobody acts on, and a second path through the duration code that only reports.
- Option C: keep today's behavior (durations measured and the floor file rewritten) and only skip the verdict.
  - pro: smallest change.
  - con: exclusion baselines and the auto-floor record drift with runs that were never judged.

#### Recommended option for Q03 (with arguments for this choice)

Option A: the levels exist to keep speed work out of development; measuring and reporting durations there invites exactly that work, and updating exclusion baselines from unjudged runs makes the `speed` verdict depend on runs that never judged speed.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: it keeps the floor file a record of whole-suite speed runs only and the lower levels quiet about speed, as the feature request allows but does not require.

### Q04: Marker format and the default walk's proof

Question description: `a.ghog.day.ok` holds one digest line today, written in place. The design writes `digest=` and `proof=` key=value lines through a temporary file and an atomic replace, and writes a marker after a green default walk too (`proof=none`), so the development noop keeps working and a later upgrade can reuse check and affected. Which proof survives a failing walk is Q08.

#### BBQ for Q04

The inspection sticker used to carry one stamp. The new sticker needs to say which inspection was passed, including the quick one, or the quick daily check could never be skipped on an unchanged car.

In this picture: the sticker is `a.ghog.day.ok`, the stamp is the digest, the inspection level is `proof=`, and the quick daily check is the default walk.

#### Options for Q04

- Option A: key=value lines (`digest=`, `proof=`, plus the scope keys of Q16), rewritten after every walk that judged a gate with the proof Q08 computes (green walks, the default one included, and failing walks too) and removed when that proof is `unproven`, always through a temporary file and an atomic replace; any unreadable or incomplete marker reads as `unproven`.
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

Option A: it records the proof with its digest in one file replaced atomically, in the grammar groundhog already uses, keeps the noop for default walks, updates or removes the marker after a failing walk as Q08 requires instead of writing it only on success, and reads any damaged marker in the safe direction.

### Q05: Evidence keys on the closing line

Question description: the design appends `full=`, `src=`, `proof=` and `reused=` to the day walk's closing line (and `full=`, `src=`, `proof=` to a direct `ghog full`, where `proof=` is what that single run earned). `proof=` takes `none|pass|cov|speed` or `unproven` (no valid evidence), so a successful default walk (`none`) is never confused with a failed or stale one. `a.ghog.status` carries the same keys, with `proof=pending` while running. Groups add a fifth key, `scope=`, under the same rule. The closing line already carries seven keys and is the line an LLM reads first.

#### BBQ for Q05

The receipt already lists the total and the payment. Adding what was ordered, who ordered it, and what came from the fridge instead of the stove can go on the same line, on a second line, or on a separate slip.

In this picture: the receipt line is the closing line, what was ordered is `full=`, who ordered it is `src=`, the fridge is the snapshot proof reused, and the separate slip is a new evidence line.

#### Options for Q05

- Option A: append the new keys (four, and `scope=` with groups) to the existing closing line.
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

Question description: `_detached_day_command` rebuilds the child command line. The design forwards `--full` only when the level came from the parameter, and relies on the inherited environment for `GHOG_FULL`, so the child reports the same `src=`. The scope is always passed explicitly, as the feature request's Q20 requires, a grouped walk through its capture (see "Scope propagation" and Q18); this question covers the level only.

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

Question description: the design renders every restart line through one helper from the walk's level. Some next-step lines live outside a walk: `ghog single` green or failing after a leveled full run, `ghog check`, and a standalone covered `ghog affected` in the coverage branch. Those runs are not walks, so they carry no level of their own. In the design, the carried level never changes what these commands run or measure; it only fills their restart lines. The scope selector travels through the same commands the same way (see "Scope propagation"), and it does narrow what `ghog affected` selects.

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

### Q09: How the review-off speed pass detects changes to the step or its duration exclusions

Question description: with review mode off, the `speed` pass runs after `a.commit` is ready and before the commit menu. Any change it makes, a duration exclusion included, must send the step back through implementation-check (feature-request gap 15). Tracked changes show in the staged tree, but an exclusion lives in the ignored `[exclusion]` section of `a.ghog.outliers`, which no tree records, and a normal timing run also rewrites that file (line 1, lowered baselines, removed entries) without accepting any new exception. The detector must therefore cover both inputs, tell a new exception from the tool's own tightening, and never read an unverifiable comparison as unchanged.

#### BBQ for Q09

After the quality check, the baker times the loaf and sometimes tweaks the recipe, or pins a note in the back office allowing one loaf to bake slowly. Before the loaf ships, someone must know whether the recipe card changed or a new allowance was pinned. They can photograph the card and the allowance board before and after, compare only the oven settings, or trust the baker to say so.

In this picture: the recipe card is the staged tree, the allowance board is the `[exclusion]` section, the two photographs are the `git write-tree` ids and the `ghog exclude --list` outputs, the oven settings are the snapshot digest, and the baker's own account is the agent's report.

#### Options for Q09

- Option A: before the pass, stage everything, record `git write-tree`, and save `ghog exclude --list`; after the green walk, stage again, record the tree, and run `ghog exclude --list --since=<saved listing>`. A different tree, an added exclusion or a raised baseline (`exclusions=changed`), or an unreadable side (`exclusions=unverified`) sends the step through implementation-check with the exclusion evidence in the step journal; lowered baselines and removed entries are tightening, not a change.
  - pro: exact for tracked content of every kind, and semantic for exclusions, so floor rewrites and ratchets cause no spurious loop;
  - pro: reuses the existing exclusion parsing, and an unverifiable comparison can never pass as unchanged.
  - con: a small listing mode on `ghog exclude`, and any tracked change, even a comment, costs one implementation check.
- Option B: compare the snapshot digest of `a.ghog.day.ok` before and after.
  - pro: already computed by groundhog.
  - con: the digest covers Python files and gate configuration only, so a changed data file, a non-Python fixture or an exclusion would go unnoticed.
- Option C: rely on the agent stating whether it changed anything.
  - pro: no machinery.
  - con: not verifiable, and easy to forget in a long repair loop.

#### Recommended option for Q09 (with arguments for this choice)

Option A: the question is "did the step or its accepted duration exceptions change", and two tree ids plus a semantic exclusion comparison answer it exactly; a change that is only cosmetic costs one implementation check, which is cheap next to an unchecked production change or an unchecked exception. Each later pass compares against its own starting point, so an exclusion already rechecked never loops.

#### Answer to Q09: option A (with reason why it must be accepted as the answer)

Option A: comparing the staged tree and the effective exclusion entries before and after the green walk tells the agent, exactly and verifiably, whether the step must go back through implementation-check, including for repairs that touch only ignored exclusion state.

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

### Q12: Where test groups are declared

Question description: the feature request asks for a versioned file at the project root mapping each group to its test and source patterns (gap 18), and leaves the format to the design. The design uses `.ghog-groups` in INI form, one section per group with multi-line `tests` and `sources` keys, read only when a group is selected.

#### BBQ for Q12

The kitchen keeps named prep lists: "pastry station: these recipes, these ingredients". The lists can hang on their own board, be written into the main recipe book whose every edit sends the inspectors through the whole kitchen again, or be typed into a strict form nobody can annotate.

In this picture: the own board is `.ghog-groups`, the main recipe book is `pyproject.toml`, part of the snapshot digest, and the strict form is a JSON file.

#### Options for Q12

- Option A: a `.ghog-groups` INI file at the project root, one section per group, `tests` and `sources` keys holding one pattern per line.
  - pro: groundhog already reads INI through `configparser` (`gate.py`), and the file allows comments;
  - pro: independent of `pyproject.toml`, which some consuming projects do not have, and outside the snapshot digest, so adding a group invalidates no proof.
  - con: one more root file.
- Option B: `[tool.ghog.groups.<name>]` tables in `pyproject.toml`.
  - pro: no new file.
  - con: `pyproject.toml` is a gate configuration file of the digest, so adding or editing any group invalidates the proof of every scope; projects without it need another home anyway.
- Option C: a JSON `.ghog-groups.json` file.
  - pro: strict structure.
  - con: a third grammar among groundhog's files, no comments, and noisy quoting for lists of globs.

#### Recommended option for Q12 (with arguments for this choice)

Option A: it reuses a grammar and a reader groundhog already has, keeps group edits from invalidating unrelated proof (the scope fingerprint already covers the selected group's own patterns), and works in every consuming project.

#### Answer to Q12: option A (with reason why it must be accepted as the answer)

Option A: a dedicated INI file is readable, commentable, read only when a group is selected, and changes a group's proof only through that group's own fingerprint.

### Q13: How the explicit whole-suite selector is spelled

Question description: the feature request requires an explicit whole-suite selector that wins over `GHOG_GROUP`, even an invalid one, and that every whole-suite restart line, detached run, ungrouped effort and prepare-release names (gap 19, Q20). It leaves the spelling to the design. The design adds a `--whole-suite` flag beside `--group=<name>`.

#### BBQ for Q13

A waiter's ticket says either "table 7 only" or "the whole room". "The whole room" can be its own box on the ticket, a made-up table number "all", or a new "area" field that replaces the table field.

In this picture: table 7 is `--group=sentinel`, the box is `--whole-suite`, the made-up table is `--group=all`, and the new field is a `--scope=` option.

#### Options for Q13

- Option A: a `--whole-suite` flag beside `--group=<name>`; both at once is a setup error (exit 5).
  - pro: reads as what it does in every restart line;
  - pro: reserves no group name.
  - con: two options for one dimension.
- Option B: a reserved value, `--group=all`.
  - pro: one option.
  - con: reserves a name a project may want, and `all` can be misread as "every group".
- Option C: a new `--scope=<name>|whole` option instead of `--group`.
  - pro: one option, explicit.
  - con: departs from the `--group=<name>` the requirement names, and `GHOG_GROUP` no longer mirrors its option.

#### Recommended option for Q13 (with arguments for this choice)

Option A: restart lines are read and followed literally by an LLM, so the whole-suite case should say so in plain words, and a flag cannot collide with any group a project declares.

#### Answer to Q13: option A (with reason why it must be accepted as the answer)

Option A: `--whole-suite` is unambiguous on every printed line, honored before `GHOG_GROUP` is read, and keeps `--group` meaning one named group only.

### Q14: How the group coverage gate collects and judges coverage

Question description: at `cov` and `speed`, a group must have 100% of its declared source files covered by its own tests, a never-executed source counting as 0% (feature-request gap 20). Today pytest-cov collects over the project's `--cov=tools`, the verdict reads its `TOTAL` line against the project's `fail_under`, and the project's coverage `omit` list exempts thin wrappers, protocols and `__init__.py`. A group's source patterns may select files outside the project's collected `source`, and reading existing data cannot supply measurements the collector never took. The design adds a `--cov` folder for every resolved source, writes the data to a scope-owned file, analyses exactly the resolved set under the project's coverage settings (omit and branch measurement included), and treats missing or stale data as an evidence error.

#### BBQ for Q14

The pastry station must show that every one of its recipes was cooked and tasted. The tasting log only records the rooms the inspector was told to watch. The inspector can be told to watch every room where a pastry recipe is cooked, the station can be forbidden to list recipes cooked outside the watched rooms, or every listed recipe can be checked, including the decorations the restaurant never tastes.

In this picture: the recipe list is the group's resolved source files, the tasting log is the coverage data file, the watched rooms are the collector's `--cov` folders, and the decorations are the project's `omit` entries.

#### Options for Q14

- Option A: measure every resolved source (one added `--cov` folder per source folder, data in a scope-owned file), then analyse exactly the resolved set, minus the project's `omit` entries, under the project's coverage settings; a source absent from valid data is unexecuted at 0%, and missing, unreadable or stale data is an evidence error (exit 5).
  - pro: every accepted source can reach the gate, and a never-executed one fails exactly;
  - pro: the same exemptions and the same statement-and-branch semantics as the whole-suite gate.
  - con: extra `--cov` folders and a second coverage reading path beside the parsed `TOTAL`.
- Option B: keep the project's collector and refuse, at group validation, any source outside its configured coverage `source` (exit 5 naming the file).
  - pro: no change to collection.
  - con: a visible but permanent restriction on which code a group can cover, unrelated to the group's own tests.
- Option C: measure every resolved source as in A, but judge every declared source file, ignoring the project's `omit` list.
  - pro: literal reading of "declared source files".
  - con: files the project deliberately exempts would hold the group gate the whole-suite gate never asks for, and some (TTY wrappers) cannot meet it.

#### Recommended option for Q14 (with arguments for this choice)

Option A: the declaration accepts general source patterns, so collection must follow them; analysing the same resolved set under the project's own settings makes the group gate a narrowing of the whole-suite gate rather than a stricter or a weaker one, and invalid data can never pass as coverage.

#### Answer to Q14: option A (with reason why it must be accepted as the answer)

Option A: the group gate measures and counts exactly the group's accepted sources, from the group's own run, with the project's exemptions and coverage semantics intact, and stops on unusable data instead of guessing.

### Q15: How a grouped `speed` run applies the outlier rule

Question description: the outlier rule flags a call at or above the gate floor and far out by a modified z-score over the run's own calls. A group must be judged against the saved whole-suite floor, or its one-second fallback, without rewriting it (feature-request Q19). In a group, "the run's own calls" are the group's calls only. The design judges a grouped run by the floor alone, the rule's existing fallback, then applies the recorded exclusions as today.

#### BBQ for Q15

A dish counts as too slow when it takes at least ten minutes and is far slower than the evening's typical dish. On a pastry-only evening every dish is slow, so "far slower than typical" never fires. The judge can apply the ten-minute bar alone, compare the pastries only with each other, or remember the typical dish of the last full evening.

In this picture: ten minutes is the gate floor, "far slower than typical" is the z-score over the run's calls, the pastry-only evening is a grouped run, and the remembered evening is a saved whole-suite scale.

#### Options for Q15

- Option A: a grouped run flags every call at or above the saved gate floor (the floor-alone rule), then applies the recorded exclusions; nothing is written to the floor file.
  - pro: literally "judged against the saved floor", independent of the group's size and spread;
  - pro: close to the whole-suite verdict in practice, since a whole-suite median sits far below the floor.
  - con: may flag a call just above the floor that a widely spread whole suite would spare.
- Option B: the unchanged two-condition rule over the group's own calls.
  - pro: one code path.
  - con: a group of uniformly slow tests sets its own norm, so its slow calls pass the z-condition and no gate of the effort ever flags them.
- Option C: the z-score against the scale of the last whole-suite measuring run (saved median and MAD).
  - pro: closest to a whole-suite verdict.
  - con: new saved state beside the floor, stale between whole-suite `speed` runs, which a grouped effort never runs itself.

#### Recommended option for Q15 (with arguments for this choice)

Option A: the saved floor is the one shared standard the requirement names, and judging by it alone keeps a group from lowering its own bar; an extra flag near the floor is resolved by the usual `fix_slow_test.md` attempt or an exclusion with evidence.

#### Answer to Q15: option A (with reason why it must be accepted as the answer)

Option A: grouped `speed` runs hold every call to the shared floor and the recorded exclusions, without a group-relative norm and without touching the floor file.

### Q16: Where per-scope proof is kept

Question description: a proof is valid only for the exact scope it was earned on (feature-request Q18), and a destination scope may reuse its own still-valid proof after a scope change (gap 24). The design keeps one marker file per scope, each carrying a scope fingerprint (name, patterns, membership) and a timing fingerprint (gate floor and exclusion entries) beside the digest; a timing mismatch alone caps that scope's saved proof at `cov`.

#### BBQ for Q16

Each station earns its own hygiene certificate. Each can hang its own on its own wall, all can share one board that every inspection rewrites, or the kitchen can keep only the last certificate issued.

In this picture: a station is a scope, a certificate is a marker with its proof, the shared board is one file of records, and keeping only the last one is a single-scope marker.

#### Options for Q16

- Option A: one marker per scope, `a.ghog.day.ok` for the whole suite and `a.ghog.day.<group>.ok` for a group.
  - pro: a walk in one scope never touches another scope's proof, so switching back reuses still-valid proof;
  - pro: each file keeps the single-writer atomic replace of Q04.
  - con: one more file in the artifact home per group used.
- Option B: one marker file holding one record per scope.
  - pro: one file.
  - con: every walk rewrites the other scopes' records, so two concurrent walks (one detached) can lose a record.
- Option C: one marker holding only the last scope's proof.
  - pro: simplest.
  - con: every scope switch discards the proof the destination scope may reuse.

#### Recommended option for Q16 (with arguments for this choice)

Option A: it gives exact-scope reuse with no read-modify-write between scopes, and the whole-suite marker keeps today's file name.

#### Answer to Q16: option A (with reason why it must be accepted as the answer)

Option A: one atomic marker per scope keeps each proof bound to its exact scope and lets a destination scope reuse its own proof after a switch.

### Q17: How workflow-owned ghog commands receive the effort scope

Question description: an ungrouped effort must use the explicit whole-suite selector and a grouped one its group, in every workflow-owned ghog command, and a scope change takes effect at the next command (feature-request gaps 19, 21 and 24). pw prints no ghog command today; commands come from instructions, plan templates, the validation default and the prepare-release operations. The design adds `pw scope`, which prints the selector or the completed command at the moment of use, and has the request renderer complete the default validation command in code.

#### BBQ for Q17

Each cook must know which station the current order belongs to. They can ask the front desk when they start cooking, hand the order to a runner who cooks it for them, or read the station printed on last week's menu.

In this picture: the front desk is `pw scope`, the runner is a `pw ghog` launcher, and last week's menu is a plan written before the scope changed.

#### Options for Q17

- Option A: `pw scope` prints the selector (or `pw scope <ghog arguments>` the completed command) when an instruction runs its ghog command; plans carry no selector; the renderer completes the validation default.
  - pro: resolved from the requirement at run time, so a change applies at the next command;
  - pro: the command the agent runs stays literal and visible, and restart lines carry it afterwards.
  - con: each instruction's first ghog call goes through `pw scope`.
- Option B: a `pw ghog <arguments>` command that runs groundhog with the selector.
  - pro: no selector to copy.
  - con: pw becomes a groundhog launcher and must reproduce the redirect, detach and environment handling of `bin/ghog.bat`.
- Option C: write the selector into each plan's ready-to-run command.
  - pro: no new pw command.
  - con: a plan written before a scope change keeps the old selector, and the requestor validation still needs another source.

#### Recommended option for Q17 (with arguments for this choice)

Option A: the requirement makes the scope changeable at any time, so it must be read when a command runs, not when a plan is written; printing the command keeps groundhog's launcher as the only runner.

#### Answer to Q17: option A (with reason why it must be accepted as the answer)

Option A: `pw scope` gives every workflow-owned command the current, validated scope as literal text, and the code paths that build commands use the same reader.

### Q18: How a published round and a detached walk keep their resolved scope

Question description: a published round and a started walk keep their scope; a replacement request must state the previous scope, the new scope and the reason; a commit-ready answer must name a pending change; and `pw progress` must show it (feature-request Q24, Q25). Keeping the group name is not enough: if the same group's patterns change after publication, or between a detached launch and the child's start, a lookup by name would run a different set of tests. The design captures the validated resolution (patterns, resolved test and source files, fingerprint, provenance): the renderer writes it, `publish-request` copies it into a core-owned `paths.scope` artifact and records its fingerprint in the coordination record, and the reviewer runs `ghog affected --no-cov --scope-file=<paths.scope>`; a detached grouped walk passes its own capture to the child. Groundhog validates a capture before running anything and stops on an unusable one; a legacy request without a capture is missing evidence.

#### BBQ for Q18

The tasting panel is judging a dish from the pastry station, and the station's recipe list may be rewritten before the verdict. The panel can keep a sealed copy of the recipe list the dish was cooked from, keep a reference to the archived edition of the list and re-read it, or rely on the cook's own notebook.

In this picture: the sealed copy is the captured resolution in `paths.scope`, the archived edition is a Git object id of `.ghog-groups` and of the tree, and the cook's notebook is a line the requestor writes into the step handoff.

#### Options for Q18

- Option A: capture the validated resolution at publication (and at detached launch) in a core-owned or launcher-owned artifact, consumed through `--scope-file`, checked against its fingerprint and the existence of every listed file, with a typed refusal when unusable.
  - pro: execution consumes exactly what was validated and published, never a later declaration;
  - pro: the renderer, the requestor and `pw progress` read the fingerprint through `status`, and no transition changes.
  - con: a new protocol artifact and a publish input in the shared core, and a third scope selector in groundhog.
- Option B: record Git object ids of `.ghog-groups` and of the reviewed tree, and re-resolve the group from those objects when evidence runs.
  - pro: no file lists stored.
  - con: `.ghog-groups` may be uncommitted when the round is published, and re-resolving from objects needs a second, object-based resolver beside the one runs use.
- Option C: a `Bound scope:` line the requestor writes into the step handoff after each publication.
  - pro: no core change.
  - con: depends on the requestor writing it every time, holds only a name to look up again, and tools would read a private working note.

#### Recommended option for Q18 (with arguments for this choice)

Option A: the bound scope is a fact about publication, so the component that publishes should keep it, in the form execution needs; a captured resolution with an integrity check makes drift either harmless or an explicit stop, never a silent change of tests.

#### Answer to Q18: option A (with reason why it must be accepted as the answer)

Option A: reviewer evidence and detached children run the exact resolution captured for their round or launch, a capture that can no longer be used stops with a diagnostic, and a missing capture is never filled with a guessed scope.

### Q19: How an effort's scope changes after its requirement exists

Question description: activation, switching and deactivation edit only the requirement's `Test group:` line, at any time and without reopening its review (feature-request Q23). The design treats that line as the only control: an edit by hand or by the agent at the human's request, validated by the next `pw scope`.

#### BBQ for Q19

A cook's station is written on the duty roster. It can be changed by rewriting that one roster line, by a manager's machine that prints the new line, or by redoing the hiring interview.

In this picture: the roster line is `- Test group:` in the requirement, the manager's machine is a `pw scope --set` command, and the interview is `write-requirement`.

#### Options for Q19

- Option A: edit the requirement's `- Test group:` line; the next `pw scope` validates it and refuses an invalid group.
  - pro: one visible, versioned line and no new command, exactly the edit the requirement settles;
  - pro: GROUNDHOG.md and the workflow documentation describe a single procedure.
  - con: an invalid edit is reported at the next `pw scope`, not while editing.
- Option B: a `pw scope --set <name>` or `--whole-suite` command that validates, then edits the line.
  - pro: validation at edit time.
  - con: a command that rewrites a requirement document for one line, and a second way to make the same edit.
- Option C: re-run `write-requirement` to ask the scope again.
  - pro: reuses the authoring menu.
  - con: replays requirement authoring for one line and risks touching the rest of the document.

#### Recommended option for Q19 (with arguments for this choice)

Option A: the requirement settles that the line is the control; validating it where it is read, before any command uses it, gives the same safety as an editing command without a second path.

#### Answer to Q19: option A (with reason why it must be accepted as the answer)

Option A: the effort's scope is whatever its requirement line says, checked by `pw scope` before any workflow command runs with it.
