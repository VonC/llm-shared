# Start the seven Claude conversations for Step 2

From this checkout in PowerShell, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\v0.13.0\claude-tabs.shared-wait-service.ps1
```

The [launcher](claude-tabs.shared-wait-service.ps1) opens a new Windows Terminal
window containing `claude-baseline`, `claude-pair-01-a`, `claude-pair-01-b`,
`claude-pair-02-b`, `claude-pair-02-a`, `claude-pair-03-a`, and `claude-pair-03-b`.
Each tab starts a fresh interactive `claude.exe` with an explicit, unique session
UUID and the same seed prompt supplied automatically. Nothing needs pasting.
Complete any normal Claude startup or trust screen if one appears, then leave
all seven tabs open after their `READY` replies. Report the printed run-record
directory to the implementing conversation.

The installed Claude Code 2.1.273 help was checked for positional initial prompts,
`--session-id`, and `--name`. These are also documented in the
[Claude CLI reference](https://code.claude.com/docs/en/cli-reference).
The launcher uses Windows Terminal's documented `-w new`, `new-tab`, fixed title,
and working-directory options from its
[command-line reference](https://learn.microsoft.com/en-us/windows/terminal/command-line-arguments).
It inherits Claude's existing model, effort, permission mode, provider and
telemetry configuration. Their actual native values still require verification.
The PowerShell execution-policy override applies only to the launched processes.

## Inspect the prompt and identities

Each invocation creates a fresh directory under
`a.shared-wait-service/claude-tabs-<UTC timestamp>-<random suffix>/`. It contains:

- `launcher.json`: the seven names and UUIDs, executable/version, seed commit,
  full-file hashes, ordered chunk hashes, and prompt hash.
- `seed-prompt.txt`: the exact initial prompt passed to every tab. It asks Claude
  to read the ordered chunks of both complete frozen drafts and reply `READY`.
- `seeds/` and `chunks/`: exact bytes frozen from commit
  `3d4b5a4643d1fba65434877d965d2c051b65e1a3`, with chunks of at most 9,000 bytes
  ending on line boundaries. Git blob identities verify the full frozen copies.
- `terminal-command.json` and terminal start/result records: the requested
  Windows Terminal invocation and its exit status.
- `<name>.started.json` and, after Claude exits, `<name>.exited.json`: launch
  intent and process exit records for each UUID.

Launch records establish intent, not prompt delivery or `READY`. Native Claude
transcripts must establish those results. An existing run directory or attempted
tab launch is never reused automatically, including after a failure. Keep the
records and report the failed tab; do not paste the seed a second time into a
partially seeded conversation.

To inspect a preparation without opening terminals:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\v0.13.0\claude-tabs.shared-wait-service.ps1 -PrepareOnly
```

A subsequent live invocation creates a fresh directory. Optional parameters are
`-Directory`, `-SeedCommit`, `-ClaudeExecutable`, and `-Terminal`. Paths containing
spaces are supported. Launch paths containing semicolons are rejected because
Windows Terminal treats semicolons as command separators.

## Keep preparation separate from measurement

On 2026-09-16 the operator requested this launcher and automatic initial prompt
delivery. It prepares a separate Claude series, with identical seed input across
the baseline and six trial conversations. Full native reads, normal `READY`,
unchanged settings, and the fixed 5% retained-context gate must pass before trial
manifests and timed prompts are issued. Keep the ten-minute baseline and trials
sequential in A/B, B/A, A/B order, with the existing timing bounds.

The launcher does not start a benchmark, complete the Claude collector/Monitor
integration, or establish Step 2 completion. The earlier smoke result and all
earlier failures remain separate evidence.

## Launcher verification

On 2026-09-16, preparation succeeded with the installed Claude Code 2.1.273.
An executable stand-in captured the actual Windows arguments for the terminal
and all seven Claude invocations: unique UUIDs, intact identical prompts, one
new window with seven tab commands, and paths containing spaces and an
apostrophe. Both frozen drafts reconstructed exactly from the 17 chunks.
Duplicate launches, existing run directories, invalid tab names and changed
seed files were rejected. These checks opened no live Claude conversation;
the human invocation and native transcript checks establish live startup and
seed completion.

The human's live launch `claude-tabs-20260916-180128-11adaf42` was verified at
18:10 UTC the same day. All seven native transcripts contain the exact initial
prompt, all 17 complete chunk results in order, and one normal `READY` completion.
The [selected seed audit](probe-claude-seeds.v0.13.0.shared-wait-service.json)
records their exact UUIDs, native snapshot hashes and context counts. The pair
differences are 3.8912%, 0.9678%, and 0.5834%, within the fixed 5% gate. All seven
original wrappers and their exact Claude child processes were still alive at
18:11:18 UTC, with no exit records.

Observed configuration is Claude Code `2.1.273`, `claude-opus-5`, effort `xhigh`,
and permission mode `auto` in every session. Provider, compaction configuration
and complete request-attempt coverage remain unestablished. Six sessions also
read `rules/chat.md`; `pair-03-b` did not. This preparation variation is retained.
The `pair-03-a` normal-end record descends from `READY` through a
`deferred_tools_record` attachment; a direct-parent-only parser would miss it.
Native `away_summary` bookkeeping follows `READY` without an accompanying
assistant completion in these snapshots. These shapes must be handled explicitly
by the matched-series adapter before timed trials begin.

Local original snapshots, the exact audit script and process checks are retained
under the run's `seed-audit-20260916-181001/` directory. No benchmark prompt or
timed observation was started during the seed audit. Keep these seven sessions
open and idle while the remaining collector/Monitor integration is completed.
