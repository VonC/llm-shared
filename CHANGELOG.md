# LLM-Shared workflow tools

Shared instructions, skills, scripts, and Python tools that drive an LLM
project from a raw idea through requirement, design, plan, and a tagged
release. The groundhog test loop (ghog), the prompt-workflow cycle (pw),
and the commit and changelog helpers are mutualized across sibling
projects.

## [v0.11.0-SNAPSHOT unreleased] The Word Is Resume - c47322f760ef57d38605a2aad3bf4a72f9523669

One word restarts an interrupted review, migration and ownership included.

- Two Agents, One Transcript
  -- A review round is a file on disk, not a conversation in one session.
- The Human Keeps the Commit
  -- Reviewers recommend commit-ready; only a person passes the gate.

Release 0.11.0 turns a review into a durable exchange. A request, an answer, a
coordination record, and a versioned transcript live under one repository-local
home, `.reviews` by default and selected by `.review-artifacts.ini`. Two
independent agent sessions hold the writer and reviewer roles, fenced by an
ownership generation and a session-only token, and neither role may start the
other. Specification and implementation reviews share that core: the writer
publishes a request and waits, the reviewer assesses and publishes an answer,
and the exchange converges only at a gate the human passes.

An interrupted review no longer needs a recovery ritual. Typing `resume` checks
artifact placement, migrates a legacy root layout when the move is safe, reads
the recorded Claude, Codex, or Gemini nature of each role, and performs
ownership pickup without asking for a token. A reviewer that has answered keeps
one quiet foreground wait open for the next request in any exchange, and
`rvw_status` reports every active review without resuming it.

Two mechanical gates now report before a commit rather than after. The Markdown
checker applies the repository rules as one authority, and `commit-plan-check`
returns a read-only readiness verdict for the staged `a.commit` in text or JSON.

### Key changes (v0.11.0)

- **Durable review exchanges**: Rounds, coordination, and transcripts persist
  under a configured artifact home, so an interrupted review resumes from disk
  with its round, occurrence, and evidence intact instead of restarting.

- **Fenced two-agent roles**: An ownership generation and a session-only token
  admit exactly one acting session per role, competing reviewers resolve to one
  claim winner, and a displaced session is refused rather than silently obeyed.

- **Readiness before the commit**: `markdown-check` and `commit-plan-check`
  report Markdown rule findings and staged-plan readiness as their own exit
  codes, so a grouped commit is validated before it is created, not after.

### 🚀 Features (v0.11.0)

- *(review)* Add exchange identity model
- *(review-exchange)* Add persistence store
- *(review-exchange-core)* Add lifecycle engine
- *(review-exchange-core)* Add command adapter
- *(review-mode)* Integrate exchange core
- *(spec-review-requestor)* Render paired requests
- *(spec-review-requestor)* Add review role
- *(spec-review-requestor)* Route live reviews
- *(review-mode)* Add specification requestor
- *(skills)* Add humanizer editing guide
- *(spec-reviewer)* Route pending reviews
- *(spec-reviewer)* Render paired answers
- *(spec-reviewer)* Add answer renderer CLI
- *(spec-reviewer)* Add reviewer orchestration
- *(spec-reviewer)* Add host adapters
- *(spec-reviewer)* Integrate reviewer workflow
- *(code-review)* Render paired requests
- *(code-review)* Add specialized requestor
- *(code-review)* Route commit gate requests
- *(review-mode)* Integrate code review requestor
- *(code-review)* Add request evidence types
- *(code-review)* Publish immutable evidence
- *(commits)* Validate exact staged plans
- *(review)* Retain executable evidence
- *(review-exchange)* Add forced reclaim
- *(review-exchange)* Recover stalled rounds
- *(code-reviewer)* Bound implementation checks
- *(code-reviewer)* Render paired review answers
- *(code-reviewer)* Route independent reviews
- *(code-reviewer)* Integrate review responder
- *(review)* Externalize wait timeout defaults
- *(consolidation)* Snapshot questions first
- *(review)* Support project validation declarations
- *(markdown-check)* Add source model and rule engine
- *(markdown-check)* Add policy and baseline
- *(markdown-check)* Add tracked checker
- *(markdown-check)* Add direct launcher
- *(markdown-check)* Enforce strong style
- *(markdown-check)* Wire shared gate
- *(markdown-check)* Enforce repository Markdown policy
- *(commit-plan)* Share staged path inventory
- *(commit-plan-check)* Expose read-only plan checker
- *(commit-plan-check)* Gate review requests
- *(commit-plan)* Expose read-only validation
- *(ghog)* Stream senv live behind GHOG_SENV_LIVE
- *(doskey)* Add the live ghog subcommand aliases
- *(senv)* Add the project PATH fingerprint check
- *(trim-thinking)* Trim an exported conversation
- *(tth)* Add the launcher and its doskey alias
- *(review-status)* Add immutable result models
- *(review-status)* Discover active exchanges
- *(review-status)* Expose status skill
- *(review-status)* Integrate status reporting
- *(review)* Add configurable artifact home
- *(review)* Enforce caller files in the artifact home
- *(commit-plan)* Require validation markers
- *(review-resume)* Record role LLM nature
- *(markdown-check)* Add missing prose rules
- *(review-exchange)* Add ownership capabilities
- *(review-exchange)* Fence session mutations
- *(review-status)* Add schema 2 context
- *(workflow)* Preserve review continuation
- *(review-resume)* Restore interrupted roles
- *(review-resume)* Wire role workflow adapters
- *(ghog)* Separate parallel and timing runs
- *(review-resume)* Integrate interrupted recovery
- *(audit)* Add SKILL and instructions for auditing applications
- *(skill)* Introduce audit-application skill
- *(review-mode)* Integrate independent review mode
- *(docs-layout)* Add version-slug layout support

### 🐛 Bug Fixes (v0.11.0)

