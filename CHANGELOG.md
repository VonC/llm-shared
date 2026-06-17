# LLM-Shared workflow tools

Shared instructions, skills, scripts, and Python tools that drive an LLM
project from a raw idea through requirement, design, plan, and a tagged
release. The groundhog test loop (ghog), the prompt-workflow cycle (pw),
and the commit and changelog helpers are mutualized across sibling
projects.

## [v0.3.0-SNAPSHOT unreleased] One call gets a pass, the suite does not - 7fe3997af9a18774ae49a195cb1ba079e42ffc5b

the [exclusion] section spares a slow test without raising line 2

- A baseline that only ratchets down
  -- 2s slower restores on exit 8; 2s faster lowers the recorded time
- ghog exclude beats raise-the-floor
  -- one command records the call at its measured time, floor lines stay yours

v0.3.0 lets ghog full accept one legitimately-slow test call without
raising the floor for every other test. a.ghog.outliers gains an optional
[exclusion] section: each entry names a test node id and the call time
recorded as its baseline. A full run spares an excluded call from the
outlier rule and from the avg=, so accepting one slow call changes nothing
for the rest of the suite, and the floor lines (1 and 2) stay user-owned.

Each excluded call is held to its recorded baseline within two seconds.
A call more than two seconds slower has drifted: the run returns exit 8
with excluded=1, and the fix is to bring it back within two seconds of the
recorded time, not to push it below the floor. A call more than two seconds
faster has the tool lower the baseline to the new time -- it only ratchets
down -- and once the call falls below the floor the entry is removed. A
test that no longer runs is dropped as stale. The ghog exclude <node>
<seconds> command writes the section, so the list stays right with no
hand-editing.

### Key changes (v0.3.0)

- **The [exclusion] section, spared and not averaged**: a.ghog.outliers
  carries an optional [exclusion] section after the two floor lines, each
  entry a test node id and its recorded baseline seconds. A full run drops
  an excluded call from the outliers and from avg=, so one accepted slow
  call moves neither the gate nor the average for the rest of the suite.

- **A two-second baseline, exit 8 on slower drift**: each excluded call is
  held to its recorded time within two seconds. More than two seconds
  slower keeps an otherwise-green run on exit 8 with excluded=1 and a
  restore-to-baseline instruction; more than two seconds faster ratchets
  the recorded time down only, and a call back under the floor or a test
  that no longer runs has its entry removed.

- **ghog exclude, the tool-managed writer**: ghog exclude <node> <seconds>
  records one must-stay-slow call at its measured time, the only writer of
  the section, so the floor lines (1 and 2) stay user-owned. The exit-8
  hint and the fix_slow_test.md guidance now point here instead of raising
  line 2 for one call.

### 🚀 Features (v0.3.0)

- *(ghog)* Read and write the exclusion section
- *(ghog)* Spare excluded calls and measure drift
- *(ghog)* Wire exclusions into run and report
- *(ghog)* Exit 8 on drift, report excluded
- *(ghog)* Add the exclude subcommand
- *(groundhog)* Per-test duration exclusions

### 📚 Documentation (v0.3.0)

- *(duration_outliers)* Let pw drive v0.3.0
- *(duration_outliers)* Trim trailing spec newline
- *(duration_outliers_exclusion)* Record step 1 validation
- *(duration_outliers_exclusion)* Record step 2 validation
- *(duration_outliers_exclusion)* Record step 3 validation
- *(duration_outliers_exclusion)* Record step 4 validation
- *(ghog)* Exclude one slow call, not line 2
- *(duration_outliers_exclusion)* Record step 5 validation
- *(duration_outliers_exclusion)* Record step 6 validation

### 🧪 Testing (v0.3.0)

- *(ghog)* Cover excluded and drifted runs

### ⚙️ Miscellaneous Tasks (v0.3.0)

- *(vscode)* Add rpartition to the spell list
- *(vscode)* Add cspell words for v0.3.0

## [v0.2.0] - Green is not the same as done

ghog full adds a third gate, 0 outliers, and exit code 8

- A second is the new floor
  -- a.ghog.outliers line 2 defaults to 1.0s; the 11s call stops hiding
- Median and MAD, not mean
  -- a robust z-score names the freak call and spares the slower test

v0.2.0 teaches ghog full to time every test call and act on the slow ones.
The full run reads pytest's own slowest-durations block
(--durations=0 --durations-min=0), keeps a call-phase seconds map per test,
and prints avg= and outliers= on the final progress line, the closed bar,
and the closing line. A run that passes every test and meets the coverage
gate but still hides a call far slower than the rest is no longer counted
as done: it returns the new exit code 8 (EXIT_DURATION_OUTLIERS), judged
last so it never masks a failing test or a coverage gap.

