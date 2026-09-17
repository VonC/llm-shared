# Named Codex tabs for the Step 2 trials

## Open the seven prepared conversations

From this checkout in PowerShell, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\v0.13.0\codex-tabs.shared-wait-service.ps1
```

The launcher opens one new Windows Terminal window with these tabs:
`baseline`, `pair-01-a`, `pair-01-b`, `pair-02-b`, `pair-02-a`, `pair-03-a`,
`pair-03-b`. Each tab runs a fresh Codex TUI against the same existing local
backend. It first replies `TAB_READY` to a small setup message, then receives
the prepared seed file and should reply `READY`. Leave the tabs open and idle
after that reply. The launcher returns after queuing the seeds; returning does
not establish that seed loading has completed or passed its context checks.

Windows Terminal 1.24 and Codex 0.154.0 were inspected locally. The launcher
uses the explicit new-window and fixed-title options documented in
[Windows Terminal's command-line reference](https://learn.microsoft.com/en-us/windows/terminal/command-line-arguments).
It requires the previously tested backend to be running at
`<CODEX_HOME>/app-server-control/app-server-control.sock`. A missing or unhealthy
backend fails before opening tabs. It does not install or restart a backend.

## Inspect the saved names and UUIDs

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\v0.13.0\codex-tabs.shared-wait-service.ps1 -Action Status
```

Local records live under `a.shared-wait-service/codex-tabs-20260916/` by default.
Each tab has an exact alias-to-UUID binding in `binding.json`. The native
session name includes a random run prefix, for example `sw-12345678-pair-01-a`.
The visible tab title remains `pair-01-a`.

The launcher finds the thread using equality against its unique first setup
message in Codex's read-only native catalog. It then verifies the original live
TUI process, native UUID, checkout, build and normal `TAB_READY` completion
before assigning the native session name. It never chooses the newest thread
or infers a UUID from the visible tab title.

## Send a prepared benchmark by tab name

After the independent driver has verified full seed reads and retained context,
written the manifest and prepared that trial's benchmark:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\v0.13.0\codex-tabs.shared-wait-service.ps1 -Action Send `
  -Name pair-01-a -InstructionFile '<prepared trial directory>\benchmark.txt'
```

Send reads the actual UTF-8 file contents and calls `codex queue` with the bound
UUID on the same backend. It requires the original TUI process to be alive,
the thread to be idle and its native name to match. A benchmark must be named
`benchmark.txt` and have a neighboring durable `manifest.json` naming that exact
thread. The driver remains responsible for seed evidence, matching, observer
startup, trial ordering and completion of the measurement windows.

Each delivery reserves its slot and saves an intent and the exact instruction
before invoking Codex once. `result.json` preserves stdout, stderr and exit
status. A receipt proves queue acceptance only; native evidence must establish
the model's response. An uncertain delivery is retained and never retried
automatically. Do not delete delivery records to bypass duplicate protection.

## Recover an interrupted launcher without reopening conversations

If setup times out, inspect the existing tabs and their local records. Use Bind
to finish identity discovery after the original setup turns complete:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\v0.13.0\codex-tabs.shared-wait-service.ps1 -Action Bind
```

Bind does not reopen a TUI or send instructions. If a seed has no delivery slot,
send it explicitly with `-Action Send -Name <alias> -Kind seed -InstructionFile
<seed path>`. An existing seed slot must be inspected before any further action.
Open refuses an existing run directory; rejected or interrupted preparations
remain evidence and replacements need a new directory and fresh conversations.

Optional parameters are `-Directory`, `-Names`, `-SeedFile`, `-CodexHome`,
`-CodexExecutable` and `-Terminal`. Names accept a comma-separated list, for
example `-Names smoke-a,smoke-b`. The Python entry point also exposes `--help`.
The wrapper transports arguments as JSON through its process environment;
paths and instruction text are never evaluated as shell code.
The execution-policy override applies only to this PowerShell process and does
not change the user's or machine's policy.

## Keep the automated preparation outside measurements

On 2026-09-16 the operator requested this automation instead of repeatedly
opening TUIs, reporting UUIDs and pasting files manually. Every new conversation
has the same setup-turn structure followed by the same controlled seed. The
unique identity and tab label are recorded as preparation context, and the
fixed 5% retained-context gate still applies.

Complete all seed loading before starting the baseline. Run the ten-minute
baseline and subsequent trials sequentially in A, B, B, A, A, B order. Keep
the source, duplicate-observation and telemetry-drain bounds unchanged.
The launcher never starts a timed benchmark automatically. This preparation
requires a new series; earlier baselines, failures and rejected preparations
are not combined with it. The two-tab launcher diagnostic is also unmeasured.

The implementation is in [the Python entry point](codex-tabs.shared-wait-service.py)
and [the PowerShell wrapper](codex-tabs.shared-wait-service.ps1).