- *(pw)* Harden plan step detection
- *(review-exchange-core)* Use NUL Git paths
- *(pw)* Resolve merged umbrella status
- *(review-exchange)* Repair format and recovery
- *(spec-reviewer)* Harden answer validation
- *(spec-reviewer)* Retire published manifests
- *(code-reviewer)* Bound evidence paths
- *(review-exchange)* Keep transcripts portable
- *(review-exchange)* Reject external paths
- *(review-exchange)* Expose request occurrence
- *(code-reviewer)* Let reviewers reclaim requests
- *(review-exchange)* Isolate launcher context
- *(code-review)* Qualify round headings
- *(pw)* Recover clean umbrella branches
- *(review-exchange)* Retry locked replacements
- *(review)* Align guidance rendering
- *(process-draft)* Pause umbrella child handoff
- *(process-draft)* Require child draft file
- *(review)* Keep reviewers waiting between rounds
- *(process-draft)* Require changed child draft
- *(markdown-check)* Clear Markdown debt
- *(drafts)* Keep umbrella paths literal
- *(workflow)* Guarantee clean consolidation
- *(review)* Guarantee clean commit completion
- *(release)* Route topics through umbrella
- *(doskey)* Stop shadowing the ghd dashboard alias
- *(release)* Support untagged first releases
- *(commit-plan)* Isolate shared module lookup
- *(review-cli)* Restore package imports
- *(review-routing)* Carry umbrella context
- *(trim-thinking)* Truncate at dated prompts
- *(review-markdown)* Keep authored blocks valid
- *(prompt-workflow)* Ignore stale code review records
- *(codex-plugin)* Validate cached redirects
- *(review)* Route gate pickup to requestor
- *(markdown)* Accept cache-relative adapters
- *(review-resume-command)* Defer discovery during active publication
- *(review-resume-command)* Retry transient migration journal replacement
- *(review)* Renew forced-resume ownership
- *(trim)* Preserve later Claude answer sections
- *(codex-plugin)* Allow metadata in redirects

### 🚜 Refactor (v0.11.0)

- *(rules)* Centralize agent guidance
- *(skills)* Redirect provider adapters
- *(docs)* Split document resolution
- *(workflow)* Split skill routing
- *(review)* Harden evidence boundaries

### 📚 Documentation (v0.11.0)