A call is flagged only when it is both far out by a robust score and at or
above a floor. The score is the modified z-score on the median and the MAD
(Iglewicz-Hoaglin cutoff 3.5), which reads the center from the bulk and is
not fooled by the right-skew of test call times. The floor lives in a
two-line, git-ignored a.ghog.outliers file: line 1 records the k * median
reference, line 2 is the active floor and defaults to a fixed 1.0s. That
default fixes the case where a sea of 0.00s calls drove the median, and so
the old auto floor, to zero and let an 11s call in a 5262-test suite slip
through. The same loop that drives a failure or a coverage gap now drives
an outlier: exit 8 routes through instructions/groundhog.md to a five-step
fix playbook, and ghog day keeps re-entering until the call is trimmed or
the floor is raised.

### Key changes (v0.2.0)

- **Per-call timing with avg= and outliers=**: ghog full parses pytest's
  slowest-durations block into a call-phase durations map on RunStats, then
  shows the average call time (outliers left out) and the outlier count on
  the final line, the closed bar, and the closing line. A bounded window
  lists the flagged calls, marks the floor, and shows the next-slowest
  runners-up under it for hand-tuning.

- **Exit code 8 for a green-but-slow run**: a full run that is green on
  tests and coverage but holds a true outlier returns EXIT_DURATION_OUTLIERS
  (8), judged after failures and coverage so it never hides them. ghog day
  records its green snapshot only on exit 0, so the loop keeps fixing slow
  calls until none remain or the floor is raised.

- **The a.ghog.outliers floor file, default 1.0s**: a two-line project-root
  file holds the k * median reference on line 1 and the active floor on line
  2, default a fixed one second. Raise line 2 to accept a legitimately slow
  call, lower it to catch faster ones, set it to 0 to switch the gate off;
  deleting the file falls back to the one-second default.

### 🚀 Features (v0.2.0)

- *(pw)* Add handoff subcommand and run_handoff
- *(wac)* Add wacnd no-delimiters alias
- *(ghog)* Capture per-call durations on full
- *(ghog)* Judge call durations into outliers
- *(ghog)* Persist the duration floor file
- *(ghog)* Exit 8 on a true duration outlier
- *(ghog)* Time full runs and gate true outliers

### 🐛 Bug Fixes (v0.2.0)

- *(senv)* Set PRJ_DIR_unix for the reword script
- *(pw)* Start fork_point at HEAD on a fresh branch
- *(pw)* Make handoffs reliable and self-executing
- *(ghog)* No false outliers on a fast suite
- *(duration_outliers)* One-second default floor

### 📚 Documentation (v0.2.0)

- *(duration_outliers)* Add design and plan
- *(pw_handoff)* Record step 1 validation
- *(pw_handoff)* Record step 2 validation
- *(pw)* Wire handoff into cycle instructions
- *(pw_handoff)* Record step 3 validation
- *(pw_handoff)* Record step 4 validation
- *(duration_outliers)* Add the draft
- *(duration_outliers)* Record step 1 validation
- *(senv)* Pin senv.bat to the project root
- *(duration_outliers)* Record step 2 validation
- *(pw)* Prepare a.commit, not the commit itself
- *(duration_outliers)* Record step 3 validation
- *(duration_outliers)* Record step 4 validation
- *(ghog)* Route exit 8 to the outlier playbook
- *(duration_outliers)* Record step 5 validation
- *(duration_outliers)* Record step 6 validation
- *(ghog)* Add fix-slow-test instruction
- *(ghog)* Clarify fix_slow_test returns to loop

### 🧪 Testing (v0.2.0)

- *(groundhog)* Split oversized status test file
- *(pw_handoff)* Add chain acceptance scenarios
- *(ghog)* Acceptance for green-but-slow run

### ⚙️ Miscellaneous Tasks (v0.2.0)

- *(vscode)* Add spell-check dictionary words
- *(spell)* Add untimed and repointed words
- *(cspell)* Allow the isclose dictionary word
- *(cspell)* Allow the undragged dictionary word

### 🔨 Build (v0.2.0)

- *(bat)* Add root `check.bat` static gate
- *(deps)* Bump pytest to 9.1.0

## [v0.1.0] - Handoffs for the prompt-workflow cycle

### 🚀 Features (v0.1.0)

