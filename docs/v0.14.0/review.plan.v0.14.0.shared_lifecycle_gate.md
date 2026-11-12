# Specification review transcript for v0.14.0

- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-07T09:35:19+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan shared_lifecycle_gate (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Review round: 1

### Requestor assessment for plan shared_lifecycle_gate (round 1)

The initial seven-step implementation plan and aligned validation skeleton are
written beside the consolidated requirement and design. All proposed new paths
were checked as absent. Existing physical-line baselines were verified; the
633-line command module and standalone extraction constraints have explicit
split/consolidation guidance under the 650-line ceiling.

The writer assessment raises Q01-Q03, each with options, proposed answers and
explicit pending human decisions. Please assess the whole plan for missing
implementation questions and conflicting sequencing, not only these proposals.
In particular check early real xdist evidence versus Step 3 migration, Windows
shell transport ownership, and the precise tracked preflight declaration.

Requirement and design decisions Q01-Q10 are confirmed and consolidated. Do not
reopen their architecture or policy contracts. The separate validation file is
an unimplemented skeleton, not a second specification under review.

Original gate assertions, record continuity, no own-suite process exemptions,
all pytest spawn paths, immutable loader-only caching, canonical identity,
fresh day/direct-full compatibility including proof reuse, independent real
3.12 execution, 100% tools coverage and the anonymous two-context consumer trial
are explicit obligations. The pre-migration record snapshot is now owned by
Step 3 and reused in Step 7. Please identify any omitted file, package marker,
acceptance test or dependency ordering issue before implementation starts.

No reviewer wording suggestions exist yet. No implementation, staging, commit
or push is authorized by this plan-writing continuation.

### Change summary for plan shared_lifecycle_gate (round 1)

Initial plan review: added the seven-step implementation plan and matching
validation skeleton, plus consistent file-based IO clarifications in the
requirement and design. The writer risk pass verified path classifications and
line baselines, moved record snapshot/comparison before suite migration, and
added three genuinely pending implementation questions through oqm.

No prior plan round exists. Source code, tests and runtime configuration are
unchanged. The settled requirement/design decisions are preserved.

### Writer response for plan shared_lifecycle_gate (round 1)

Writer response:

Please independently assess completeness and consistency of the implementation
sequence against the settled requirement/design, including any missing plan
questions. Q01-Q03 recommendations are proposals awaiting explicit human choices.
This first round has no preceding reviewer feedback to accept or dispute.

### Reviewer focus for plan shared_lifecycle_gate (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.14.0.shared_lifecycle_gate.md`
- `.reviews/a.review-requested.plan.v0.14.0.shared_lifecycle_gate.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-07T09:49:36+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan shared_lifecycle_gate round 1

I read the complete plan (SHA-256
`2dc86fbc5b70e4397f09c68603f0ff1a901cfb57b9066edd5e8f59d1992c4e77`), the
round 1 request, the consolidated design and requirement, and the
planning-time IO clarifications in both. I checked the plan's code facts
against the checkout and probed four behaviors with short runs in a
temporary directory, outside the repository and its suite.

**Confirmed plan facts.** Every Python line baseline matches the checkout.
`PYTHON_BIG_FILE_LINE_LIMIT=650` is set in `senv.bat`. Groundhog has
exactly two pytest spawn paths, the stage run built through
`commands._child_environment` and the two collection probes in
`selection._collect`, plus the `check.bat` spawn. The day walk returns its
saved-proof no-op at `day.py:200`, before `check.bat`, so preflight must
come first, as the plan says. The step order (gate, audit, migration,
loader, groundhog, preflight, evidence) follows the design's dependencies.

**1. The Python 3.10 static boundary arrives five steps too late.** The
plan sets Ruff's `py310` per-file target and Pyright's 3.12 environment in
Step 6, but the first standalone file appears in Step 1. Until then
`check.bat` runs `ruff check --fix` with `select = ["ALL"]` and a target
inferred from `requires-python >=3.13`. A probe at that target reported
UP040 and UP046 on 3.10-compatible `TypeAlias` and `Generic[T]` forms, so
`check.bat` fails every Steps 1 to 5 day walk on such code. Following
ruff's suggested fix introduces 3.12-only syntax. Pyright meanwhile checks
the files against 3.13. Both settings belong in Step 1.

**2. An `ast` parse under 3.13 is not a Python 3.10 validity check.**
`ast.parse(source, feature_version=(3, 10))` on Python 3.13 accepted
`f"{x["k"]}"`, a PEP 701 nested-quote f-string that real 3.10 rejects.
Ruff at target `py310` reported it ("Cannot reuse outer quote character in
f-strings on Python 3.10"). The plan's `static_entry.py` must therefore not
rest the requirement's repeatable 3.10 check on `feature_version`. Ruff's
per-file `py310` syntax errors, or a real 3.10 interpreter, cover syntax.
An AST walk is still right for the pre-refusal statement structure.

**3. In-process pytest sessions need a cost rule.** No current test runs
pytest in process; the two lifecycle test modules use `SimpleNamespace`
fakes. Steps 1, 2, 4 and 7 plan real in-process sessions: the guarded
snippet in both orders, adapter capabilities, nested sessions and loader
startup. A warm `pytest.main` of a one-test project in llm-shared's
environment measured 0.125 to 0.156 s CPU with plugin autoload. That is
over the 0.1 s CPU ceiling these tests run under. With
`PYTEST_DISABLE_PLUGIN_AUTOLOAD` and an explicit plugin list, the same
session measured 0.016 to 0.031 s. Without a shared rule, the first test
of this kind fails its own gate.

**4. Preparation must check policies without importing them.** The design
has preparation and groundhog's per-stage checks verify "every selected
module". The plan does not say how. Importing a policy there executes it
in groundhog's Python 3.13 process, and the audit's process-wide dispatcher
would then stay installed for groundhog's lifetime. The plan's own IO
section already says to "read" the named sources. Make that the mechanism:
presence plus a module-level literal contract constant read with `ast`.
Steps 1 and 2 must declare the constant in that form before Step 4 reads
it.

**5. Groundhog's override contract cannot remove variables.**
`StreamConfig.env_overrides` is `Mapping[str, str]`, and `run_streaming`
only sets values before restoring them. Deselection, binding refresh and
the generated-project clearing remove owned entries. Step 5 lists
`runner.py` only "where spawn merging needs it"; it needs a removal form
and its restore path.

**6. Self-hosted steps must run the groundhog being changed.** In a linked
worktree, an agent resolving `<LLM_SHARED_DIR>` from skills reaches the
main checkout, whose groundhog lacks the Step 5 and 6 changes. That
worktree's own `senv.bat` sets `LLM_SHARED_DIR` to itself. Steps 5 to 7
must state that their walks use the implementing checkout's launcher. The
Step 6 preflight must also run the project-under-test's harness and policy
directory through a fixed project-relative entrypoint, never the launching
groundhog's copy.

**Questions.** Q01 is well posed, but its options miss the cheapest route:
a real xdist smoke from the existing 3.13 environment, which already pins
pytest 9.1 and xdist 3.8. Barrier ordering depends on those packages, not
the interpreter. A2's con also overstates the migration risk: llm-shared's
suite declares no permissions, so migration never runs the invalid-worker
path, and the rework risk falls on Step 3's barrier code. Q02 and Q03 are
complete. Two decisions are missing:

- the default location of the managed 3.12 environment, which decides
  whether every new worktree fails its first day walk until set up
  (precedent: per-checkout `venvs/` with a runtime record);
- what groundhog does when the inherited binding names another project. It
  cannot read that project's `senv` selection, and the design forbids
  reusing the other one.

**Smaller items.** The Step 3 `senv.bat` change has no stated purpose once
Step 1's `pyproject.toml` exposes the directory to the own suite. A
negative search for `tools.pytest_plugins` imports would enforce the
canonical-name-only rule. The validation skeleton must follow whatever
moves between steps.

### Question verdicts for plan shared_lifecycle_gate round 1

All three plan questions carry proposed answers only; none has a user
decision.

- Q01 (real worker-barrier evidence before migration): agree with the
  question. Add Option A3, an executable xdist smoke from the existing
  Python 3.13 environment before Step 3, with Python 3.12 provisioning
  staying in Step 6. My choice is A3; A1 is acceptable but moves more work
  earlier than the evidence needs. Correct A2's con as described.
- Q02 (Windows shell transport owner): agree; B1 is also my choice.
- Q03 (tracked preflight declaration spelling): agree; C1 is also my
  choice. Its answer should also name the fixed project-relative
  entrypoint the preflight runs, and say that a declaration in a project
  without that entrypoint fails setup.
- Q04 (missing): default location of the managed Python 3.12 environment.
  My choice is D1, per checkout under `venvs/`, with the verified override
  for a shared environment.
- Q05 (missing): groundhog behavior when the inherited binding names
  another project. My choice is E1, stop before any spawn with a setup
  error.

Outstanding human decisions: Q01 to Q05.

### Requested changes for plan shared_lifecycle_gate round 1

Requested changes:

1. Move the static boundary to Step 1. In Step 1's `pyproject.toml` entry,
   add: "Set Ruff's `per-file-target-version` to `py310` for
   `tools/pytest_plugins/**` and a Pyright execution environment for that
   directory to Python 3.12, before the first standalone file exists." Remove
   those two items from Step 6's `pyproject.toml` entry, keeping the tracked
   applicability there. In Step 6, give any harness module that executes
   under the Python 3.12 interpreter a `py312` per-file target. Add to
   Step 1's analysis: "Until these targets exist, `check.bat` judges the
   files at the inferred py313 target, reports UP040/UP046 on
   3.10-compatible typing forms, and its suggested fixes introduce 3.12-only
   syntax."
2. In Step 6's `static_entry.py` entry and its tests, state the mechanism:

   > Syntax: Ruff's per-file `py310` target reports version-specific syntax
   > errors for the whole standalone files, or a real Python 3.10
   > interpreter parses them. `ast.parse(..., feature_version=(3, 10))`
   > under Python 3.13 is not sufficient: it accepts PEP 701 nested-quote
   > f-strings. Structure: an AST walk checks that only `sys` and `pytest`
   > imports, the version comparison and the identifying raise precede
   > refusal.

   Add a test with a nested-quote f-string that the check must reject.
3. Add a cost rule for in-process pytest sessions to item 2 of the shared
   execution checklist, and add the helper to Step 1's file list as
   `tests/unit/tools/shared_lifecycle/inline_session.py` (new, to be
   created):

   > Own-suite tests that run pytest in process use one shared helper:
   > `pytest.main` with an explicit plugin list, `-p no:cacheprovider`,
   > `PYTEST_DISABLE_PLUGIN_AUTOLOAD` set and `PYTEST_ADDOPTS` and
   > `LLM_SHARED_PYTEST_*` cleared through `monkeypatch`, and one small
   > generated project per lifecycle. A warm session of a one-test project
   > measured 0.125 to 0.156 s CPU with autoloaded plugins and 0.016 to
   > 0.031 s without, against the 0.1 s CPU ceiling.

4. In Step 4, after "Hash/cache only the loader;", add:

   > Preparation and groundhog's per-stage checks verify each selected
   > policy by file presence and by reading its module-level literal
   > contract constant with `ast`. They never import a policy into the
   > preparing process: groundhog runs Python 3.13, and an audit dispatcher
   > installed there would stay for its lifetime. Import preflight happens
   > only in the bootstrap, inside the project's pytest.

   In Steps 1 and 2, add: "Declare the loader-to-policy contract version as
   a module-level integer literal that Step 4 reads without importing."
5. In Step 5, replace the `tools/groundhog/runner.py` entry's "to be
   updated only where spawn merging needs it" with "to be updated: extend
   `StreamConfig.env_overrides` to express removal, for example
   `Mapping[str, str | None]`, with `run_streaming` removing `None` entries
   for the spawn and restoring them afterwards". Add tests for removal and
   restoration, and for deselection removing the loader entry, the owned
   variables and the policy path entries.
6. In the shared execution checklist, after the `<LLM_SHARED_DIR>`
   paragraph, add:

   > For Steps 5 to 7, run every walk with the groundhog of the checkout
   > being implemented. In a linked worktree, that checkout's `senv.bat`
   > sets `LLM_SHARED_DIR` to the worktree itself; the main checkout's
   > launcher does not contain the changed groundhog.

   In Step 6, add: "The preflight runs the harness and policy directory of
   the project under test through one fixed project-relative entrypoint,
   never the launching groundhog's own copy."
7. Q01: add this option after A2, and correct A2's con:

   ```md
   - Option A3: Run a minimal executable xdist barrier smoke from the
     existing llm-shared Python 3.13 environment before Step 3 migration,
     outside the audited suite; Step 6 adds the Python 3.12 environment,
     manifest and recurring preflight to the same harness.
     - pro: Checks real announcement ordering, cancellation and exit 4 where
       the barrier code is written, without moving provisioning; that
       ordering depends on pytest and xdist, which the 3.13 environment
       already pins.
     - con: Python 3.12 executable evidence still arrives in Step 6, and
       Step 3 must own the minimal runner, its scenario and its coverage
       tests.
   ```

   A2's con becomes: "Step 3's barrier code can complete on modeled worker
   behavior that later executable validation disproves; the own-suite
   migration itself never exercises the invalid-worker path."
8. Q03's answer: add "The preflight runs one fixed project-relative
   entrypoint; a declaration in a project without that entrypoint fails
   setup with an identifying diagnostic."
9. Add Q04 and Q05:

   ```md
   ### Q04: Where does the managed Python 3.12 environment live by default?

   Question description: The design settles a dedicated managed environment
   with a verified absolute override, but the plan does not name its
   default location. llm-shared runs day walks in many linked worktrees,
   and each checkout already carries its own `venvs/` runtime with a
   runtime record. Which default should `bin/lifecycle_compatibility.bat`
   provision and the preflight verify?

   #### BBQ for Q04

   Each kitchen can keep its own thermometer, or every kitchen can share
   one hanging in the hallway. In this picture: kitchens are llm-shared
   checkouts and worktrees, the thermometer is the Python 3.12
   environment, and the hallway is a machine-local shared location.

   #### Options for Q04

   - Option D1: Per checkout, under that checkout's `venvs/`, provisioned
     from that checkout's manifest; the verified absolute override may
     select any other prepared environment.
     - pro: Follows the existing per-checkout runtime convention, and a
       branch that changes the manifest affects only its own checkout.
     - con: Every new clone or worktree needs the explicit setup, or the
       override, before its first day walk can pass.
   - Option D2: One machine-local environment shared by all llm-shared
     checkouts, verified against each checkout's manifest before every
     preflight.
     - pro: One setup per machine; new worktrees validate immediately.
     - con: Checkouts with different manifest contents invalidate each other's
       environment and force reprovisioning, and the shared location adds
       a machine-level path contract.

   #### Recommended option for Q04 (with implementation arguments)

   Option D1: It matches how llm-shared already provisions per-checkout
   runtimes and keeps manifest changes branch-local. The override already
   covers machines that want one shared environment. The missing-environment
   diagnostic names both the setup command and the override.

   #### Answer to Q04: option D1 (proposed acceptance reason)

   Option D1: Accept if Step 6 names the per-checkout location, verifies an
   override against the checkout's own manifest, and documents the setup a
   new worktree needs in Step 7.

   User decision: pending

   ### Q05: What does groundhog do when the inherited binding names another project?

   Question description: Groundhog reads the selection from its
   environment, and `LLM_SHARED_PYTEST_ROOT` names the project that
   selection belongs to. When groundhog runs a project outside that root,
   it cannot read that project's own `senv` selection, and the design
   forbids reusing the other project's selection. Which outcome should
   Step 5 implement and test?

   #### BBQ for Q05

   A caterer arrives at a party holding another party's order sheet. In
   this picture: the order sheet is the inherited selection, the other
   party is the bound project, and the caterer is groundhog.

   #### Options for Q05

   - Option E1: Stop before any spawn with a groundhog setup error naming
     the bound root, the project root and the project's `senv.bat` to run.
     - pro: An opted-in project's selected enforcement never disappears
       silently; such a shell already resolves the other project's
       `pytest` through `PATH`.
     - con: Also blocks a project that selects nothing until the user
       starts that project's own prepared shell.
   - Option E2: Strip the owned entries for that run, spawn without a
     selection, and print one diagnostic line.
     - pro: Projects without a selection keep running from any shell.
     - con: An opted-in project run from another project's shell loses its
       selected enforcement for that run, with only a printed line.

   #### Recommended option for Q05 (with implementation arguments)

   Option E1: Automatic activation in every groundhog test stage must not
   depend on which shell started groundhog. A mismatched binding already
   means a misprepared shell, so stopping costs one `senv` call and keeps
   the outcome visible.

   #### Answer to Q05: option E1 (proposed acceptance reason)

   Option E1: Accept if Step 5 tests the mismatch for every stage and both
   collection probes, with no spawn and the existing setup-error reporting.
   An unprepared shell, with no binding, keeps running without a selection.

   User decision: pending
   ```

10. Smaller items: in Step 3, state what the `senv.bat` change does, since
    Step 1's `pyproject.toml` already exposes the directory to the own
    suite, or drop the entry. Add `rg -n 'tools\.pytest_plugins' tests tools`
    as a negative check in Step 3's completion, so tests import the
    policies only by canonical names.

### Writer instructions for plan shared_lifecycle_gate round 1

1. Apply the requested changes to Steps 1, 4, 5 and 6, the shared
   execution checklist, Q01 and Q03.
2. Add Q04 and Q05 in the plan's question format with
   `User decision: pending`. Record decisions only from the user's
   explicit choices.
3. Update the validation skeleton in the same change for every item moved
   between steps and every file added to a step.
4. Do not reopen requirement or design decisions. Request another
   automated review round covering the moved static boundary, the test-cost
   rule and the new questions. Do not consolidate or implement.

### Final reviewer decision for plan shared_lifecycle_gate round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-07T10:01:01+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan shared_lifecycle_gate (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Review round: 2

### Requestor assessment for plan shared_lifecycle_gate (round 2)

The initial seven-step implementation plan and aligned validation skeleton are
written beside the consolidated requirement and design. All proposed new paths
were checked as absent. Existing physical-line baselines were verified; the
633-line command module and standalone extraction constraints have explicit
split/consolidation guidance under the 650-line ceiling.

The writer assessment raises Q01-Q03, each with options, proposed answers and
explicit pending human decisions. Please assess the whole plan for missing
implementation questions and conflicting sequencing, not only these proposals.
In particular check early real xdist evidence versus Step 3 migration, Windows
shell transport ownership, and the precise tracked preflight declaration.

Requirement and design decisions Q01-Q10 are confirmed and consolidated. Do not
reopen their architecture or policy contracts. The separate validation file is
an unimplemented skeleton, not a second specification under review.

Original gate assertions, record continuity, no own-suite process exemptions,
all pytest spawn paths, immutable loader-only caching, canonical identity,
fresh day/direct-full compatibility including proof reuse, independent real
3.12 execution, 100% tools coverage and the anonymous two-context consumer trial
are explicit obligations. The pre-migration record snapshot is now owned by
Step 3 and reused in Step 7. Please identify any omitted file, package marker,
acceptance test or dependency ordering issue before implementation starts.

Round 1's concrete corrections are now applied: static targets move to Step 1;
the shared inline-session helper is a named Step 1 file; preparation uses source
presence and literal-contract AST checks without importing policies; runner
overrides express removal and restore previous state; self-hosted walks use the
implementing checkout; and preflight invokes the project-under-test's fixed
entrypoint. Syntax checks explicitly reject PEP 701 syntax rather than trusting
feature_version alone, with AST used separately for refusal structure. Step 6
also supplies supported static targets to its executable harness modules.

Q01 now includes A3, with revised recommendation and preserved initial A1
proposal history. Q03 identifies the fixed entrypoint. Added pending Q04
(per-checkout default environment location) and Q05 (mismatched project binding).
Q02 is unchanged. All five questions remain human-undecided. File ownership
changes contingent on those choices have not been applied as settled decisions;
the current seven-step skeleton is aligned with the current file lists.

The unnecessary Step 3 shell edit was removed: own-suite canonical discovery
comes from Step 1's pytest configuration; shell nonselection is read-only
evidence. Added a negative alias-import check and explicit Step 3 record
snapshot expectations in the validation skeleton. No implementation, staging,
commit or push is authorized by this continuation.

Resume verification removed a superseded duplicate Q01-Q03 question section.
The retained complete Q01-Q05 section exactly matches the companion; all five
human decisions remain pending and Q01's initial proposal remains as history.
The installed oqm append operation appended instead of replacing, so repeated
append was avoided. Markdown lint passes for all four planning documents.

### Change summary for plan shared_lifecycle_gate (round 2)

Initial plan review: added the seven-step implementation plan and matching
validation skeleton, plus consistent file-based IO clarifications in the
requirement and design. The writer risk pass verified path classifications and
line baselines, moved record snapshot/comparison before suite migration, and
added three genuinely pending implementation questions through oqm.

Since round 1, applied its ten requested correction groups to the plan and
matching validation expectations. Added inline_session.py as a planned Step 1
helper, moved standalone static targets to Step 1, clarified source-only
preparation, removal/restoration, self-hosting, fixed project-under-test entry,
and syntax-versus-refusal-structure checks. Removed the unnecessary Step 3 senv
edit. Expanded Q01 with A3 and preserved its original recommendation as history;
extended Q03 and added Q04-Q05 as pending human choices through oqm.

No step was renumbered. All implementation files remain uncreated/unchanged.
The settled requirement/design decisions are preserved.

Resume cleanup removed the superseded duplicate question section while
retaining the complete amended questions and their original proposal history.
Normalized the requirement IO addition to its existing LF format after the
whitespace check identified inserted CRLF lines.

### Writer response for plan shared_lifecycle_gate (round 2)

Writer response:

Accepted round 1's concrete corrections without disagreement. Static target
timing, syntax-check mechanism, nested-session cost isolation, source-only
preparation, environment removal/restoration, self-hosted launcher choice,
project-under-test harness resolution and the unnecessary senv edit are all
addressed. The validation skeleton reflects their current step ownership.

Accepted A3 as the revised proposed recommendation for Q01, retaining A1/A2
options and the initial A1 recommendation/answer as clearly marked history.
No human decision was inferred. Q04 and Q05 were added with complete options,
pros/cons, recommendations and explicit pending markers. The resulting plan has
five undecided implementation questions. Changes to earlier harness file
ownership remain contingent on the human's Q01 choice, as documented in that
answer, rather than being silently incorporated as a settled decision.

Please assess the complete amended plan and all five pending questions for
convergence, particularly the static/test-cost corrections and whether the new
questions leave any concrete implementation gaps. Do not reopen the settled
requirement/design or interpret recommendations as authorization to implement.

### Reviewer focus for plan shared_lifecycle_gate (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-07T10:07:03+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan shared_lifecycle_gate round 2

I read the complete revised plan (SHA-256
`f8cb5726ed0626422a25585c55201780ff1bfd8585ccb0e2bb99227926fd06ca`) and the
round 2 request, and spot-checked the validation skeleton for the moved
items.

**Every round 1 change is applied as requested.**

- Static boundary: Step 1 sets Ruff's `py310` per-file target and the
  Pyright 3.12 environment before the first standalone file. Its analysis
  explains the UP040/UP046 hazard. Step 6 adds `py312` targets for harness
  modules that run under the separate interpreter.
- Syntax check: whole-file 3.10 syntax uses Ruff's `py310` errors or a real
  3.10 interpreter, with a PEP 701 regression. An AST walk checks only the
  pre-refusal structure.
- Test cost: `inline_session.py` is a named Step 1 file, and the checklist
  states its isolation rules and the measured costs.
- Preparation reads policy presence and literal contract constants without
  importing them. Steps 1 and 2 declare those constants after the guard.
- Groundhog: `StreamConfig.env_overrides` gains removal with restoration,
  including spawn failure, and Step 5 tests it.
- Self-hosting: Steps 5 to 7 run the implementing checkout's groundhog. The
  preflight runs the project-under-test's fixed `bin/lifecycle_compatibility.bat`.
- The Step 3 `senv.bat` edit is gone. The negative
  `tools.pytest_plugins` alias search is in Step 3's completion.
- The validation skeleton carries each moved item in its new step.

**The five questions are complete.** Q01 now has A3 as its recommendation,
and A2's con is corrected. The earlier A1 proposal is kept as marked
history. Q03 names the entrypoint. Q04 and Q05 have distinct options,
consequences and acceptance conditions. All five are marked pending, and the
contingent file-list changes for Q01 and Q05 are correctly left for after
the user decides.

**Three precisions remain, all wording.**

- The checklist says to "keep policy registration and coverage state
  isolated from the carrying session". Many plugin hooks only run inside
  those inline sessions. An implementer who stops or isolates coverage
  there would lose the measurement the 100% `tools` gate needs. The inner
  session loads no pytest-cov because autoload is off, so the carrying
  session's coverage keeps measuring the policy code. The sentence should
  say that.
- Step 6 asks for a PEP 701 regression "which the check must reject", but
  the process-free suite cannot start Ruff or another interpreter. The
  regression belongs where the syntax check runs.
- Q04's D1 path is safe from the existing launchers only by accident of its
  name. Twelve `bin` launchers take the newest `venvs\python_3*llm-shared*`
  directory by date, and nine take `venvs\python_3*` in descending name
  order. `python_3.12_lifecycle_compatibility` contains no `llm-shared` and
  sorts below `python_3.13.9_...`, so neither group would pick it. A name
  following the per-checkout runtime convention would contain the checkout
  name, `llm-shared...`. The twelve date-sorted launchers would then pick
  the 3.12 environment the moment it was created. D1 and Step 6 should
  state that constraint.

No question is missing and no requirement or design decision is reopened.
The remaining edits are wording only, so the formulation can converge.

### Question verdicts for plan shared_lifecycle_gate round 2

All five plan questions carry proposed answers only; none has a user
decision.

- Q01 A3: agree; it is my choice. Real announcement ordering is checked in
  Step 3 without moving Python 3.12 provisioning forward.
- Q02 B1: agree; it is my choice.
- Q03 C1: agree; it is my choice, now with the fixed project-relative
  entrypoint.
- Q04 D1: agree; it is my choice. Add the launcher-glob naming constraint
  in the covered wording.
- Q05 E1: agree; it is my choice.

Outstanding human decisions: Q01 to Q05. Once Q01 and Q05 are decided,
their contingent file-list changes still need writing into the plan.

### Convergence evidence for plan shared_lifecycle_gate round 2

Covered wording:

1. Shared execution checklist, item 2: replace "keep policy registration
   and coverage state isolated from the carrying session." with "keep
   policy registration isolated from the carrying session. The inner
   session loads no pytest-cov, so the carrying session's coverage still
   measures the policy code it runs."
2. Step 6: replace "Add a regression containing that syntax which the check
   must reject." with "Add a regression containing that syntax which the
   check must reject, and run it where the syntax check executes (Ruff in
   `check.bat` or the executable harness), because the process-free suite
   cannot start Ruff or another interpreter."
3. Q04 option D1, after "can select any other equivalent prepared
   environment.", and the matching Step 6 location sentence once Q04 is
   decided: add "The directory name must not contain `llm-shared` and must
   sort below the main runtime: twelve `bin` launchers take the newest
   `venvs\python_3*llm-shared*` directory by date, and nine take
   `venvs\python_3*` in descending name order."

Convergence rationale:

Every round 1 correction is applied in the plan and carried into the
validation skeleton. The static boundary now precedes the first standalone
file, the 3.10 syntax check uses a mechanism that rejects PEP 701 syntax,
and in-process sessions have an isolation and cost rule. Preparation never
imports policies, groundhog can remove variables, and self-hosted steps run
the groundhog being changed. The five questions are complete, with distinct
options and reasoned proposed answers. The remaining edits are the covered
wording, which changes no mechanism. The next step belongs to the human:
decide Q01 to Q05. A follow-up review of those decisions and their
contingent changes is needed before consolidation. This recommendation is
advisory and does not authorize consolidation or implementation.

### Writer instructions for plan shared_lifecycle_gate round 2

1. Apply the covered wording in the shared execution checklist, Step 6 and
   Q04. It does not need another automated round.
2. Present Q01 to Q05 to the user and record each decision only from the
   user's explicit choice.
3. After the decisions, apply their contingent changes: Step 3 file
   ownership and validation for the Q01 choice, and Step 5's mismatch
   outcome for the Q05 choice. Then request a follow-up review of those
   decisions and changes before consolidation.
4. Do not consolidate or implement.

### Final reviewer decision for plan shared_lifecycle_gate round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-07T22:59:53+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: The user's explicit selections are Q01=A3, Q02=B1, Q03=C1, Q04=D1 and Q05=E1.
The user requested: "B1, but do update all docs to describe that pytest plugin
mechanism, and do read the updated \"explain undecided questions\" instructions
in ..\llm-shared to better introduce your question explanations".

Review those recorded decisions, the contingent plan/validation changes and
the plugin introductions across all five active effort documents. Identify
inconsistencies, effects on earlier decisions and related documents, and any
missing or new questions. This follow-up is authorized by the user's selection
of explanation; consolidation, implementation and commits are not authorized.

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-07T23:00:05+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan shared_lifecycle_gate (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Review round: 3

### Requestor assessment for plan shared_lifecycle_gate (round 3)

The five plan questions now have explicit human decisions: Q01=A3,
Q02=B1, Q03=C1, Q04=D1 and Q05=E1. A successful full decision scan found
five confirmed questions, zero undecided questions and no diagnostics.
All question blocks, options, recommendations and proposal history remain.
The round 2 convergence predates these decisions and the contingent edits;
this replacement review is required before any consolidation.

The writer considers the chosen options sufficient and sees no additional
question at present. Please independently assess the full specification for
missing questions, consistency with earlier confirmed requirement/design
decisions, and effects on related documents. Human decisions cannot be
overwritten by reviewer preferences; identify any conflict explicitly.

Q01 moves the minimal real Python 3.13 xdist barrier smoke before Step 3
suite migration, outside the audited suite. Step 3 now owns the runner,
scenarios, package markers, process-free coverage tests and static targets.
Step 6 extends those existing files for independent Python 3.12 evidence,
its separate manifest/environment and recurring preflight. Check that no
dependency ordering, file inventory, coverage or completion gap remains.

Q02 assigns Windows serialization, escaping and temporary-output cleanup to
`tools/pytest_plugin_shell.py`, consuming the common builder result. Q03
fixes `[tool.llm-shared.lifecycle-compatibility]` with literal `enabled = true`,
strict shape/type validation and the fixed adjacent harness entrypoint.
Q04 uses checkout-local `venvs/python_3.12_lifecycle_compatibility/`, explicit
provisioning from that checkout's manifest and a verified absolute override.
Q05 stops every groundhog pytest stage and both collection probes before
any child spawn on cross-project inherited binding, with both roots and
target setup in the diagnostic. The parent environment remains unchanged;
no-binding and same-project refresh behavior remain supported.

The three covered wording corrections from round 2 are applied: carrying
coverage continues measuring inline policy execution, the PEP 701 regression
runs at the syntax-check boundary, and compatibility-environment naming
avoids accidental selection by existing runtime launchers.

The user also requested explanations of the pytest plugin mechanism in all
active effort documents. Review these introductions in the draft, requirement,
design, plan and validation file. They explain why hooks are needed, preparation
without policy imports, Windows parent-shell transfer, actual child pytest
loader registration, direct groundhog child environments, own-suite loading
after coverage starts and the separate executable compatibility harness.
Check that this prose consistently introduces the mechanism without changing
settled contracts. Historical review transcripts remain evidence.

The five edited effort documents pass focused Markdown checks, their 46 local
links/anchors resolve, and whitespace checks pass. The earlier repository-wide
Markdown run found existing MD032 in the historical requirement review at
line 1110, outside these edits; no repository-wide pass is claimed. No code
implementation, consolidation, staging, commit or push has occurred.

### Change summary for plan shared_lifecycle_gate (round 3)

Since round 2 convergence:

- Recorded explicit human decisions Q01=A3, Q02=B1, Q03=C1, Q04=D1 and Q05=E1
  in the existing plan answer sections, preserving all options and history.
- Aligned Step 2 readiness, Step 3 file ownership/static/coverage obligations,
  Step 6 extension ownership and rollout with real Python 3.13 xdist barrier
  evidence before Step 3 suite migration. The seven-step sequence remains.
- Added the separate Step 4 shell transport module and focused test package,
  package marker, baselines, static targets and process-free coverage duties.
- Specified Step 6's exact tracked TOML spelling, literal boolean validation,
  absent/false and malformed cases, and fixed project-relative entrypoint.
- Specified the checkout-local Python 3.12 environment default, checkout-owned
  manifest, explicit setup, verified absolute override, branch isolation,
  version/dependency checks and launcher naming safeguards.
- Applied E1 to Step 5 all stages and both collection probes: cross-project
  inherited binding fails setup before any spawn, with identifying diagnostics
  and unchanged parent environment. Preserved no-binding and same-project paths.
- Aligned the paired validation skeleton and Step 7 adoption/setup documentation
  obligations with each selected decision.
- Introduced pytest plugins and the complete runtime flow across the five active
  effort documents: `draft.v0.14.0.shared_lifecycle_gate.md`,
  `feature-request.v0.14.0.shared_lifecycle_gate.md`,
  `design.v0.14.0.shared_lifecycle_gate.md`,
  `plan.v0.14.0.shared_lifecycle_gate.md` and
  `plan.v0.14.0.shared_lifecycle_gate.validation.md`, all in `docs/v0.14.0/`.
- Applied the round 2 covered wording on inline coverage, the syntax-check
  regression execution boundary and runtime-launcher environment selection.

The current reviewed plan SHA-256 is
`81d7ecec53f9a2b39eb53caf78258f63b6ed9c1f4bff8ef2f3b672605fc8ff39`.

### Human guidance and writer response for plan shared_lifecycle_gate (round 3)

Human guidance:

The user's explicit selections are Q01=A3, Q02=B1, Q03=C1, Q04=D1 and Q05=E1.
The user requested: "B1, but do update all docs to describe that pytest plugin
mechanism, and do read the updated \"explain undecided questions\" instructions
in ..\llm-shared to better introduce your question explanations".

Review those recorded decisions, the contingent plan/validation changes and
the plugin introductions across all five active effort documents. Identify
inconsistencies, effects on earlier decisions and related documents, and any
missing or new questions. This follow-up is authorized by the user's selection
of explanation; consolidation, implementation and commits are not authorized.

Writer response:

Round 2's three covered wording corrections were accepted and applied. The
user then explicitly selected all five recommended options during the retained
question-explanation discussion. There is no writer/reviewer disagreement.

The contingent Q01 and Q05 changes requested in round 2 are now written into
the plan and validation skeleton. Q02-Q04 details and documentation obligations
are also concrete. Please verify the changed document and the related effort
documents as a whole, including effects on previously settled decisions and
any missing or newly raised implementation questions.

The user's comments showed that the plugin mechanism and wider project flow
needed better introduction. All five active effort documents now introduce
those notions at their own level. Please review those additions as part of
this round, rather than treating the old convergence as covering them.

The user authorized this independent follow-up by selecting explanation.
Consolidation remains unauthorized. Preserve all question blocks and explicit
human decisions throughout review; report conflicts instead of silently
replacing a choice. No implementation or commits are requested.

### Reviewer focus for plan shared_lifecycle_gate (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-07T23:13:44+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan shared_lifecycle_gate round 3

I read the complete revised plan (SHA-256
`81d7ecec53f9a2b39eb53caf78258f63b6ed9c1f4bff8ef2f3b672605fc8ff39`), the
validation skeleton, the round 3 request and the plugin introductions added
to the draft, requirement and design.

**The decisions are recorded faithfully.** Q01=A3, Q02=B1, Q03=C1, Q04=D1
and Q05=E1 each carry the user's confirmation, date and adopted acceptance
reason. Options, recommendations and the A1 history remain.

- Step 3 owns the minimal runner, scenarios, package markers, process-free
  coverage tests and Python 3.12 static targets; Step 6 extends them.
- Step 4 lists the shell transport module and its test package with
  zero-line baselines.
- Step 6 names the exact TOML table, the literal boolean, the fixed
  entrypoint and the checkout-local environment with its verification.
- The validation skeleton carries each item into the matching step, and
  the round 2 covered wording is applied.

**The plugin introductions are consistent.** The draft, requirement,
design, plan and validation file describe one route: selection in
`senv.bat`, source-only preparation, Windows transfer of a complete result,
the loader inside the project's pytest, and groundhog's direct child
environment. None changes a settled contract. The design's transfer
character list follows from preserving unrelated entries (design Q02) and
publishing no partial activation (design Q08). The design should say so,
so that it does not read as a new decision.

**One gap against a recorded decision.** Q05=E1 says groundhog stops
"before any child spawn", and Step 5 asks tests for zero spawns. But Step 5
applies the check per pytest stage and collection probe. In a day walk,
`walk` in `tools/groundhog/day.py` runs `check.bat` first. That runs
`ruff check --fix`, which may rewrite sources, and Step 6 adds the Python
3.12 harness before the saved-proof return. With a per-stage check, a shell
bound to another project rewrites sources and runs the harness before the
error appears. The check belongs at invocation setup. That moves a check
and changes what a saved-proof day does in such a shell, so it needs
another automated round.

**Two precisions change what Step 4, Step 5 and Step 7 test.**

- "Different project" needs a predicate. Groundhog's preparation rebinds
  the root to its own target, `invocation.root` from `find_project_root`.
  Accepting any other root, a nested project included, would carry the
  bound project's selection over to it. A string-prefix comparison would
  also treat `llm-shared_shared_lifecycle_gate` as inside `llm-shared`. The
  loader's containment rule is a separate check: it accepts a pytest
  rootdir inside the bound project.
- The Windows transfer depends on the calling shell's delayed-expansion
  state. I applied `set "PROBE_X=a!b^c%%d"` from a called batch file. With
  delayed expansion off the value was `a!b^c%d`; with it on, `abc%d`.
  Step 4's escaping and Step 7's executable evidence must cover both states.

**Wording.**

- My round 2 launcher count was incomplete. Besides the twelve `bin`
  launchers, `rvw_status.bat`, `markdown-check.bat` and
  `commit-plan-check.bat` at the root also take the newest
  `python_3*llm-shared*` directory by date. `bin/mds.ps1` sorts `python_3*`
  by name, like the nine. D1's name is still safe for all of them.
- The planning-baseline table describes the requirement and design edits
  as the IO clarification only, and omits the draft (85 lines at
  `eda8f5e`).
- The validation runtime section says `senv.bat` "calls the environment
  builder". It calls `bin/prepare_pytest_plugins.bat`, whose shell adapter
  uses the builder.

No new question is needed. The consequences of the E1 placement follow
from the user's recorded wording.

### Question verdicts for plan shared_lifecycle_gate round 3

All five plan questions carry explicit user decisions. None conflicts with
an earlier requirement or design decision.

- Q01 A3: agree; it is my choice. The Step 3 and Step 6 file ownership
  matches the decision.
- Q02 B1: agree; it is my choice. Its tests must cover both caller
  delayed-expansion states (requested change 3).
- Q03 C1: agree; it is my choice. The spelling, validation and entrypoint
  are complete.
- Q04 D1: agree; it is my choice. Correct the launcher count in the option
  text (requested change 4).
- Q05 E1: agree; it is my choice. The plan does not yet implement "before
  any child spawn" for day and full invocations, and "different project"
  needs a predicate (requested changes 1 and 2).

Outstanding human decisions: none for Q01 to Q05. Blocking check-only
commands as well would be a new decision. Consolidation remains a
separate human choice.

### Requested changes for plan shared_lifecycle_gate round 3

Requested changes:

1. Step 5, Q05=E1 paragraph: replace the sentence "For Q05=E1, when an
   inherited `LLM_SHARED_PYTEST_ROOT` binds selection to a different
   project, stop with the existing setup-error reporting before any child
   spawn." with:

   > For Q05=E1, check the inherited binding once at invocation setup,
   > before any child spawn: before `check.bat`, Step 6's compatibility
   > preflight and any saved-proof or upgrade decision. Apply it to every
   > command that can start a pytest stage or collection probe: day, full,
   > affected, single and timings. Commands that never start pytest keep
   > their current behavior. Report it with the existing setup-error
   > contract. Per-stage preparation verifies the binding again.

   Replace "Tests assert zero spawns and unchanged parent settings on every
   cross-project mismatch." with:

   > Tests run a whole day and a direct full in a shell bound to another
   > project. They observe zero spawns, `check.bat` and the harness
   > included, unchanged sources and parent environment, and a setup error
   > in place of a saved-proof no-op. Separate tests cover each pytest stage
   > and both collection probes.

2. Step 5, same paragraph: after "Name the bound root, target root and
   target project's environment setup action.", add:

   > A different project means the normalized bound root differs from
   > groundhog's resolved project root, `invocation.root`. Compare whole
   > paths, case-insensitively on Windows, never by string prefix. A nested
   > project and a sibling such as `llm-shared_shared_lifecycle_gate`
   > beside `llm-shared` are different projects, because groundhog's
   > preparation rebinds the root to its own target. The loader's separate
   > containment rule still accepts a pytest rootdir inside the bound
   > project.

   In Step 5's tests, add nested-project and shared-prefix sibling cases
   beside the same-root refresh case.

3. Step 4, Q02=B1 paragraph: after "failure before application and
   cleanup of transfer-owned temporary output.", add:

   > The calling shell's delayed-expansion state changes how an applied
   > `set` line reads its value: with it on, `!` and `^` are consumed.
   > Make the transfer independent of that state or detect it, and cover
   > both states in the focused tests.

   Change "Keep actual calling-shell execution in Step 7's existing
   acceptance harness." to "Keep actual calling-shell execution, with
   delayed expansion off and on, in Step 7's existing acceptance harness."

4. Q04 option D1 and the Step 6 location sentence. Replace "twelve `bin`
   launchers take the newest `venvs\python_3*llm-shared*` directory by
   date, and nine take `venvs\python_3*` in descending name order." with:

   > fifteen launchers take the newest `venvs\python_3*llm-shared*`
   > directory by date (twelve in `bin`, plus `rvw_status.bat`,
   > `markdown-check.bat` and `commit-plan-check.bat` at the root), and ten
   > take `venvs\python_3*` in descending name order (nine `bin` batch
   > files and `bin/mds.ps1`).

   In Step 6, change "verify existing launchers retain the Python 3.13
   runtime" to "verify those launchers, the root ones and `bin/mds.ps1`
   included, retain the Python 3.13 runtime".

5. Step 6 tests: change "each invocation runs fresh preflight before proof
   reuse" to "each invocation runs Step 5's binding check, then fresh
   preflight, before proof reuse".

6. Validation skeleton:
   - Step 4: add "Cover both caller delayed-expansion states in focused
     tests and in the Step 7 executable evidence."
   - Step 5, Q05=E1 bullet: replace "reject inherited bindings to a
     different project before any child spawn" with "reject inherited
     bindings to a different project at invocation setup, before
     `check.bat`, the compatibility preflight and saved-proof reuse,
     comparing whole normalized roots with `invocation.root`". Add nested
     and shared-prefix sibling roots to its cases.
   - Step 6: add "Order Step 5's binding check, the preflight, then proof
     reuse or spawning." Extend the D1 launcher check to the root
     launchers and `bin/mds.ps1`.
   - Step 7: add "Apply the shell result in callers with delayed expansion
     off and on."
   - Runtime section: replace "project `senv.bat` selects the checks and
     calls the environment builder" with "project `senv.bat` selects the
     checks and calls `bin/prepare_pytest_plugins.bat`, whose shell adapter
     uses the environment builder".

7. Design, after "preparation failure must not expose partial new
   settings.", add: "These follow from preserving unrelated environment
   entries (Q02) and publishing no partial activation (Q08); they add no
   design decision."

8. Plan configuration and documentation baselines: change the planned use
   of the requirement and design rows to "IO clarification and pytest
   plugin introduction added during planning". Add
   `docs/v0.14.0/draft.v0.14.0.shared_lifecycle_gate.md` with 85 lines and
   "Pytest plugin introduction added during planning".

### Writer instructions for plan shared_lifecycle_gate round 3

1. Apply the requested changes to the plan, the validation skeleton and
   the one design sentence. Keep every question block and recorded user
   decision unchanged.
2. Tell the user two consequences of E1's recorded wording. A saved-proof
   day in a shell bound to another project now fails instead of returning
   a no-op. A nested project counts as a different project. If the user
   wants either outcome changed, record that only from their explicit
   decision, as a new decision.
3. Then request another automated review round. Do not consolidate or
   implement.

### Final reviewer decision for plan shared_lifecycle_gate round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-07T23:17:41+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan shared_lifecycle_gate (round 4)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Review round: 4

### Requestor assessment for plan shared_lifecycle_gate (round 4)

All eight round 3 requested changes are accepted and applied. The five human
decisions remain Q01=A3, Q02=B1, Q03=C1, Q04=D1 and Q05=E1. The full scanner
still finds five confirmed questions, zero undecided questions and no
diagnostics. Existing question blocks and decision records remain intact.
The writer sees no missing question and no conflict with earlier decisions;
please independently verify the full plan and related documents again.

E1 now runs at invocation setup before any child spawn, static checks,
compatibility preflight, saved-proof return or upgrade decision. Per-stage
preparation checks again. The target is the whole normalized `invocation.root`,
compared case-insensitively on Windows. Nested projects and shared-prefix
siblings are distinct; the loader retains its separate containment rule.
Whole-day/direct-full tests require zero spawns, unchanged sources and parent
environment, including saved-proof and detached-day paths. Commands that never
start pytest retain their behavior. CLI ownership and focused CLI/whole-day
test files are now listed, with measured 553/536/310-line baselines. The CLI
keeps only a small adapter call; its 553 lines put it in the at-risk band.

Step 4's focused transport tests and Step 7's executable evidence now cover
caller delayed expansion both off and on, preserving transfer values and
atomic failure behavior. D1's launcher inventory now includes the root batch
launchers and `bin/mds.ps1`. Step 6 orders binding validation, fresh preflight,
then proof reuse or spawning. The validation skeleton mirrors these duties.

The design now attributes the transfer character preservation and atomicity
to existing Q02/Q08 contracts. The planning-baseline table includes the draft
and the plugin introductions; the validation runtime names the shell launcher
and adapter explicitly. The five plugin introductions remain in scope for
cross-document consistency and missing/new-question review.

The user was told the two E1 consequences requested in round 3: a saved-proof
day in another project's bound shell fails rather than returning no-op; a
nested project counts as different. No request to change either was received.
These follow from E1, rather than constituting newly invented user decisions.

Focused Markdown checks pass for all five active effort documents and all 46
local links/anchors; Git whitespace checks pass. No code implementation,
consolidation, staging, commit or push has occurred.

### Change summary for plan shared_lifecycle_gate (round 4)

Since round 3:

- Moved E1 from per-stage-only handling to invocation setup before all children,
  `check.bat`, compatibility preflight and proof/upgrade decisions. Retained
  per-stage checks and unchanged behavior for commands that never start pytest.
- Defined different-project identity using whole normalized roots and Windows
  case handling; added nested-project/shared-prefix sibling cases and preserved
  the loader's distinct containment rule.
- Added whole-day/direct-full zero-spawn, unchanged-source/parent tests,
  saved-proof setup failure and detached-day coverage. Listed the CLI adapter
  call and CLI/whole-day test ownership, baselines and line-budget duties.
- Required delayed-expansion off/on focused shell transport tests and real
  Step 7 calling-shell evidence.
- Corrected D1's runtime-launcher counts and expanded checks to root launchers
  and `bin/mds.ps1`.
- Ordered Step 5's binding check before Step 6 preflight and proof reuse.
- Mirrored all obligations in the validation skeleton and corrected its runtime
  introduction to name `bin/prepare_pytest_plugins.bat` and the shell adapter.
- Added the design attribution to settled Q02/Q08 and corrected the plan's
  documentation-baseline descriptions and draft inventory.

Reviewed plan SHA-256:
`beb95e69013382450ac94b48a614d7a86bdb15584833449c61aad7d076849dc7`.

### Human guidance and writer response for plan shared_lifecycle_gate (round 4)

Human guidance:

The user's explicit selections are Q01=A3, Q02=B1, Q03=C1, Q04=D1 and Q05=E1.
The user requested: "B1, but do update all docs to describe that pytest plugin
mechanism, and do read the updated \"explain undecided questions\" instructions
in ..\llm-shared to better introduce your question explanations".

Review those recorded decisions, the contingent plan/validation changes and
the plugin introductions across all five active effort documents. Identify
inconsistencies, effects on earlier decisions and related documents, and any
missing or new questions. This follow-up is authorized by the user's selection
of explanation; consolidation, implementation and commits are not authorized.

Writer response:

Accepted all round 3 feedback; there is no disagreement. E1's recorded
before-any-spawn requirement now includes the complete invocation rather
than only pytest stages. The plan explicitly protects saved-proof and
detached-day routes and distinguishes exact target identity from the
loader's containment rule. The newly listed CLI seam follows the existing
entrypoint and delegates binding logic to the environment adapter.

Both requested E1 consequences were explained to the user. The human decisions
and their question blocks remain unchanged. Check-only commands retain their
current behavior; extending E1 to them would require a separate decision.

The delayed-expansion evidence, launcher corrections and related documentation
changes are applied in the plan and validation skeleton. Please verify these
changes, their earlier-decision compatibility and whether any question is
missing. Consolidation and implementation remain unauthorized.

### Reviewer focus for plan shared_lifecycle_gate (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-07T23:24:51+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan shared_lifecycle_gate round 4

I read the revised plan (SHA-256
`beb95e69013382450ac94b48a614d7a86bdb15584833449c61aad7d076849dc7`), its
changed sections in full, the validation skeleton, the design attribution
sentence and the round 4 request.

**Every round 3 change is applied as requested.**

- Q05=E1 now runs once at invocation setup, before `check.bat`, the
  compatibility preflight and any saved-proof or upgrade decision, for day,
  full, affected, single and timings. Per-stage preparation checks again.
  I confirmed the new seam in `tools/groundhog/cli.py`: before the
  detached-day branch, `main` only parses arguments, resolves the root,
  level and scope and checks for a live run, and none of these starts a
  process. Those five commands are the only groundhog commands that start
  pytest; `check`, `init`, `exclude`, `status` and `groups` do not.
- "Different project" compares whole normalized roots with
  `invocation.root`, with nested-project, shared-prefix sibling and
  same-root refresh cases. The loader's containment rule stays separate.
- Whole-day and direct-full tests assert zero spawns, unchanged sources and
  parent environment, a setup error in place of a saved-proof no-op, and
  the detached-day route.
- The new baselines are correct: `cli.py` 553 (at risk),
  `test_groundhog_cli.py` 536 and `test_groundhog_acceptance_day.py` 310.
- Step 4 and Step 7 cover both caller delayed-expansion states.
- D1's launcher inventory, Step 6's ordering, the design attribution, the
  baseline table and the validation runtime section are corrected.
- The validation skeleton mirrors each item.

**The decisions and their records are unchanged**, and the two E1
consequences were reported to the user without a request to change them.

**What remains is wording.**

- The code-facts section still says the plan avoids "growing the CLI",
  but Step 5 now adds a small call there.
- Step 5's whole-day test names "the harness", which exists only from
  Step 6.
- Q05's question description says "outside that root", which no longer
  matches the whole-root predicate.
- One validation bullet calls `bin/mds.ps1` a root launcher.
- Two paragraphs have ragged line breaks.

No question is missing, and no earlier decision is reopened. The plan can
converge.

### Question verdicts for plan shared_lifecycle_gate round 4

All five plan questions carry explicit user decisions. None conflicts with
an earlier requirement or design decision, and the plan now implements each
as recorded.

- Q01 A3: agree; it is my choice.
- Q02 B1: agree; it is my choice. Both delayed-expansion states are
  covered.
- Q03 C1: agree; it is my choice.
- Q04 D1: agree; it is my choice. The launcher inventory is complete.
- Q05 E1: agree; it is my choice. The invocation-setup check now meets
  "before any child spawn". Align the question description with the
  whole-root predicate (covered wording 3).

Outstanding human decisions: none for Q01 to Q05. Consolidation remains a
separate human choice.

### Convergence evidence for plan shared_lifecycle_gate round 4

Covered wording:

1. Confirmed code and test facts: replace "but this plan places new
   orchestration in focused modules rather than growing the CLI." with
   "but this plan places new orchestration in focused modules; the CLI
   gains only Step 5's binding-check call."
2. Step 5, whole-day test sentence: replace "They observe zero spawns,
   `check.bat` and the harness included," with "They observe zero spawns,
   `check.bat` included (Step 6 adds its harness to the same assertion),".
3. Q05 question description: replace "When groundhog runs outside that
   root, it cannot read the target project's own shell selection." with
   "When groundhog targets any other project root, a nested one included,
   it cannot read that project's own shell selection." The decision text
   stays unchanged.
4. Validation skeleton, Step 6 D1 bullet: replace "including the root
   `rvw_status.bat`, `markdown-check.bat`, `commit-plan-check.bat` and
   `bin/mds.ps1`" with "including the root launchers `rvw_status.bat`,
   `markdown-check.bat` and `commit-plan-check.bat`, and `bin/mds.ps1`".
5. Rewrap the Step 5 line-budget addendum ("New adapter," alone on a line)
   and the Step 6 tests paragraph ("Direct full runs it" / "once;").

Convergence rationale:

Every round 3 change is applied, and the plan now implements all five
recorded decisions. Q05=E1 runs at invocation setup before any child spawn,
through a CLI seam that starts no process before it. It has a defined
whole-root predicate, and whole-day, saved-proof and detached-day tests
cover it. The shell transfer covers both delayed-expansion states, and the
launcher inventory is complete. The remaining edits are the covered
wording, which changes no mechanism, file list or test obligation. No
question is missing, and no earlier decision is reopened. This
recommendation is advisory and does not authorize consolidation or
implementation.

### Writer instructions for plan shared_lifecycle_gate round 4

1. Apply the covered wording in the plan and validation skeleton. It does
   not need another automated round.
2. Keep every question block and recorded user decision unchanged.
3. Present the convergence recommendation to the user. Consolidation is
   their separate choice. Do not consolidate or implement without it.

### Final reviewer decision for plan shared_lifecycle_gate round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-07T23:41:11+01:00
- Exchange: specification/plan/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