- *(skills)* Explain canonical adapters
- *(review)* Define exchange core
- *(review)* Record step 1 completion
- *(review-exchange-core)* Record step 2 validation
- *(review-exchange-core)* Record step 3 completion
- *(review-exchange-core)* Add requestor guide
- *(review-exchange-core)* Record step 4 validation
- *(review-exchange-core)* Record step 5 validation
- *(spec-review-requestor)* Define review flow
- *(spec-review-requestor)* Record step 1 validation
- *(spec-review-requestor)* Record step 2 validation
- *(spec-review-requestor)* Record step 3 validation
- *(spec-review-requestor)* Close step 3 review
- *(spec-review-requestor)* Record step 4 validation
- *(spec-review-requestor)* Close step 4 review
- *(spec-reviewer)* Define reviewer workflow
- *(spec-reviewer)* Record step 1 validation
- *(spec-reviewer)* Record step 2 validation
- *(spec-reviewer)* Record review history
- *(spec-reviewer)* Record step 3 validation
- *(spec-reviewer)* Record step 4 review
- *(spec-reviewer)* Record step 4 validation
- *(review)* Define code review requestor
- *(code-review-requestor)* Record step 1 validation
- *(code-review-requestor)* Record step 2 validation
- *(code-review-requestor)* Record step 3 validation
- *(code-review-requestor)* Record step 4 validation
- *(code-reviewer)* Define the implementation review responder
- *(code-reviewer)* Design review responder
- *(code-reviewer)* Plan review responder
- *(code-reviewer)* Record step 1 validation
- *(review)* Require unique and well-formed headings in appended rounds
- *(wiki)* Give sections unique headings
- *(code-reviewer)* Record step 2 completion
- *(code-reviewer)* Record step 3 validation
- *(code-reviewer)* Record step 4 validation
- *(review-mode)* Add quality follow-ups
- *(code-reviewer)* Record step 5 completion
- *(code-reviewer)* Record step 6 validation
- *(code-reviewer)* Polish review record
- *(review-mode-docs)* Define documentation scope
- *(release)* Widen step 12 to every version source
- *(review-mode-docs)* Design documentation set
- *(review-mode-docs)* Plan independent review documentation
- *(review-mode-docs)* Explain independent review authority
- *(review-mode-docs)* Record step 1 validation
- *(review-mode-docs)* Teach review journeys
- *(review-mode-docs)* Record step 2 validation
- *(review-mode-docs)* Add task guides
- *(review-mode-docs)* Record step 3 validation
- *(review-mode-docs)* Publish review contract
- *(review-mode-docs)* Record step 4 completion
- *(review-mode-docs)* Close acceptance coverage
- *(review-mode-docs)* Record step 5 validation
- *(review-mode-docs)* Record code review
- *(review-mode-docs)* Integrate review guide
- *(review-mode)* Add recovery command topics
- *(review)* Explain wait timeout precedence
- *(workflows)* Sync review and draft guides
- *(markdown-check)* Define checker requirement
- *(markdown-check)* Record specification review
- *(consolidation)* Explain question snapshots
- *(markdown-check)* Record questions
- *(review)* Repair request list spacing
- *(markdown-check)* Add MD032 requirement
- *(markdown-check)* Consolidate checker design
- *(markdown-check)* Record plan questions
- *(markdown-check)* Clarify checker reads
- *(markdown-check)* Record plan review
- *(markdown-check)* Consolidate plan
- *(markdown-check)* Settle lint exceptions
- *(markdown-check)* Record step 1 validation
- *(markdown-check)* Record step 1 code review
- *(markdown-check)* Record step 2 validation
- *(markdown-check)* Publish checker reference
- *(markdown-check)* Record step 3 validation
- *(commit)* Record pre-consolidation questions
- *(commit-plan)* Refine child draft
- *(commit-plan)* Consolidate requirement
- *(commit)* Record pre-consolidation questions
- *(commit)* Consolidate design decisions
- *(plan)* Record pre-consolidation questions
- *(commit-plan)* Settle checked plan
- *(commit-plan)* Fix review list formatting
- *(commit-plan-check)* Record step 1 validation
- *(workflow)* Document clean commit handoffs
- *(commit-plan-check)* Record step 2 validation
- *(commit-plan-check)* Record step 2 review
- *(commit-plan-check)* Record step 3 validation
- *(commit-plan-check)* Record step 3 review
- *(commit-plan-check)* Fix format example
- *(commit-plan-check)* Wire readiness checks
- *(commit-plan-check)* Record step 4 validation
- *(commit-plan-check)* Record step 4 review
- *(release)* Document umbrella routing
- *(feature)* Record pre-consolidation questions
- *(review-status)* Consolidate requirement
- *(review-status)* Record design review
- *(review-status)* Record consolidation choice
- *(review-status)* Consolidate status design
- *(trim-thinking)* Document the tth command
- *(plan)* Record pre-consolidation questions
- *(review-status)* Bound status file reads
- *(review-status)* Consolidate implementation plan
- *(review-status)* Repair transcript markdown
- *(review-status-command)* Record step 1 validation
- *(review-status-command)* Record step 2 validation
- *(review-status)* Require public skill
- *(review-status)* Record step 3 completion
- *(review-status)* Publish review transcript
- *(plan)* Record pre-consolidation questions
- *(review-status)* Record step 4 completion
- *(code-reviewer)* Consolidate plan decisions
- *(code-reviewer)* Publish review dialogue
- *(review-status-command)* Record step 4 validation
- *(feature)* Record pre-consolidation questions
- *(review-resume)* Define resume requirement
- *(review-resume)* Record specification review
- *(review-resume)* Widen reviewer wait
- *(review-resume)* Record reopened review
- *(design)* Record pre-consolidation questions
- *(review-resume)* Consolidate design
- *(review-resume)* Record design review
- *(plan)* Record pre-consolidation questions
- *(review-resume)* Clarify artifact IO
- *(review-resume)* Consolidate implementation plan
- *(review-resume)* Record plan review
- *(review)* Qualify repeated exchange headings
- *(review-resume-command)* Record step 0 validation
- *(review-resume)* Record step 0 code review
- *(review)* Require the artifact home for caller files
- *(review-resume-command)* Record step 1 review
- *(review-resume-command)* Record step 1 validation
- *(review)* Keep reviewers available
- *(commit-plan)* Require validation markers
- *(trim-thinking)* Explain dated truncation
- *(markdown)* Require heading spacing
- *(review-resume-command)* Record step 2 validation
- *(markdown)* Describe enforced prose rules
- *(review-resume)* Preserve step 2 exchange
- *(review-resume-command)* Record step 3 validation
- *(workflows)* Resolve shared tool paths
- *(codex-plugin)* Explain cached redirects
- *(review-resume-command)* Record step 3 review
- *(review)* Explain new-session pickup
- *(resume)* Require automatic pickup
- *(review-status)* Describe migration preflight
- *(review-resume-command)* Record step 4 validation
- *(review)* Enforce role-isolated workflows
- *(review)* Publish independent review guidance
- *(review-resume-command)* Record review exchange
- *(review-resume)* Define foreground wait outcomes
- *(review-resume-command)* Record step 5 validation
- *(review-resume)* Record step 5 review
- *(review-resume-command)* Document shipped resume workflows
- *(review-resume-command)* Record step 6 validation
- *(review-resume)* Retain step 6 review
- *(agents)* Delegate policy to canonical files
- *(groundhog)* Raise the status polling floor
- *(implementation-check)* Bound coverage claims
- *(tools)* Use a neutral project placeholder
- *(docs-layout)* Document version-slug layout option
- *(docs-layout)* Drop the last four-layout claims
- *(wiki)* Cover the v0.11.0 release topics

### ⚡ Performance (v0.11.0)

- *(prepare-release)* Shorten planner checks
- *(tests)* Keep calls below duration gate
- *(test)* Remove duplicate coverage reports
- *(review-exchange)* Isolate wait setup
- *(tests)* Reduce review regression setup costs
- *(tests)* Distribute acceptance scenarios

### 🎨 Styling (v0.11.0)

- *(wiki)* Normalize navigation line endings
- *(markdown)* Clear remaining lint debt

### 🧪 Testing (v0.11.0)

- *(skills)* Reject copied adapter bodies
- *(workflow)* Cover exact document lookup
- *(perf)* Isolate slow assertion calls
- *(release)* Move Git setup to fixtures
- *(review-exchange)* Cover persistence faults
- *(review-exchange-core)* Cover lifecycle states
- *(review-exchange-core)* Cover command adapter
- *(prepare-release)* Move Git setup to fixtures
- *(review-exchange-core)* Add acceptance journeys
- *(pw)* Cover merged umbrella routing
- *(sensitive-history)* Mock unborn Git state
- *(spec-review-requestor)* Cover role contracts
- *(spec-review-requestor)* Cover review routing
- *(prompt-workflow)* Move git run to fixture
- *(spec-review-requestor)* Prove full workflow
- *(groundhog)* Move Git work to fixtures
- *(spec-reviewer)* Cover answer rendering
- *(spec-reviewer)* Cover reviewer boundaries
- *(spec-reviewer)* Prove reviewer workflow
- *(prepare-release)* Shorten git test calls
- *(groundhog)* Shorten duration-gated setup
- *(code-review)* Prove requestor lifecycle
- *(duration)* Shorten gated checks
- *(duration)* Cut full-suite runtime
- *(code-reviewer)* Prove responder acceptance
- *(groundhog)* Bound subprocess integration calls
- *(perf)* Shorten repository acceptance
- *(review)* Split lifecycle and policy contracts
- *(markdown-check)* Cover parsing and rule behavior
- *(markdown-check)* Cover checker workflow
- *(markdown-check)* Cover gate rollout
- *(workflow)* Stabilize verification gates
- *(commit-plan-check)* Cover readiness rollout
- *(trim-thinking)* Cover the trimmer and its CLI
- *(trim-thinking)* Mark fixture as used
- *(markdown)* Cover MD038 file allowance
- *(review-status)* Cover active discovery
- *(review-status)* Cover skill and command
- *(review-routing)* Cover context handoff
- *(review-status)* Cover status command
- *(review-resume)* Add performance guardrails
- *(commit-plan)* Cover validation markers
- *(review-status)* Avoid redundant path resolution
- *(review-artifacts)* Stub failed tracking query
- *(review-exchange)* Cover ownership fencing
- *(workflows)* Cover shared path resolution
- *(tooling)* Cover redirect checks
- *(review-status)* Prove schema 2 behavior
- *(review-resume-command)* Cover cross-workflow resume acceptance

