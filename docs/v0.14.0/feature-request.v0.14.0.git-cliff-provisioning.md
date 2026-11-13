# Provision pinned git-cliff automatically

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Slug: git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md

## Draft basis and user need for git-cliff provisioning

As a maintainer who renders a generated changelog or runs a generated release
with the llm-shared release tooling, I need the exact git-cliff version my
project expects to be available without installing it, finding it or even
knowing it is a dependency. A missing or unusable binary must stop generated
work with a precise setup diagnostic before anything in my project changes,
while every operation that does not render a changelog keeps working.

The [focused draft](draft.v0.14.0.git-cliff-provisioning.md) derives from item
3 of the [sibling release tooling umbrella](draft.v0.14.0.sibling_release_tooling.md)
and was approved on 2026-11-13. It gathers the umbrella contracts on the
internal cache and downloader, the exact pin, the compatibility research from
2.7.0 to 2.14.2, the fixed `GIT_CLIFF` value, the `gcliff` launcher and alias,
concurrency and integrity checks, and the dependency-specific preflight errors
(umbrella decisions 17 to 21 and confirmed answer Q1 A). This requirement
records those outcomes without choosing their implementation. The user's
clarifications of 2026-11-13 are integrated below and summarized in the
[requirement clarifications](#requirement-clarifications-for-git-cliff-provisioning).

## Current behavior before git-cliff provisioning

- dev_workflow's `uc` alias (`tools/dev_workflow/init.bat`) runs
  `update-changelog.bat`, which starts `bash` on `update-changelog.sh`. That
  script invokes `${PRGS}/git-cliffs/current/git-cliff.exe` with
  `-c cliff.toml -w <PRJ_DIR> -s footer -o CHANGELOG.tmp.md`, first printing
  its version with `-V`. Only then does it clean the output with sed, inject
  the `version.txt` notes, attach `changelog-header.md`, label the sections
  and apply the `.changelog.fixes` Perl rules.
- That binary comes from global senv. The one observed here is
  `git-cliff-2.7.0-x86_64-pc-windows-msvc`, selected through a `current`
  directory. Nothing pins, checks or downloads a version: a missing binary
  fails inside `bash` at its first call, after the alias has started.
- Item 1, `release-project-root`, is completed and merged. It supplies the
  explicit validated project root, root-scoped Git, dispatch through the
  self-locating `bin/release_workflow.bat` and `bin/release_alias.bat`, the
  Windows x64 runtime check, and the common `.release.ini` reader, read with
  interpolation off, that composes explicitly registered domain schemas and
  validates every declared setting before mutation. It names this item's
  managed binary cache as the one distinct permitted write area inside the
  tooling checkout.
- Item 2, `version-sources`, is completed and merged. It ships the `version`
  and `versions` operations and the shared stable/snapshot tag classifier and
  range selector that git-cliff input will use. Configuring git-cliff with that
  selector is item 4's work.
- The release engine has no git-cliff code. Its shipped schemas are `tooling`
  and `version`, so a `[git-cliff]` section is reported today as an unknown
  configuration section, and a git-cliff executable key under `[tooling]` is
  rejected as an unknown key.
- llm-shared ships no `bin/gcliff.bat` launcher, and its alias set
  (`senv.doskey`) defines no `gcliff` alias. That alias set is one shared file:
  llm-shared's `senv.bat` loads it with `doskey /MACROFILE`, and my-project's
  `senv.bat` loads `..\llm-shared\senv.doskey`. Global senv defines its own
  `gcliff` macro on the `PRGS` 2.7.0 binary.
- llm-shared's `.gitignore` has no entry for `.tools/git-cliff/`. Its generic
  `*.exe`, `*.zip` and `*.lock` patterns cover some of the files a cache would
  hold, but other files placed there, such as an extracted text file or a
  digest record, would appear as untracked.

## Scope and ownership boundaries of git-cliff provisioning

This item owns pin resolution and admission, asset selection, download,
integrity and version checks, the cache with its locks and its ignore rule,
direct invocation, and the shared resolver behind the `gcliff` launcher and
alias definition. It registers the `[git-cliff]` configuration section with the
common reader, and it delivers the raw-output compatibility evidence that
admits the initial pin.

The neighboring behaviors stay with their items:

| Umbrella item | Behavior owned by that item |
| --- | --- |
| 4, changelog-management | When rendering needs git-cliff, `cliff.toml`, header, ranges, fix rules and archives, the preflight ordering before automatic `fixes init`, and rechecking its own rendering and postprocessing against the admitted pin |
| 5, build-release-lifecycle | Calling provisioning in generated release `pre` before project writes |
| 6, release-tooling-setup | Bringing the aliases, `gcliff` included, to a consumer that does not load llm-shared's shared alias file yet; proposing a newer tested pin with its diff; recommending the provisioning warm-up without requiring a download |
| 7, prepare-release-integration | `/prepare-release` Steps 10 and 11 calling the changelog services |
| 8, llm-shared-cutover | llm-shared's own `.release.ini` pin; adding `gcliff` to the shared `senv.doskey`; verifying that the cache stays ignored; parity rehearsals of the complete legacy and new pipelines |

Umbrella items integrate into the `sibling_release_tooling` branch; main
receives the completed umbrella once, after all items are developed. A consumer
that loads files from llm-shared's main checkout therefore sees items 3 and 8
together.

The cache layout below the fixed path, the storage and hash of the local
integrity record, the lock mechanism and the test that a lock holder is gone,
the download client with its proxy and certificate-store integration, the
archive extraction method, the digest source, the time-budget values and retry
policy, and the exact output formats and exit-code numbers remain design work.

## Version notation for the git-cliff pin

| Context | Form | Example |
| --- | --- | --- |
| git-cliff pin in `.release.ini` and the cache directory | `X.Y.Z`, without `v` | `2.14.2` |
| Upstream GitHub release tag | `vX.Y.Z` | `v2.14.2` |

The pin follows the umbrella notation rule (decision 31): a value that sets a
version never includes `v`; an upstream tag keeps its actual spelling.

## Exact pin resolution from the project configuration

Read an exact `[git-cliff] version` from the consuming project's
`.release.ini`, or use the tested llm-shared default when it is omitted. The
proposed default is 2.14.2; it becomes the tested default once its
compatibility evidence is recorded (see
[the evidence this item delivers](#compatibility-evidence-this-item-delivers)).

```ini
[git-cliff]
; exact version to download automatically into llm-shared's ignored cache
version = 2.14.2
```

- Only tested pins are admitted. The tested set holds the versions with
  recorded compatibility evidence, the default included. Any other exact
  version is refused before mutation with a diagnostic that lists the tested
  pins. This is stricter than umbrella decision 19, which asks for evidence
  before cutover and deliberate upgrades but does not itself restrict project
  pins; item 6 remains the deliberate path to a newer tested pin.
- An omitted pin follows the tested default of the executing llm-shared
  checkout. The version never moves during a release, only when that checkout
  changes, and an explicit pin survives a tooling update while it stays in the
  tested set. Item 6's upgrade workflow reports a changed default when the user
  upgrades through it; an ordinary checkout update, such as a `git pull` in
  llm-shared, can change the next output without that report. A project that
  needs a fixed renderer declares the pin, as llm-shared does at its cutover.
- The pin belongs to internal provisioning. The common reader validates it with
  every other declared setting, before mutation, including for operations that
  never need git-cliff and for the `gcliff` launcher: an invalid declaration,
  even in an unrelated section, is reported with the reader's diagnostic, and
  no other pin is used as a fallback.
- No executable key exists in `.release.ini`: llm-shared computes the fixed
  internal path, and no consumer runs code from project configuration.
- Within a project, the pin comes from that project; outside one, the
  llm-shared default applies. For `gcliff`, the project is the worktree
  containing the current directory.
- Never resolve a floating `latest`. A later upgrade is a deliberate pin change
  with compatibility evidence (umbrella decision 19).
- Obtaining a version only to gather compatibility evidence is separate from
  admitting it as a pin: an evidence candidate is never accepted from
  `.release.ini` before its evidence is recorded.

## Internal versioned cache for the git-cliff binary

The fixed location for one pin and platform is:

```text
<LLM_SHARED_DIR>/.tools/git-cliff/<version>/<platform>/git-cliff.exe
```

- Each executing llm-shared checkout, a main checkout or a linked worktree,
  uses only its own cache, with no cross-checkout or per-user fallback. When a
  write that provisioning needs is denied, the setup diagnostic names the path
  and the permission failure. Whether a read-only checkout can reuse an
  existing entry depends on the lock or validation writes the design needs;
  this requirement promises neither outcome.
- This item ignores the whole `.tools/git-cliff/` cache in llm-shared Git
  before its first write, in every checkout, so no provisioning file can appear
  as untracked or join a commit. The item 8 cutover only verifies that the
  cache stays ignored. The mechanism, such as a root `.gitignore` entry or a
  self-ignoring cache directory, is design work.
- Versioned directories let consumers with different pins share one llm-shared
  checkout.
- Cache writes are the explicit exception to keeping consumer temporary state
  out of llm-shared. Consumer transaction state never goes into the tooling
  checkout.
- The cache has its own provisioning locks, separate from the per-project
  release operation lock. Linked-worktree Git metadata and this tooling cache
  keep distinct boundaries.
- Complete entries stay until a user deliberately removes one while nothing
  uses it. Provisioning never evicts a complete valid entry and never replaces
  a binary another release is using. A removed entry is available offline again
  only after a later provisioning succeeds. Leftovers of an interrupted
  download are cleaned by a later provisioning of that version, only once their
  owner is established to be no longer running.

## Direct invocation through GIT_CLIFF and the gcliff launcher

- `GIT_CLIFF` is a launcher-local value computed from the internal path, not an
  external override. No PATH, `PRGS`, global-senv, alias or machine
  installation discovery is performed (umbrella decision 20).
- Invoke the absolute executable directly. Leave the parent's PATH and
  environment unchanged.
- The `bin/gcliff.bat` launcher and the `gcliff` alias use the same resolver
  and downloader as the engine. The alias is available to every user who loads
  llm-shared aliases, including without global senv (umbrella decision 17).
  Scripts call the launcher directly, since doskey aliases do not expand in
  subprocesses.
- The launcher selects the project from the worktree containing the current
  directory, including from a nested directory (umbrella decision 16).
  git-cliff arguments pass through unread: a target argument such as
  `--workdir` or `--repository` that points at another repository does not
  select that repository's pin. Outside a worktree, or in one without a
  `[git-cliff]` pin, the default applies after the whole-file validation.
- git-cliff's standard output and exit status pass through `gcliff` unchanged.
- This item ships and tests `bin/gcliff.bat` and the alias definition without
  editing the shared `senv.doskey`. Item 8 adds the alias to that shared file
  at llm-shared's cutover, a shared exposure that reaches every console loading
  the file; item 6 brings it to consumers that do not load that file yet. A
  consumer that loads the shared file from llm-shared's main checkout, such as
  my-project, receives the provisioned `gcliff` when the completed umbrella
  reaches main, replacing a global-senv `gcliff` loaded earlier, while its own
  legacy `uc` can keep rendering with 2.7.0 until that consumer's migration.
  This mixed-version interval is accepted and recorded, not avoided.
- Provisioning happens at first need. A launcher call such as
  `bin\gcliff.bat --version`, or `gcliff --version` once the alias is exposed,
  is the documented way to provision a project's pin ahead of time, for
  example before working offline. Setup can recommend that call; it never
  requires a download.

## Provisioning sequence before generated changelog work

1. Check the selected cache entry: first verify the cached executable against
   its locally recorded integrity data, then run its `--version`, which must
   report the pin. A missing or mismatching local record makes the entry
   invalid before it runs. Reuse a valid copy without network access.
2. If it is absent or invalid, obtain the matching OS and architecture release
   asset from `orhun/git-cliff` on GitHub, verify its published integrity
   information, and extract it safely into a unique temporary cache directory.
   The download goes to GitHub only, through the documented standard proxy
   configuration and the operating system's trusted certificates, always with
   certificate verification and with no mirror setting.
3. Validate `--version`, record the extracted executable's local integrity
   data, then publish the cache entry atomically under a per-version and
   per-platform lock. Concurrent releases must not consume a partial install
   or replace a binary another release is using.
4. If the fixed binary still cannot be made available, stop with the requested
   version, the internal path and the download, verification or execution
   diagnostic. Explain the llm-shared setup, network or permission failure; do
   not ask the user to install git-cliff or change PATH.

An interrupted download leaves no entry that a later run accepts as valid. A
valid cached binary needs no network; a missing one with no network fails with
the step 4 diagnostic.

### Lock contention and interrupted provisioning

A second caller that finds the lock held waits for the holder, reporting that
it waits, up to a bounded time, then fails with a diagnostic naming the lock
and its holder. Two callers started together therefore both succeed after one
download, provided it completes within the waiting caller's budget. A lock is
recovered automatically, and its partial download discarded, only once its
holder is established to be no longer running: the lock's age alone never
proves that, and recovery never removes a temporary installation that a live
caller still owns.

### Time budgets for provisioning stages

Every provisioning-controlled network operation, the release metadata lookup
and the asset download, and every version probe has a documented finite time
budget, with bounded retries if any. An expired budget reports the pin, the
internal path and the failed stage, leaves no entry that a later run accepts,
and releases recoverable lock state, without changing the project. These
budgets bound the lock holder's own work, as the bounded wait bounds the
callers waiting for it; rendering by git-cliff itself stays outside this
guarantee.

### Provisioning messages and exit status

A download and its result are announced in one or two lines on standard
error, plus the lock-wait message when a caller waits; reuse of a valid cache
prints nothing. A provisioning failure uses an exit status that the admitted
git-cliff versions never return, so a caller can tell "tool unavailable" from
"git-cliff reported an error"; the design verifies that for each admitted
version.

### Integrity data for each git-cliff release asset

The supported platform contract defines the integrity check for each asset; do
not assume every asset has a `.sha512` sidecar. For example, 2.14.2 lists those
for tarballs but not for Windows ZIPs; the inspected x86_64 MSVC ZIP has a
SHA-256 digest in GitHub's asset metadata. Verify that digest where it is
available. Missing verification data is an explicit setup failure, never a
reason to skip the check, for every production pin.

Two kinds of integrity data serve different purposes. The archive digest is
checked against upstream data once, at download time. The integrity record of
the extracted executable is kept locally when the entry is published, so a
later run detects a changed binary offline before running it. That local record
detects divergence from what was published; it does not defeat a coordinated
replacement of both the record and the binary.

### Evidence-only exception for the 2.7.0 comparison binary

Checked on 2026-11-13 through GitHub's release API, the 2.7.0
`git-cliff-2.7.0-x86_64-pc-windows-msvc.zip` asset has no asset digest, and
2.7.0 publishes `.sha512` sidecars for its tarballs only. The 2.7.0 Windows
binary therefore cannot be verified against upstream data, and the integrity
rule keeps 2.7.0 from ever being a production pin.

On 2026-11-13, before the binary first runs, the user authorized a narrowly
scoped evidence-only trust policy for the compatibility comparison. The
evidence run obtains the 2.7.0 Windows ZIP from the named upstream GitHub
release over certificate-verified HTTPS, records its exact asset identity and
SHA-256 digest, and runs it solely for the frozen-input comparison. HTTPS is
the initial trust anchor; the recorded digest identifies the downloaded bytes
and is rechecked when the comparison is repeated, but it does not authenticate
the initial download. The candidate is never admitted as a project pin or
published as an entry that normal provisioning accepts, and missing upstream
verification data remains a setup failure for every production pin. Repeating
the comparison needs no new authorization; reviewing its resulting evidence is
a separate acceptance step.

## Operations that need the provisioned binary

Provisioning occurs before any consuming-project managed-file, index, commit or
tag mutation. Generated mode means only that changelog text is rendered from
Git commits using git-cliff; it is not a separate version or release lifecycle.

| Operation | Needs the provisioned binary |
| --- | --- |
| `changelog` in generated mode, including `uc` | Yes |
| Generated release `pre` | Yes |
| The `gcliff` launcher and alias | Yes |
| `version`, `versions list`, `versions set`, `versions check` | No |
| `snapshot`, which does not regenerate a changelog | No |
| Ordinary builds | No |
| Curated-mode validation and curated release builds | No |
| Fix-rule conversion; `fixes dry-run`, which uses existing text | No |

`uc`, `uvf` and release-note preparation run the git-cliff preflight before
automatic `fixes init`, so a missing tool cannot leave a newly created rule file
behind. That ordering belongs to item 4; this item supplies the provisioning
those callers run first.

When llm-shared sits beside the project, the umbrella states:

| Situation | `b` (build) | `brel` / `br` | `gv`, `uc`, `uver`, `uvf` |
| --- | --- | --- | --- |
| Pinned git-cliff absent from the internal cache | Builds | Generated `br`/`brel` downloads and verifies it automatically before project mutation; curated release builds need none | Generated `uc` does the same; version and snapshot commands and curated validation need no binary |
| Internal git-cliff unavailable and download or verification fails | Builds | Generated release fails with the internal path, version and setup or network diagnostic; curated release builds work | Generated `uc` fails; version commands and curated validation remain available |

All release entries still require `main` and the readiness gates (item 5).

## Supported platform for git-cliff provisioning

The v0.14.0 release tooling supports Windows x64 only initially, covering
git-cliff provisioning among the other parts (confirmed answer Q1 A). Other
operating systems and architectures require later scope; existing Unix
deployment references do not extend this support. An unsupported platform
receives a clear scope diagnostic before project mutation.

## Failure when git-cliff provisioning cannot supply the binary

Attempt automatic provisioning first. If it cannot supply the binary, fail
generated work before project mutation with an internal setup or download
diagnostic naming the requested version, the internal path and the failed
stage, with the distinct provisioning exit status; other operations remain
usable (umbrella decision 21). A stalled stage fails at its time budget instead
of hanging. Never require a manual git-cliff installation or a PATH change.

## Compatibility of the 2.14.2 pin with the observed 2.7.0

Upstream checked on 2026-10-09: the GitHub latest-release endpoint identifies
[2.14.2, published 2026-09-18](https://github.com/orhun/git-cliff/releases/tag/v2.14.2).
[2.7.0 was published 2024-11-20](https://github.com/orhun/git-cliff/releases/tag/v2.7.0).
The following changes matter to this engine; this is release-note and existing
`cliff.toml` inspection, not evidence of a completed binary parity run.

| Releases since 2.7.0 | Relevant changes | Consequence for llm-shared |
| --- | --- | --- |
| [2.8.0](https://github.com/orhun/git-cliff/releases/tag/v2.8.0), [2.9.0](https://github.com/orhun/git-cliff/releases/tag/v2.9.0) | Subdirectory/config discovery, monorepo include-path changes, worktree path fix, custom-range/submodule fixes, `require_conventional` | Exercise explicit roots, linked worktrees and nested repositories; keep config and range explicit |
| [2.10.0](https://github.com/orhun/git-cliff/releases/tag/v2.10.0) | Breaking change to empty default header/footer; include/exclude paths in config; skip-tag evaluation fix | Specify header/footer deliberately and compare generated bytes; skipping a tag must not accidentally discard its commits |
| [2.11.0](https://github.com/orhun/git-cliff/releases/tag/v2.11.0), [2.12.0](https://github.com/orhun/git-cliff/releases/tag/v2.12.0) | Unmatched-commit failure option, regex template filters, offline and `--skip-tags` CLI options; Azure DevOps template variable renamed | Useful controls, but opt in deliberately; audit any consumer remote templates and preserve the engine's own release-tag selection |
| [2.13.0](https://github.com/orhun/git-cliff/releases/tag/v2.13.0) | More config locations, configurable commit-processing order, per-commit statistics and offline environment support | Avoid ambient config/order changes; keep rendering local unless remote metadata is explicitly required |
| [2.14.1](https://github.com/orhun/git-cliff/releases/tag/v2.14.1) | Breaking config discovery, multi-value CLI parsing and remote PR-author field changes; graph-reachability release assignment, Windows path matching and nested annotated-tag fixes | Recheck command arguments, merge histories and custom templates; explicit config limits discovery surprises |
| [2.14.2](https://github.com/orhun/git-cliff/releases/tag/v2.14.2) | Multiple commit parsers can apply; all fields of a parser must match; `--workdir` include-path fix | Compare grouping, skip rules and security-body matches in the existing ordered parser list, not just successful execution |

### Pinning policy options for git-cliff

| Pinning policy | Pros | Cons |
| --- | --- | --- |
| Exact `version = 2.14.2` in `.release.ini` (recommended for this cutover) | Reproducible binary, recent worktree/Windows/range fixes, automatic first-use install, reviewable upgrades | Newer parser/default behavior can change output; compatibility evidence and a deliberate later pin update are required |
| Retain exact `2.7.0` as a production pin | Closest comparison with the observed old tooling | Rejected: its Windows ZIP has no upstream integrity data, so it cannot be admitted; 2.7.0 is only the evidence-only comparison candidate |
| Floating `latest` on each run | Gets new upstream changes without editing config | Output and CLI behavior can change without project review; network dependence and hard-to-reproduce releases; rejected |

### Compatibility evidence this item delivers

This item establishes raw git-cliff output evidence only. 2.7.0 and 2.14.2 run
with identical, recorded inputs: llm-shared's history frozen at a recorded
commit, the same explicit ranges, the dev_workflow `cliff.toml` and the same
command-line flags as `update-changelog.sh`, that is
`-c cliff.toml -w <root> -s footer`. The evidence matrix covers commit parsers
and skip rules,
snapshot-tag history and archive ranges, with a recorded fixture history for
any case llm-shared's own history lacks. Every difference is classified as
intentional or a defect.

The postprocessing that `update-changelog.sh` applies after git-cliff (sed
cleanup, `version.txt` notes, `changelog-header.md`, section labels and
`.changelog.fixes` rules) is outside this evidence. Item 4 rechecks its new
rendering, configuration and postprocessing, and item 8's parity rehearsals
compare the complete legacy and new pipelines. my-project's history and fix
rules stay with its own migration.

2.14.2 is obtained through this item's download and upstream integrity
verification as an evidence candidate, and joins the tested set as the default
once this evidence is recorded. 2.7.0 runs only under the
[evidence-only policy](#evidence-only-exception-for-the-270-comparison-binary).
Later setup and upgrade checks (item 6) can propose a newer tested exact pin
with its diff; ordinary release runs never silently move the pin. Until that
evidence exists, 2.14.2 remains a researched recommendation, and the upstream
release check above dates from 2026-10-09.

## Consumer inputs shaping git-cliff provisioning

These repositories shape the need. Their own migrations stay in their own
efforts; llm-shared's belongs to item 8.

- llm-shared: generated changelog with 2 fix rules. Its cutover (item 8)
  creates `.release.ini` with the exact git-cliff pin, verifies that the
  internal `.tools/git-cliff/` cache stays ignored (this item ignores it before
  its first write), and adds `gcliff` to the shared `senv.doskey` with the
  other aliases. Parity rehearsals against dev_workflow accept approved
  git-cliff output fixes as documented intentional differences.
- my-project: generated changelog with 32 fix rules, so it needs the
  provisioned binary for `uc` and generated releases. Its `senv.bat` loads
  llm-shared's shared `senv.doskey`, so it receives the provisioned `gcliff`
  when the completed umbrella reaches main, while its legacy `uc` keeps 2.7.0
  until its own migration.
- workspace-halo: its hand-written, marketplace-style `CHANGELOG.md` uses the
  `curated` mode, so it never needs git-cliff.

## Gap to close in the implementation for git-cliff provisioning

1. Register a `[git-cliff]` domain schema with the common reader: an exact
   `version` in `X.Y.Z` form, admitted only when it is in the tested set and
   validated before mutation, with the executing checkout's tested default
   when it is omitted. Keep rejecting any executable key.
2. Compute the fixed internal path for the resolved pin and the supported
   platform in the executing checkout, and ignore `.tools/git-cliff/` in
   llm-shared Git before the first cache write.
3. Reuse a cached binary offline after its local integrity check and version
   check; otherwise select, download through the standard proxy and operating
   system trust store, verify, extract and atomically publish the matching
   release asset under a per-version and per-platform lock, with bounded and
   reported waiting, recovery only from a holder established to be gone,
   finite stage budgets and no automatic eviction of complete entries.
4. Report the requested version, the internal path and the precise setup,
   network, verification or execution failure with its stage, under the
   distinct provisioning exit status, before any consuming-project mutation.
5. Diagnose unsupported operating systems and architectures before project
   mutation.
6. Ship `bin/gcliff.bat` and the `gcliff` alias definition on the shared
   resolver: the pin of the worktree containing the current directory, the
   llm-shared default outside one, git-cliff's arguments, output and exit
   status passed through, the parent environment unchanged and the shared
   `senv.doskey` left unedited.
7. Expose the provisioning entry point that items 4 and 5 call before
   generated changelog work, while keeping every operation that does not need
   git-cliff free of it.
8. Establish raw-output compatibility evidence for the 2.14.2 pin against
   2.7.0 on recorded frozen inputs and the coverage matrix, using the
   evidence-only policy for 2.7.0, and record the intentional differences.

## Acceptance criteria for git-cliff provisioning

- Read an exact project or default pin, admitting only tested pins, compute its
  ignored internal version and platform path in the executing checkout, and
  reuse a cached binary that passes its local integrity check and its version
  check without network. No executable override, PATH search or mutation,
  `PRGS` or senv dependency.
- Automatically download the correct GitHub release asset when it is absent or
  invalid, through the standard proxy configuration and the operating system's
  certificates, verify its integrity and version, extract it safely and
  publish it atomically under a cache lock. Handle concurrent users with
  bounded, reported waiting, interrupted downloads with owner-aware recovery,
  stalled stages with finite budgets, and offline use. Support Windows x64
  only initially and diagnose other platforms before project mutation.
- Report the internal path and pin, and the precise setup, network or
  verification failure with its stage and a provisioning exit status distinct
  from git-cliff's, when provisioning cannot supply the binary. Never require
  a manual git-cliff installation. Do this before any consuming-project
  managed-file or Git mutation.
- The direct launcher and the `gcliff` alias definition share provisioning;
  scripts do not depend on doskey expansion. The worktree containing the
  current directory selects the pin and the llm-shared default applies outside
  one, after validation of the whole `.release.ini`; git-cliff's arguments,
  output and status pass through, and the parent's environment stays
  unchanged. This item does not edit the shared `senv.doskey`.
- Establish raw-output compatibility evidence for the proposed exact 2.14.2
  pin on recorded frozen inputs with the parser, skip-rule, snapshot-tag and
  archive-range matrix, and record the intentional differences from the
  observed 2.7.0, which runs only under the authorized evidence-only policy.
  No floating latest and no silent pin upgrade at release time.
- Version operations, ordinary builds, curated validation and fix conversion
  remain available without provisioning; the cache is ignored before its first
  write and its state never joins a commit.

## Code references for git-cliff provisioning

- `tools/release_workflow/schemas.py`: `SHIPPED_SCHEMAS` holds the `tooling`
  and `version` domains; this item adds the git-cliff domain to that explicit
  manifest.
- `tools/release_workflow/configuration.py`: the common `.release.ini` reader,
  with interpolation off, that rejects unknown sections and keys before
  mutation.
- `tools/release_workflow/bootstrap.py`: the Windows x64 runtime check item 1
  ships.
- `tools/release_workflow/cli.py`: `SHIPPED_HANDLERS`, today only `version` and
  `versions`.
- `bin/release_workflow.bat` and `bin/release_alias.bat`: the self-locating
  launchers a `bin/gcliff.bat` sits beside.
- `senv.doskey`: llm-shared's shared alias set, loaded with
  `doskey /MACROFILE` by llm-shared's and my-project's `senv.bat`; item 8 adds
  the `gcliff` alias there.
- `.gitignore`: generic `*.exe`, `*.zip` and `*.lock` patterns, no
  `.tools/git-cliff/` entry yet; this item makes the cache ignored before its
  first write.
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`:
  already rejects a git-cliff executable key under `[tooling]`.
- `tools/dev_workflow/update-changelog.sh`, `update-changelog.bat`, `init.bat`
  and `cliff.toml`: the legacy invocation through `PRGS` and the `uc` alias
  this item's provisioning replaces, and the configuration and flags of the
  raw-output comparison.

## Requirement clarifications for git-cliff provisioning

The user decided each question after an explanation on 2026-11-13, and
independent review round 4 checked the decisions for consistency. The question
blocks, with their full options and arguments, are kept in the commit
`docs(feature): record pre-consolidation questions`.

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Only tested pins are admitted; any other pin is refused before mutation with the tested pins listed, and evidence candidates stay outside admission. Every generated changelog comes from a reviewed renderer; stricter than decision 19 | Exact pin resolution; Gap 1; first acceptance criterion | Any exact version with a supported asset (unreviewed output, late integrity failures); any version with a warning (lost in automated runs) |
| Q02 | An omitted pin follows the executing checkout's tested default; an explicit pin survives tooling updates while tested; the version never moves during a release, but a plain checkout update can change it without an item 6 report. Keeps decision 1's zero configuration | Exact pin resolution; Gap 1 | Requiring an explicit pin in generated mode (contradicts decision 1); recording the default on the first run (hidden project mutation) |
| Q03 | A cached entry is valid only when it matches its local integrity record, checked before `--version` runs, and then reports the pin; a missing or mismatching record invalidates it. A changed binary never runs | Provisioning sequence step 1; Integrity data; Gap 3; first acceptance criterion | `--version` alone (runs a modified binary); file existence alone (late, worse failure) |
| Q04 | Each executing checkout uses only its own cache, with no fallback; a denied required write gives the setup diagnostic; read-only reuse is left to the design. Keeps decisions 7 and 20 | Internal versioned cache; Gap 2 | Worktrees sharing the main checkout's cache (crosses item 1's boundary); a per-user fallback (a second location) |
| Q05 | This item ignores the whole cache before its first write in every checkout; item 8 verifies it. The item that writes the cache keeps it out of Git; the window concerns the umbrella branch and its worktrees, since main receives the umbrella only after all items | Internal versioned cache; Scope table; Consumer inputs; Gap 2; last acceptance criterion; umbrella llm-shared consumer bullet and item 8 | The ignore rule at the item 8 cutover (untracked cache files until then) |
| Q06 | A second caller waits with a message up to a bounded time, then fails naming the lock and holder; a lock is recovered only once its holder is established gone, never on age alone, never removing a live caller's files | Lock contention and interrupted provisioning; Gap 3; second acceptance criterion | Failing at once (spurious failures); unbounded waiting with manual cleanup |
| Q07 | GitHub only, through the documented standard proxy configuration and the operating system's trusted certificates, certificate verification always on, no mirror | Provisioning sequence step 2; Gap 3; second acceptance criterion | A mirror base URL (new setting and trust decision); a direct connection with Python's own bundle (fails behind proxies) |
| Q08 | One or two standard-error lines per download plus the wait line, silent reuse, git-cliff's output and status passed through, and a provisioning status the admitted versions never return | Provisioning messages and exit status; Direct invocation; Failure; Gap 4; third acceptance criterion | Silence until failure (a first download looks hung); progress on standard output (corrupts captured output) |
| Q09 | Provisioning at first need; `bin\gcliff.bat --version`, or the alias once exposed, is the documented warm-up; setup may recommend it and never requires a download | Direct invocation; Scope table | A dedicated provision command (duplicates `gcliff`); a setup download (network dependency, stale after a pin change) |
| Q10 | The worktree containing the current directory, nested folders included, selects the pin; arguments pass through unread, and a target argument never selects another repository's pin | Exact pin resolution; Direct invocation; Gap 6; fourth acceptance criterion | An explicit root argument (breaks plain git-cliff arguments); parsing `--workdir` and `--repository` (couples the launcher to git-cliff's syntax) |
| Q11 | `gcliff` validates the whole `.release.ini` like every release operation and reports any invalid declaration, with no fallback | Exact pin resolution; fourth acceptance criterion | Validating `[git-cliff]` alone (changes item 1's reader contract); falling back to the default (undermines exact pinning) |
| Q12 | This item ships and tests the launcher and alias definition without editing the shared `senv.doskey`; item 8 adds the alias there as a shared exposure, and item 6 serves consumers not loading that file; the mixed-version interval with a legacy `uc` is recorded, and main consumers receive the alias when the umbrella merges | Direct invocation; Scope table; Consumer inputs; Gap 6; fourth acceptance criterion; umbrella alias paragraph and items 3, 6 and 8 | Editing the shared file in this item (an earlier interval); a new alias name (two names for one tool); per-project activation (departs from decision 17) |
| Q13 | This item delivers raw git-cliff output evidence on recorded frozen inputs with the parser, skip-rule, snapshot-tag and archive-range matrix; postprocessing stays with item 4 and full parity with item 8; 2.14.2 is admitted once its evidence is recorded | Compatibility evidence this item delivers; Gap 8; fifth acceptance criterion; umbrella decision 19 and item 3 | Provisioning-only evidence (contradicts the acceptance criterion); adding my-project (its own effort); the full legacy pipeline (duplicates item 8) |
| Q14 | Complete entries stay until removed by hand while unused; no automatic eviction and no replacement of a binary in use; partial leftovers are cleaned under the Q06 ownership check | Internal versioned cache; Gap 3 | Automatic removal of unused versions (may delete one still needed); a clean command (extra scope for a small disk cost) |
| Q15 | Every provisioning network stage and version probe has a documented finite budget with bounded retries; expiry names the stage, leaves no accepted entry, releases the lock and changes nothing in the project | Time budgets for provisioning stages; Failure; Gap 3; second acceptance criterion | Bounding the lock wait alone (a stalled holder hangs every first use); manual cancellation (an operator step) |
| Q16 | The user authorized, before first execution, an evidence-only exception: 2.7.0 over certificate-verified HTTPS, asset identity and SHA-256 recorded, run only for the comparison; never a pin or accepted entry, and production provisioning stays fail-closed | Evidence-only exception; Integrity data; Pinning policy; Compatibility evidence; fifth acceptance criterion; umbrella provisioning sequence and decision 19 | Corroborating with the global-senv binary (machine-specific, not authentication); dropping the 2.7.0 run (renderer differences cannot be isolated) |