- *(git-workflows)* Add shared prompts, skills, and tools
- *(git)* Add root a.commit replay flow
- *(copilot)* Add prompt and skill workflows
- *(skills)* Add doc review workflow skills
- *(skills)* Add design skill template
- *(skills)* Add plan skill templates
- *(tools)* Add shared root and eof helpers
- *(commits)* Add grouped commit workflow tools
- *(merge-msg)* Add merge reword flow
- *(tools)* Add coverage gap mapping tool
- *(skills)* Add review-and-update-project-docs
- *(.claude/skills)* Migrate text-only skills
- *(.claude/skills)* Migrate skills with assets
- *(templates)* Add open-question template
- *(skills)* Point open-question skills to template
- *(skills)* Add ultrathink to write-design
- *(skills)* Add prepare_release_notes entrypoints
- *(tools)* Add cert-aware uv launcher
- *(git-history-dashboard)* Add shared dashboard tool
- *(tools)* Add wrap_commit text formatter
- *(tools)* Add open-questions section manager
- *(skills)* Add ChatGPT Codex agent skills
- *(tools)* Add prompt workflow generator
- *(pw)* Add the implement cycle prompts
- *(pw)* Name the step in the commit prompt
- *(gbc)* Fail on unscoped commit title
- *(gbc)* Add verbose flag for tracebacks
- *(pw)* Support lettered plan sub-step ids
- *(tools)* Merge adjacent backtick spans
- *(tools)* Backtick wrap-list literals
- *(tools)* Backtick path-separator words
- *(tools)* Add implement-missing prompt
- *(tools)* Lock topic to branch
- *(tools)* Add groundhog pytest reset tool
- *(bin)* Route pytest aliases through ghog
- *(skills)* Register the groundhog loop
- *(tools)* List prompt menus higher step first
- *(tools)* Top implement-missing in cycle menu
- *(tools)* Self-redirect unredirected ghog runs
- *(tools)* Self-report the ghog run lifecycle
- *(tools)* Route Q32 into the init pointers
- *(pw)* Add handoff resolution core

### 🐛 Bug Fixes (v0.1.0)

- *(merge-docs)* Read docs from merge parents
- *(merge-msg)* Use unix paths for bash helpers
- *(merge-msg)* Use PRJ_DIR_unix in reword script
- *(batch-commit)* Keep stop and allow pathspecs
- *(git-batch-commit)* Parse wrapped What items
- *(packaging)* Repair project install metadata
- *(env)* Refresh uv cert and public lock setup
- *(deps)* Bump uv to 0.11.17 for security fixes
- *(senv)* Correct cmd if/else block syntax
- *(pw)* Cancel the menu on ESC
- *(bin)* Honest check exit and big-file scan
- *(tools)* Count only selected tests in bar total
- *(tools)* Fill the user bar on a clean finish
- *(tools)* Post-fix reports restart at ghog day
- *(tools)* Hide the detached survivor console

### 🚜 Refactor (v0.1.0)

- *(coverage-gap)* Split coverage helpers
- *(git-batch)* Split git batch workflow
- *(skills)* Rename plan template to validation
- *(skills)* Fold check-plan prompt into skill
- *(instructions)* Share markdown rules, add table
- *(rules)* Mutualize writing rules
- *(prompts)* Retarget refs to rules/
- *(templates)* Centralize skill templates
- *(skills)* Mutualize bodies via instructions
- *(scripts)* Mutualize update-merge scripts
- *(senv)* Add LLM_SHARED_DIR beside legacy
- *(env)* Read LLM_SHARED_DIR everywhere
- *(tools)* Split wrap_commit by passes

### 📚 Documentation (v0.1.0)