### ⚙️ Miscellaneous Tasks (v0.11.0)

- *(editor)* Add review protocol words
- *(plugin)* Refresh Codex cache version
- *(plugin)* Refresh Codex cache version
- *(workspace)* Set halo logo scale
- *(workspace)* Allow replayable spelling
- *(editor)* Accept rescope spelling
- *(editor)* Accept junctioned spelling
- *(editor)* Accept review vocabulary
- *(vscode)* Recognize numstat spelling
- *(vscode)* Recognize neighbours spelling
- *(vscode)* Accept review terminology
- *(editor)* Accept review terminology
- *(editor)* Accept overcount spelling
- *(editor)* Accept baselining spelling
- *(vscode)* Recognize checker terminology
- *(env)* Resolve Claude launcher path
- *(editor)* Add review vocabulary
- *(editor)* Add workflow vocabulary
- *(editor)* Add review status vocabulary
- *(editor)* Add review status terms
- *(markdown)* Scope transcript lint
- *(dev-env)* Update editor and aliases
- *(review-status)* Add status aliases
- *(editor)* Recognize review status alias
- *(vscode)* Recognize prevalidated
- *(lint)* Ignore review helper files
- *(editor)* Add mkdocs to dictionary
- *(lint)* Ignore scratch Python files
- *(vscode)* Add Markdown check task
- *(codex)* Refresh local plugin metadata
- *(vscode)* Set active activity bar borders
- *(repo)* Record automation settings
- *(vscode)* Drop duplicate radon exclude entry

### 🔨 Build (v0.11.0)

- *(deps)* Declare watchdog directly

## [v0.10.0] - 2026-07-31 - Four Folders, One Document

`pw document` finds an artifact from its version, slug, and type.

- No Guessing at the Fork
  -- Topology previews prove branch boundaries before a merge starts.
- Hooks, Hogs, and History
  -- Commit hooks, Groundhog, and history scans catch repository trouble.

Release 0.10.0 makes branch selection explicit. The topology planner reports
on-main, integration, and feature scopes, proves feature boundaries, and
previews merges or commit-by-commit replays in an isolated object directory.
Prepare-release can land one topic, follow an ordered umbrella, audit the
Diátaxis wiki, and prepare the final release files without rewriting a
published feature branch.

Document workflows now carry one of four layouts from draft processing through
release. `pw document` locates an artifact from version, slug, and type alone,
while ordered umbrella routing advances only after the validation evidence on
disk agrees with the declared status table.

### Key changes (v0.10.0)

- **Proven release scope**: The planner reports exact commits, boundaries, and
  conflict previews for main, integration, and feature releases before Git
  history changes.

- **Folder-independent documents**: Drafts and later artifacts share a chosen
  flat, minor, full-version, or nested directory, and `pw document` finds the
  unique match without branch or prompt-memory context.

- **Safer repository tools**: Sensitive-commit hooks and contextual history
  scans catch exposed terms, while Groundhog, the local docs server, editable
  presentation builds, and logo extraction provide tested project utilities.

### 🚀 Features (v0.10.0)

- *(html_to_pptx)* Editable pptx from HTML deck
- *(pptx)* Mirror example slides, env branding
- *(pptx)* One-line pptx and pdf generators
- *(antigravity)* Add 22 workflow wrappers
- *(skills)* Add sanitize-git-history skill
- *(isolate-logos)* Split logo sheets to PNG
- *(tools)* Add the serve_docs local site server
- *(release)* Add topology planner
- *(wiki)* Add project wiki shortcut
- *(release)* Apply gitworkflow selection
- *(history-scan)* Add contextual Git audit
- *(git-diagrams)* Render release histories
- *(hooks)* Block sensitive pending commits
- *(skills)* Add sensitive hook setup
- *(ghog)* Restore fast tests under half floor
- *(release)* Audit Diataxis wiki coverage
- *(prepare-release)* Target integration first
- *(pw)* Route ordered umbrella work
- *(workflow)* Chain umbrella requirements
- *(plugin)* Add refresh launcher
- *(doc-structure)* Update document output paths to versioned topic folders
- *(docs)* Add skill to arrange docs folders
- *(drafts)* Add selectable docs layouts
- *(pw)* Find documents across layouts
- *(workflow)* Carry docs layout choices
- *(document-layouts)* Support four layouts

### 🐛 Bug Fixes (v0.10.0)

- *(groundhog)* Clear senv guard for a stale PATH
- *(senv)* Clear NO_MORE_SENV guard in checks
- *(oqm)* Load the guard-clearing project env
- *(env)* Report activation after echo reload
- *(ghog)* Separate duration report sections
- *(pw)* Resolve post-commit plan topics
- *(groundhog)* Render full reports plainly
- *(prompt)* Detect renamed drafts
- *(prompt)* Add implement step id
- *(prompt)* Route terminal plans to release
- *(groundhog)* Separate actionable ghog report sections
- *(bin)* Self-locate LLM_SHARED_DIR in launchers
- *(new-draft)* Skip same-path draft move
- *(codex)* Package every shared instruction
- *(wiki)* Build mounted documentation cleanly
- *(serve-docs)* Preserve emoji nav titles
- *(venv)* Repair incomplete scaffolds
- *(senv)* Recover incomplete project venvs
- *(workflow)* Require reviewed decision rows
- *(covg)* Use an explicit --root verbatim
- *(workflow)* Resolve umbrella branch topics
- *(workflow)* Force post-write review
- *(merge)* Cover develop and main targets
- *(pw)* Share umbrella topic resolution
- *(plans)* Make line estimates advisory
- *(senv)* Create shared sensitive rules file
- *(sensitive-hooks)* Allow empty rule files

### 🚜 Refactor (v0.10.0)

- *(groundhog)* Split out reporting_nextstep
- *(pptx)* Strict types, split deck build
- *(senv)* Delegate venv setup to switchpy
- *(pw)* Rename settled-row constant
- *(tests)* Split structural checks
- *(pw)* Isolate collection routing
- *(release)* Split feature planning

### 📚 Documentation (v0.10.0)

- *(rules)* Add interactive_menu rule
- *(instructions)* Adopt interactive_menu rule
- *(rules)* Add command_prefix_char rule
- *(instructions)* Use command_prefix_char rule
- *(rules)* Note the NO_MORE_SENV guard clear
- *(instructions)* Call tools via bin wrappers
- *(groundhog)* Require final day run
- *(commits)* Pin batch commit workflow
- *(commits)* Clarify commit gate choices
- *(workflow)* Refresh post-v0.9.0 docs
- *(presentation)* Add llm-shared deck
- *(presentation)* Add title-slide logo
- *(presentation)* Add local brand config
- *(presentation)* Detail AI self-review skills
- *(presentation)* Add llm-shared deck as pptx
- *(rules)* Full-path calls for bin launchers
- *(presentation)* Security slide, anchors, dashes
- *(presentation)* Add auto-revue example slides
- *(wiki)* Add theme logos and their prompts
- *(wiki)* Add Diataxis documentation set
- *(main)* Emojis, wiki links, duration gate
- *(antigravity)* How-to and host updates
- *(wiki)* Document history sanitization
- *(rules)* Forbid em dash in prose
- *(requirement)* Underscores in topic label
- *(check)* Flip doc-level status line on last Yes
- *(prepare-release)* Gate on validation status
- *(wiki)* Document the local docs server
- *(release)* Define branch-aware preparation
- *(release)* Explain selection workflows
- *(workflow)* Explain AI ownership and review
- *(hooks)* Explain shared sensitive rules
- *(sanitize)* Classify binary hits, bound terms
- *(wiki)* Binary triage and word-boundary rules
- *(ghog)* Record the Q70 half-floor restore
- *(workflow)* Explain routing handoffs
- *(readme)* Document agents and test gate
- *(merge)* Explain shared target rewording
- *(merge)* Define rewording contract
- *(release)* Explain release wiki audits
- *(pw)* Document umbrella handoff routing
- *(open-questions)* Map BBQ analogy concepts
- *(workflow)* Pin decisions table routing shape
- *(wiki)* Document reusable logo workflow
- *(document-layouts)* Record feature request

### ⚡ Performance (v0.10.0)

- *(groundhog)* Cut slow duration tests
- *(prompt)* Reuse current branch
- *(git-history)* Move repo setup to fixtures
- *(tests)* Trim slow validation calls
- *(senv)* Check hooks only in the current repo
- *(sensitive-history)* Stub git failure
- *(tests)* Cut repeated Git setup

### 🎨 Styling (v0.10.0)

- *(instructions)* Drop doubled blank line
- *(sensitive)* End hook tools with eof marker

### 🧪 Testing (v0.10.0)

- *(instructions)* Normalize wrapper assertion
- *(prompt)* Cover post-commit fallbacks
- *(release)* Cover workflow contracts
- *(sensitive)* Type the monkeypatched doubles
- *(tools)* Hermetic project-root walk tests
- *(release)* Cover the planner to the gate
- *(prompt-workflow)* Cover draft edge cases

### ⚙️ Miscellaneous Tasks (v0.10.0)

- *(repo)* Drop a hardcoded author and path
- *(codex)* Rebundle plugin with instructions
- *(lint)* Allow img, drop line-length rule
- *(vscode)* Add Workspace Halo logo
- *(codex)* Expose isolate-logos skill
- *(codex)* Refresh plugin cachebuster
- *(vscode)* Refresh workspace metadata
- *(codex)* Rebundle drifted instructions
- *(vscode)* Add project spelling terms
- *(plugin)* Refresh llm-shared cache version

### 🔨 Build (v0.10.0)

- *(deps)* Declare python-pptx in dev group
- *(check)* Follow shellcheck exe rename
- *(senv)* Versioned uv-lock-public filter
- *(deps)* Pin pip 26.1.2 for CVE-2026-8643

## [v0.9.0] - 2026-06-25 - Passing the Baton

pw skill names the next step from the docs on disk, so the phases chain

- Terse beats literary
  -- pw skill prints one bare command where pw handoff writes a whole prompt
- Mind the one stop
  -- the review's Q0x table is the only human-in-the-loop pause left

v0.9.0 makes the document phase of the workflow chain itself. A new pw skill
subcommand reads the effort documents on disk -- which exist, which carry open
questions, which are settled -- and prints one bare next-step command,
host-prefixed for Claude or Codex. The write-requirement, write-design, and
write-plans skills, and the consolidate skill, end on a `## Handoff` that runs
`pw skill` and follows the command it prints, so the requirement, design, and plan
phases advance with no menu and no go-ahead.

The one stop left in the document phase is /review-ask-questions, where a human
answers a `Q0x | Title | Recommended Answer` table before the chain resumes. The
commit gate gains the same engine through `pw skill --after-commit`, which derives
the next action -- the next plan step, prepare-release once the last is
committed, or nothing for a standalone commit -- and presents it as a
multi-choice. A shared run-pw.md documents the launcher for any shell.