- *(readme)* Explain project-first workspace use
- *(skill)* Add decision table requirement
- *(skills)* Add split-and-define workflow
- *(skills)* Add requirement doc templates
- *(skills)* Add split item ordering step
- *(prompts)* Drop old write-plan prompt
- *(skills)* Move split-large-file to skill
- *(check)* Add final verdict lines
- *(workflow)* Add IA branch guide
- *(skills)* Spell out option pros and cons
- *(skills)* Fix write-requirement checks
- *(write-requirement)* Defer open questions
- *(open-questions)* Add question description
- *(readme)* Rewrite contents tree for new layout
- *(development)* Rename impl-md to validation-md
- *(development)* Add phase diagrams and goal
- *(readme)* Add workflow overview and goal
- *(repo)* Multi-agent reframe + llm-shared rename
- *(readme)* Note LLM must review its own work
- *(dev)* Expand LLM self-review rationale
- *(repo)* Document why/what commit body extension
- *(release-notes)* Add release prep guide
- *(release-notes)* Space out key changes list
- *(release-notes)* Document the prepare step
- *(license)* Add MIT license
- *(readme)* Document the uv-based workflow
- *(readme)* Clarify uv cert and lock behavior
- *(skill)* Add wac step before user review
- *(skill)* Route open questions through oqm
- *(tools)* Add prompt workflow spec
- *(oqm)* Lead answers with the chosen option
- *(pw)* Spec the implement cycle prompts
- *(pw)* Spec the commit prompt step naming
- *(pw)* Spec lettered plan sub-step ids
- *(senv)* Document coverage-safe test aliases
- *(steps)* Require pta and 100% unit coverage
- *(templates)* Add yes/no validation header
- *(templates)* Add Missing work and No status
- *(tools)* Spec the implement-missing prompt
- *(templates)* Require Not started first status
- *(tools)* Spec the topic-branch lock
- *(tools)* Drop step-analysis template
- *(tools)* Spec groundhog, the pytest reset tool
- *(instructions)* Verify steps with ghog day
- *(plans)* Record Missing work on a No check
- *(md)* Add `GROUNDHOG.md` and wire the manuals
- *(tools)* Spec the Q54 menu-order decision
- *(plans)* Require Missing work on partial checks
- *(tools)* Spec the Q55 implement-missing top
- *(rules)* Get shell commands right first try
- *(ghog)* Document the a.ghog.log redirect
- *(ghog)* Record the Q31 self-redirect guard
- *(instructions)* Inline the redirected ghog call
- *(ghog)* Record the Q32 run lifecycle
- *(instructions)* Inline the status-file contract
- *(ghog)* Record Q33 and the poll cadence
- *(instructions)* Mirror the ghog status poll
- *(check)* Pin the step status first sentence
- *(pw_handoff)* Add design, draft and plan

### 🎨 Styling (v0.1.0)

- *(tests)* Sort imports in metadata test

### 🧪 Testing (v0.1.0)

- *(tools)* Cover helper script branches
- *(git)* Cover batch commit workflows
- *(coverage)* Cover gap mapping tool
- *(git-history-dashboard)* Cover build pipeline
- *(oqm)* Cover the CLI entry point
- *(tools)* Cover groundhog units and AT1-AT17
- *(tools)* Split git_batch_commit coverage
- *(tools)* Type and split plan-cycle tests
- *(tools)* Cover the ghog self-redirect guard
- *(tools)* Cover the ghog run lifecycle
- *(tools)* Pin the hidden-console spawn flags

### ⚙️ Miscellaneous Tasks (v0.1.0)

- *(repo)* Add workspace bootstrap files
- *(workspace)* Split local setup tweaks
- *(repo)* Add shared tool workspace config
- *(shell)* Wire shared tool entry points
- *(shell)* Add shared venv wrappers
- *(shell)* Route commit macros via wrappers
- *(shell)* Add gcab root commit alias
- *(editor)* Add gcab spellcheck word
- *(env)* Init git unix path helpers
- *(env)* Add uv doskey shortcut
- *(.claude)* Add core Claude agent config
- *(senv)* Add claude doskey alias
- *(claude)* Permissions and local ignores
- *(vscode)* Add ultrathink to spell dict
- *(write-plans)* Drop implementation template
- *(spell)* Add frontmatter to cSpell words
- *(tests)* Rename copilot-shared to llm-shared
- *(vscode)* Rename workspace file to llm-shared
- *(git)* Ignore local wheel build output
- *(senv)* Move shell aliases to uv tooling
- *(vscode)* Add cspell word for unaliased
- *(env)* Ignore local cert bundles
- *(gitignore)* Ignore git_history.csv export
- *(senv)* Add wac alias for wrap_commit
- *(vscode)* Turn on copilot otel db exporter
- *(vscode)* Allow tset in spell-check words
- *(claude)* Allow local commit wrapper script
- *(senv)* Drop coverage from pta alias
- *(vscode)* Add groundhog terms to cSpell

### 🔨 Build (v0.1.0)

- *(uv)* Align project metadata with sync
- *(shell)* Add covg command wrappers
- *(release-notes)* Add prep script and template
- *(deps)* Bump pip pin to 26.1.1
- *(deps)* Adopt uv and declarative pyproject
- *(ghd)* Add launcher and shell alias
- *(senv)* Harden uv-lock-public clean filter
- *(oqm)* Add launcher and shell alias
- *(pw)* Add launcher and shell aliases