### Key changes (v0.9.0)

- **The pw skill subcommand**: reads the documents on disk and prints the bare
  next-step command, host-prefixed, with a forced-skill form and an
  --after-commit mode for the commit gate.

- **Automated document-phase handoffs**: the writing and consolidate
  instructions chain through pw skill, so requirement, design, and plan advance
  with no go-ahead, the review the one human-in-the-loop stop.

- **Question table, choice lists, and the pw docs**: review-ask-questions posts
  a `Q0x | Title | Recommended Answer` table and a next-step hint, process-draft
  and split-and-define present multi-choice lists, and `run-pw.md` plus the README
  and DEVELOPMENT pw comparison land, guarded by new test suites.

### 🚀 Features (v0.9.0)

- *(handoff_automation)* Add pw skill module
- *(handoff_automation)* Pw skill disk routing
- *(handoff_automation)* Pw skill subcommand
- *(handoff_automation)* Automated handoffs
- *(handoff_automation)* Hints and choice lists
- *(handoff_automation)* Commit-gate multi-choice
- *(handoff_automation)* Pw skill chains the phases

### 🐛 Bug Fixes (v0.9.0)

- *(release-notes)* Drop the doubled version heading

### 🚜 Refactor (v0.9.0)

- *(codex-plugin)* Nest under llm-shared dir

### 📚 Documentation (v0.9.0)

- *(process-draft)* Fix step 6 untracked rename
- *(handoff_automation)* Add v0.9.0 effort docs
- *(handoff_automation)* Record step 1 validation
- *(handoff_automation)* Commit-gate multi-choice
- *(handoff_automation)* Align routing prose
- *(handoff_automation)* Record step 2 validation
- *(handoff_automation)* Record step 3 validation
- *(handoff_automation)* Record step 4 validation
- *(handoff_automation)* Record step 5 validation
- *(handoff_automation)* Record step 6 validation
- *(handoff_automation)* Record step 7 validation
- *(handoff_automation)* Shared run-pw note
- *(handoff_automation)* Question table and hint
- *(handoff_automation)* Document pw skill
- *(release-notes)* Un-double the v0.9.0 heading

### 🧪 Testing (v0.9.0)

- *(handoff_automation)* Pw skill acceptance
- *(handoff_automation)* Guard run-pw links
- *(handoff_automation)* Guard question table

### ⚙️ Miscellaneous Tasks (v0.9.0)

- *(repo)* Ignore codex runtime, add spell word
- *(repo)* Editor dictionary words
- *(vscode)* Add memorising to the dictionary

## [v0.8.0] - 2026-06-23 - One report, many repos

git-history-report builds one combined dashboard across several repos

- Slice it without a server
  -- project, type and date filters recompute every chart, plus a leaderboard
- Notes that outlive the rebuild
  -- a regenerated figures file beside a hand-kept notes file per project

v0.8.0 turns the single-repo git_history_dashboard into a multi-project
report. A new git-history-report skill resolves one or several repo targets,
tags every commit with its project, and writes one combined dashboard.html
plus data.json; several repos require `--out-dir`, and the page opens unless
`--no-open`. The payload gains a project dimension and an author tally, so the
by_project slices sum back to the top-level series and feed a top-10
contributor leaderboard. In the browser, a single applyFilters recompute
redraws every chart and metric card under a project filter, a commit-type
filter, and a week-indexed date range, and a light/dark toggle remembers a
manual choice through a data-theme override.

The release also splits the hand-written analysis out of the template.
analysis.py rewrites analysis.generated.md from the figures on every run and
keeps one `analysis.notes.<project>.md` per project, created once and never
overwritten, combined and converted to HTML through a uv markdown seam; the
template is now project-neutral with `__TITLE__` and `__ANALYSIS__` slots and no
my-project strings. Supporting workflow fixes land too: pw resolves dotted
sub-step ids and folds hyphen and underscore slugs, the groundhog parser
strips ANSI color so the counters fill under forced color, and a Codex agents
plugin manifest carries valid SKILL.md YAML.

### Key changes for v0.8.0 (v0.8.0)

- **Multi-repo git-history-report skill**: one skill builds a combined commit
  dashboard for one or several repos, writes data.json and a self-contained
  dashboard.html to a chosen `--out-dir`, opens it unless `--no-open`, skips a
  failing repo, and prints a run summary.

- **In-page filters and a contributor leaderboard**: a single applyFilters
  recompute sums the visible by_project slices and redraws every widget under
  project, type and date filters, with a top-10 author leaderboard and a
  remembered light/dark toggle.

- **Split analysis files and a project-neutral template**: a regenerated
  `analysis.generated.md` and a hand-kept `analysis.notes.<project>.md` per
  project, combined through a uv markdown seam into the `__ANALYSIS__` slot,
  with the my-project strings gone.

### 🚀 Features (v0.8.0)

- *(git-history-report)* Per-project breakdown
- *(git-history-report)* Multi-repo CLI
- *(git-history-report)* Analysis files and slots
- *(git-history-report)* In-page filters and theme
- *(git-history-report)* Skill, docs, and acceptance tests
- *(git-history-report)* Multi-project commit dashboard

### 🐛 Bug Fixes (v0.8.0)

- *(pw)* Fold - and _ in doc slug matching
- *(groundhog)* Strip ANSI escapes in the parser
- *(pw)* Keep dotted sub-step ids like 1.1

### 🚜 Refactor (v0.8.0)

- *(git-history-report)* Split build.py

### 📚 Documentation (v0.8.0)

- *(groundhog)* No re-walk without a change
- *(commit)* A.commit at root, group all staged
- *(git-history-report)* V0.8.0 design and plans
- *(dashboard)* Refresh my-project observations
- *(workflow)* No mid-chain stop before commit
- *(git-history-report)* Record step 1 check
- *(git-history-report)* Record step 1.1 check
- *(git-history-report)* Record step 2 check
- *(git-history-report)* Record step 3 check
- *(git-history-report)* Record step 4 check
- *(git-history-report)* Record step 5 check

### 🧪 Testing (v0.8.0)

- *(git-history-report)* Step 0 scaffolding
- *(git-history-report)* Trim the pbt example budget

### ⚙️ Miscellaneous Tasks (v0.8.0)

- *(vscode)* Add behaviours to the dictionary
- *(vscode)* Add XPASS to the dictionary
- *(agents)* Codex plugin manifest and YAML fix

## [v0.7.0] - 2026-06-22 - Branch to brel in one command

prepare-release readies every artifact and stops at the tag

- No browser, still a PDF
  -- activity-report renders Markdown to HTML and PDF, browser-free
- A stale log can no longer lie
  -- ghog day stamps each phase with a banner, a timestamp, and a duration

v0.7.0 turns release preparation into one skill. The new prepare-release
runs from any branch: it merges the effort into main with a why/what merge
message, sets version.txt to the X.Y.Z-SNAPSHOT, runs the release notes and
the changelog, updates pyproject.toml and uv.lock, and stops at a single
chore(release) commit so the tag-cutting brel stays a manual, reviewed step.
It calls the update-merge-commit-msg and prepare_release_notes skills and
hands control back through a git-ignored flag file.

The release also makes the work visible and the workflow tighter. The
activity-report skill gathers git history across working trees and now
renders the report to HTML then PDF with a pure-Python engine, with no
browser to hang on Windows, and updates an existing report instead of
overwriting it. The pw workflow gains a plan review round, so a plan is
challenged before any code is written, and ghog day frames each phase with
vvv/^^^ banners and a per-step duration so an old timestamp gives away a
stale log.

### Key changes for v0.7.0 (v0.7.0)

- **prepare-release skill**: one command, from any branch, that merges,
  rewords, sets the X.Y.Z-SNAPSHOT version, writes the notes and changelog,
  updates pyproject and uv, and stops at one prepare commit before brel.

- **activity-report to HTML and PDF**: the report renders to HTML then PDF
  with the browser-free xhtml2pdf helper, and an existing report is updated
  in place rather than overwritten.

- **ghog day per-step timing**: each phase is framed by vvv/^^^ banners with
  a full local timestamp and a duration, so a stale a.ghog.log shows old
  times instead of passing as a fresh green run.

### 🚀 Features (v0.7.0)

- *(prompt_workflow)* Add plan review round
- *(activity-report)* Add the git log/diff script
- *(groundhog)* Timestamp each day-walk step
- *(prepare-release)* One-command release prep
- *(activity-report)* HTML/PDF and update mode
- V0.7.0 prepare-release and workflow tooling

### 🐛 Bug Fixes (v0.7.0)

- *(open_questions)* Collapse blank lines on strip

### 📚 Documentation (v0.7.0)

- *(workflow)* Document the pw handoff cycle
- *(write-plans)* Lint workarounds, skeleton fills
- *(workflow)* Document the plan review round
- *(review)* Add plan, scope questions per type
- *(activity-report)* Add the two templates
- *(activity-report)* Add the skill and workflow
- *(workflow)* Cmd-shell caveat, ghog big files
- *(guides)* Refresh the workflow guides
- *(prepare-release)* Origin/main check on main
- *(prepare-release)* Catch a pause-time commit

### ⚙️ Miscellaneous Tasks (v0.7.0)

- *(vscode)* Add cSpell dictionary words
- *(vscode)* Add unreviewed to cSpell

## [v0.6.0] - 2026-06-21 - No Console, No Hang

git_batch_commit commits from a background shell now

- No console, no problem
  -- git_batch_commit detects the missing TTY or takes --non-interactive
- A failed batch stops, it no longer hangs
  -- stdin goes to DEVNULL and a non-zero exit replaces the input() prompt

v0.6.0 lets an agent run the batch-commit tool from a background shell.
git_batch_commit used to demand a real terminal: it asked for a console
before git commit, then prompted on a failure, so an agent in a
-NonInteractive, auto-backgrounded shell first hit a console error and
then hung at the continue/stop prompt with no way to answer. The tool now
treats the run as non-interactive when --non-interactive is passed or no
console is attached: it commits without a TTY and with stdin detached, and
it stops a failed batch with a non-zero exit instead of calling input().

The rest of the release trims the test suite. Two test files had crossed
the 650-line gate that the check.bat big-files step rejects, so they are
split by topic into smaller files, each with a single responsibility.
Several real-git integration tests spent whole seconds spawning redundant
git config processes; they now take their identity from the GIT_AUTHOR_*
and GIT_COMMITTER_* env vars, so the config spawns are gone and the full
suite passes the check gate at 100% coverage.

### Key changes for v0.6.0 (v0.6.0)

- **Non-interactive batch commits**: git_batch_commit runs in a background
  shell, commits with no TTY and detached stdin, and exits non-zero on a
  git or add-phase failure instead of prompting at the continue/stop step.

- **Test files under the size gate**: test_new_draft_workflow.py and
  test_wrap_commit.py are split by topic, each resulting file back under
  the 650-line limit with a single responsibility.

- **Faster real-git tests**: the throwaway repositories take their commit
  identity from GIT_AUTHOR_*/GIT_COMMITTER_* env vars, dropping the
  per-repo git config subprocess calls that dominated their setup time.

### 🚀 Features (v0.6.0)

- *(git_batch_commit)* Add non-interactive mode

### 🧪 Testing (v0.6.0)

- *(new_draft)* Split workflow tests by topic
- *(wrap_commit)* Split wraplist tests out
- *(integration)* Speed up real-git tests

### ⚙️ Miscellaneous Tasks (v0.6.0)

- *(release)* Prepare v0.6.0

## [v0.5.0] - 2026-06-20 - A draft walks in, an effort walks out

process-draft names the draft, new_draft renames and branches it

- No prompts, just flags
  -- --from-draft takes the slug, version, and layout the reader gathered
- Even an unsaved draft makes the move
  -- git mv in place, a staged copy into the worktree, the old file dropped

v0.5.0 turns a rough draft into a named, versioned effort on its own
branch. The new process-draft skill runs the first pass a reader has to
do: it decides whether the draft is one feature-request, one issue, or
several, writes that type into the draft, proposes three titles and three
slugs, and picks the version from version.txt. It then hands the
mechanical half to new_draft, which gains a non-interactive --from-draft
mode: given the chosen slug, version, and a --worktree or --in-place
layout, it checks the slug against local and remote branches, creates the
branch with git switch -c, and renames the draft to `draft.vX.Y.Z.<slug>.md`
inside the chosen tree. process-draft then hands off to write-requirement
for one topic or split-and-define for several.

The draft moves whether or not it is committed. In the current tree a
tracked draft is a git mv and an untracked one a plain rename; for a
sibling worktree the text is written into the worktree docs, staged, and
the source dropped. A shared read_version_txt parser, read by both the
instruction and the tool, takes the version from the first line of
version.txt and drops a trailing -SNAPSHOT, so the two never disagree. A
build fix also syncs uv.lock, which had lagged behind the released
project version.

### Key changes for v0.5.0 (v0.5.0)

- **process-draft scaffolds the first pass**: the skill classifies a
  draft as one feature-request, one issue, or a collection, records the
  type, proposes three titles and three slugs, picks the version from
  version.txt, and hands off to write-requirement or split-and-define.

- **new_draft gains a --from-draft mode**: a non-interactive run takes an
  existing draft, a slug, a version, and a --worktree or --in-place
  layout, checks the slug against local and remote branches, creates the
  branch with git switch -c, and renames the draft inside the chosen tree.

- **The draft relocates in place or into a worktree**: a tracked draft
  moves with git mv and an untracked one with a plain rename; a worktree
  run writes the text into the worktree docs, stages it, and drops the
  source, so an uncommitted draft still moves across.

### 🚀 Features (v0.5.0)

- *(new_draft)* Read the version from version.txt
- *(new_draft)* Add draft relocation git helpers
- *(new_draft)* Add the --from-draft mode

### 📚 Documentation (v0.5.0)

- *(process-draft)* Add the process-draft skill
- *(release)* Prepare v0.5.0 notes and changelog

### 🔨 Build (v0.5.0)

- *(uv)* Sync uv.lock to the 0.4.0 release

## [v0.4.0] - 2026-06-18 - One command starts the next effort

new_draft checks the slug, proposes the version, writes the draft

- The commit plan answers to the index
  -- gbc counts every git add against staged files, a rename as two
- Scaffold a branch, guard the commit, rename the launcher
  -- new_draft starts efforts, gbc guards the plan, pw turns prompt_workflow

v0.4.0 adds new_draft, one command that starts a development effort. It
reads a slug from the prompt and rejects it when a local branch or any
declared remote already uses that name, proposes a patch, minor, or major
version from the current one, optionally creates a sibling git worktree,
and writes the draft skeleton on the new branch. The tool ships as five
modules -- models, git, prompts, workflow, and a script hub -- with a
new_draft.bat launcher and the nd and ndr aliases to run it.

The commit helpers get stricter. gbc validates the a.commit plan before
it commits: the run fails when the git add count does not match the
staged files, and a.commit is emptied once every block is committed. A
follow-up fix counts a rename as two paths, the old removed and the new
added, so a clean rename like pw.bat to prompt_workflow.bat no longer
trips the check. wrap-commit drops the backticks from a type(scope):
subject opener on reflowed lines.

### Key changes for v0.4.0 (v0.4.0)

- **new_draft scaffolds an effort**: one command validates the slug
  against local branches and every declared remote, proposes a patch,
  minor, or major version, optionally adds a sibling worktree, and writes
  the draft skeleton on a new branch. It ships as five modules with a
  new_draft.bat launcher and the nd and ndr aliases.

- **gbc checks the plan against the index**: the root a.commit workflow
  now fails when the git add count differs from the staged files, and
  empties a.commit when every block has committed. A rename counts as two
  paths, so a renamed file no longer leaves the count one short.

- **Launcher and subject cleanups**: pw.bat becomes prompt_workflow.bat
  with a venv glob that resolves in the `_main` worktree, and wrap-commit
  strips the backticks from a type(scope): subject opener on reflowed
  lines.

### 🚀 Features (v0.4.0)

- *(gbc)* Validate plan, empty a.commit when done
- *(wrap-commit)* Bare backticked subject opener
- *(new-draft)* Scaffold new development efforts

### 🐛 Bug Fixes (v0.4.0)

- *(git-batch-commit)* Count a staged rename as two paths

### 📚 Documentation (v0.4.0)

- *(changelog)* Backtick ghog exclude placeholders
- *(release)* Prepare v0.4.0 notes and changelog

### 🧪 Testing (v0.4.0)

- *(new-draft)* Cover the scaffolding tool

### ⚙️ Miscellaneous Tasks (v0.4.0)

- *(vscode)* Add backticked to cSpell words

### 🔨 Build (v0.4.0)

- *(coverage)* Omit new_draft UI seam
- *(bin)* Add new_draft, rename pw launcher

## [v0.3.0] - 2026-06-17 - One call gets a pass, the suite does not

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
test that no longer runs is dropped as stale. The ghog exclude `<node>`
`<seconds>` command writes the section, so the list stays right with no
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

- **ghog exclude, the tool-managed writer**: ghog exclude `<node> <seconds>`
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
- *(ghog)* Read TESTING.md for slow-test fixes
- *(release)* V0.3.0 release notes and changelog

### 🧪 Testing (v0.3.0)

- *(ghog)* Cover excluded and drifted runs

### ⚙️ Miscellaneous Tasks (v0.3.0)

- *(vscode)* Add rpartition to the spell list
- *(vscode)* Add cspell words for v0.3.0

### 🔨 Build (v0.3.0)

- *(version)* Bump to 0.3.0

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
