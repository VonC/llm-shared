# Shared wait service native-wake probe results

## Step 2 status and evidence limits

**Step 2 is complete.** The code and required available-host live evidence
gates are satisfied. Both controlled baselines and all six matched pairs have
retained observations and audits. Codex B1/B2/B3 passed, with B2's observer
recovery retained. Claude B2/B3 passed after the exact native-ancestry repair;
Claude B1 remains failed and was never retried. All three Claude A trials
passed functionally while retaining the unavailable initial-yield parameter.
The final Claude integrity audit passed at `2026-09-17T09:11:59.194Z`.
At `09:12:14.715Z`, closure verification confirmed all seven original sessions,
unchanged final transcript hashes and exited observers. All seven Claude tabs
may now be closed. The human started, seeded and submitted the benchmark prompt
to every measured conversation. Request accounting remains unknown, and no
strict-idle, quota or billing-savings claim follows from these prototype results.

| Evidence | Status | Finding |
| --- | --- | --- |
| Codex executable | Inspected | `codex-cli 0.154.0`; exact-UUID `queue --thread --message` is exposed |
| Codex backend | Prepared local backend works | Original checks returned `10050`; the corrected WebSocket transport now reaches the explicitly connected human-started TUI |
| Codex idle wake | Three controlled functional observations passed | B1/B2/B3 first useful validation at 48.863/27.169/20.380 seconds; one consumption each, exact completion marker and full duplicate/drain observation; B2 recovery and original failed trials retained |
| Claude executable | Actual session inspected | Fresh human-started Claude Code `2.1.273`, model `claude-opus-5`, effort `xhigh`, permission mode `auto` |
| Claude Monitor | Smoke and two controlled B trials passed | B2/B3 useful wake at 5.623/11.906 seconds, one consumption each and full duplicate/drain windows; B1's original binding failure and failed smoke preparations remain retained |
| Request completeness | Unknown | Neither inspected transcript shape certifies every model request attempt |
| Ten-minute unchanged-source baselines | Both controlled baselines audited | Codex completed 600 seconds plus its drain; Claude completed 600.014624 quiet seconds plus a separate 120.013902-second drain |
| A/B-prototype order | Three matched pairs per host audited | A/B, B/A, A/B order retained; Codex B2 recovery, Claude B1 failure and Claude A initial-yield deviations remain explicit |
| Functional route evidence | Proven for measured Codex and Claude cases | Native normal-end, exact thread/event, useful continuation, single consumption and full windows verified for passing B cases; accounting remains unknown and service evidence remains future work |

Inspection dates: 2026-09-15 through 2026-09-17. Seed revision:
`3d4b5a4643d1fba65434877d965d2c051b65e1a3`.
The two complete draft blobs are frozen together by the driver, with a separate
SHA-256 for each exact source path in every trial manifest.
The [redacted manifest and configuration excerpts](probe-manifests.v0.13.0.shared-wait-service.json)
retain trial identities, controls, stream offsets and original manifest hashes.
They provide audit references without claiming trial completion or complete
request coverage.
The separate [controlled-series evidence export](probe-controlled.v0.13.0.shared-wait-service.json)
contains the completed series' selected settings, identities, boundaries, usage,
seed costs, paired deltas and original hashes without private native content.
The [controlled Claude export](probe-claude-controlled.v0.13.0.shared-wait-service.json)
and [final Claude audit](probe-claude-series-audit.v0.13.0.shared-wait-service.json)
retain the seven outcomes, all three pair comparisons and verified closure.

## Inspected host evidence

### Codex 0.154.0 observations

Read-only checks used the installed executable at
`%USERPROFILE%/.codex/packages/standalone/current/bin/codex.exe`:

```text
codex --version
codex queue --help
codex app-server daemon version
codex app-server generate-json-schema --out a.shared-wait-service/inspection/codex-schema
```

The generated protocol describes `initialize`, `initialized`, and `thread/read`
with `includeTurns: false`. Its thread status distinguishes `idle`, `active`,
`notLoaded`, and `systemError`. The provisional queue adapter reads this existing
backend before sending. A failed connection does not start a daemon, change
configuration, resume a thread, or count as a functional pass.

An explicitly selected local rollout from this build contains:

- `session_meta.payload.id` and `cli_version` for stream binding.
- `token_usage_record.payload.thread_id`, `turn_id`, `response_id`, and `usage`.
- Usage fields `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`,
  `output_tokens`, `reasoning_output_tokens`, and `total_tokens`.
- `event_msg` / `task_complete` with `turn_id`, `last_agent_message`,
  `started_at`, `completed_at`, `duration_ms`, and `time_to_first_token_ms`.

The adapter accepts response usage without inventing request-start records.
The observer binds normal completion to the exact registering turn. Its
`mark-normal-end` action records timing only and cannot arm the native route.

### Claude Code 2.1.272 observations

The installed executable is `%USERPROFILE%/.local/bin/claude.exe`. Read-only
inspection of its embedded Monitor definition found these inputs:

| Input | Installed shape |
| --- | --- |
| `description` | Required string |
| `command` or `ws` | Exactly one; command emits event lines on stdout |
| `timeout_ms` | Optional duration, minimum 1,000 ms; runtime-dependent maximum/cap |
| `persistent` | Available only in the unbounded schema variant |
| Output | `taskId`, `timeoutMs`, optional `persistent` |

The tool has a runtime availability predicate and a runtime choice between
bounded and unbounded schemas. Binary presence does not establish that Monitor
is available in a particular conversation. Inspect the actual session tool
schema before submitting a Monitor call. A foreground tool still waiting at
normal end cannot demonstrate the required native wake.

A selected `2.1.272` transcript contains `sessionId`, `version`, `requestId`,
`timestamp`, and assistant `message.id` / `message.usage`. Claude separates
uncached input, cache-read input, and cache-creation input. The adapter adds
those three for total input, retains cache-read separately, and preserves an
unknown reasoning count when `output_tokens_details.thinking_tokens` is absent.
An older `2.1.233` archive was inspected separately and is not counted as current
build evidence or accepted by the current adapter.

### Claude 2.1.273 actual-session capability and smoke

The human started session `b929a07c-afd9-482a-a373-4375a3a93625` in the target
checkout and submitted `CLAUDE_WAIT_CAPABILITY_20260916`. Native evidence records
`ToolSearch` with `select:Monitor`, the resulting `deferred_tools_record`
containing the actual Monitor definition, and a normal final response at
`2026-09-16T15:03:27.578Z`. The session uses `claude-opus-5`, effort `xhigh`,
and permission mode `auto`. Provider identity remains unknown. No Monitor was
started during that capability check, and no settings were changed.

The [selected capability evidence](probe-claude-capability.v0.13.0.shared-wait-service.json)
retains the actual input schema and the private native snapshot's SHA-256.
Both `description` and `timeout_ms` are required by this exposed schema.
`timeout_ms` has a declared maximum of 3,600,000 ms, while the loaded tool
description specifies a runtime cap of 1,800,000 ms. There is no `persistent`
parameter. These schema observations are separate from the live smoke evidence
recorded below.

The [bounded smoke procedure](claude-smoke.v0.13.0.shared-wait-service.md) uses
the [ordinary-code probe](claude-probe.shared-wait-service.py) and its
[native evidence selector](claude-probe-state.shared-wait-service.py).
Its current ignored run is `a.shared-wait-service/claude-smoke-20260916-04`.
The driver exposes `prepare --directory <absolute-run> --transcript
<absolute-native-jsonl>`, followed by `observe --directory <absolute-run>`
through the repository Python environment. The observer is launched hidden;
the human submits the procedure in the existing Claude TUI.

The bridge registers durably, acknowledges arming through a bounded file-event
handshake, and remains silent. The observer requires the exact successful
Monitor call, the exact armed final message and its native `turn_duration`
parent chain. It then holds the source unchanged for 600 seconds before
persisting and emitting one compact event. The authorized continuation checks
identities and consumes through the existing prototype store. Observation
includes a 60-second first-useful-action bound, a 120-second duplicate window,
and a separate 120-second drain. Bridge exit notices count as host activity.
This unseeded feasibility smoke is excluded from matched A/B results.

Preflight checks passed for exact native normal-end binding, missing/error
registration rejection, human interruption, single-line event output, persisted
result validation, duplicate rejection, and a complete ordinary-code simulated
observer/bridge/consume lifecycle. These checks are not live Claude evidence.
At the time of this smoke, the full collector adapter remained pinned to Claude `2.1.272`; this
`2.1.273` smoke retains selected native records separately and never claims
complete request-attempt coverage or a completed matched benchmark.

The first prepared smoke (`claude-smoke-20260916-01`) failed during observer
startup at `2026-09-16T15:15:00.381669Z`, before any Monitor invocation. The
reader incorrectly required a session identity on a `file-history-snapshot`
bookkeeping record, and the startup acknowledgement had been published before
native-file validation. The human submitted the procedure; Claude found the
failure and stopped without starting Monitor. Its failure evidence and exact
driver sources are retained in that run. This is a harness failure, not a
finding about native Claude wake support.

The repair ignores only the identified sessionless bookkeeping record; missing
identity on conversation records or another explicit session still fails.
Startup now validates the actual transcript and arms its file watcher before
publishing readiness. Regression checks cover the actual transcript, the
bookkeeping record and identity rejection.

The second smoke (`claude-smoke-20260916-02`) reached the exact Monitor call at
`2026-09-16T15:37:05.495Z` and received task `btvovf7we`. Its launcher failed
before writing `armed.json`; the bounded confirmation timed out, and Claude
stopped without retrying or printing the armed marker. The session sets
`NoDefaultCurrentDirectoryInExePath=1`, so the bare `senv.bat` resolved to an
unrelated PATH entry and Python was unavailable. The observer was stopped after
verifying that failure. Native evidence, launchers, diagnostics and the driver
sources at failure remain under `-02`. This did not exercise native idle wake.

The generated launchers now call the project-root `senv.bat` by absolute path.
An ordinary-code Windows preflight also exposed benign `uv` stderr being treated
as fatal by Windows PowerShell's `ErrorActionPreference=Stop`; the launcher now
captures native output with `Continue` and explicitly checks the process exit
code before emitting anything. The full generated Monitor/confirm/consume
sequence passed with `NoDefaultCurrentDirectoryInExePath=1`, exactly one stdout
event line, and one accepted consumption. These are launcher checks, not model
wake evidence. Neither failed live run has been overwritten or counted as
successful.

The third preparation (`claude-smoke-20260916-03`) expired at
`2026-09-16T16:21:45.283813Z`, exactly 1,800 seconds after observer startup.
The human's next submission reached Claude at approximately `16:47:53Z`.
Claude found `stop.json` and stopped without invoking Monitor. This is an
expired preparation window, not an idle/wake result. The original failure
snapshot and source files are retained; a separate `native-operator-abort.jsonl`
snapshot includes Claude's later refusal to start and has SHA-256
`ea2b0049f10c019253d4d82c90c20673f3070abd747c0fc47102a2e477decaab`.

Run `-04` uses new source/wait/event identities and a 24-hour operator
submission window. Only that pre-registration window changed: registration,
the 600-second quiet interval, the 60-second wake bound, and the duplicate and
drain intervals retain their previous limits. Its ordinary-code observer waits
on filesystem notifications; the longer submission window adds no model poll.

Run `-04` reached native normal end at `2026-09-16T17:00:14.648Z`.
The observer held the source unchanged for 600.008 seconds and published its
single event at `17:10:14.656042Z`. Without another human submission, Claude
issued the exact consumption command at `17:10:19.913Z`: 5.257 seconds after
handoff. Persisted consumption was accepted at `17:10:42.106681Z`, and Claude
printed exactly `WAIT_TEST_DONE` at `17:10:43.331Z`. Its final native turn ended
at `17:10:43.369Z`; observation finished at `17:14:43.404786Z`, after the full
120-second duplicate window and separate 120-second drain.

The observer and an independent audit both report functional success. The
[selected smoke evidence](probe-claude-smoke.v0.13.0.shared-wait-service.json)
records 24 passing checks against the frozen native snapshot, exact session and
build, unchanged probe sources, one Monitor invocation, the native normal-end
chain, one persisted event and its exact consumption command. There were no
observed tool calls or usage completions during the quiet interval, no human
input after registration, no duplicate consumption and no further observed
tool calls or usage completions after `WAIT_TEST_DONE`.

Monitor task `biet31tdq` delivered its event notice at `17:10:14.979Z` and a
successful stream-ended notice at `17:10:14.982Z`. Both preceded the useful
continuation; the exit notice caused no separate later activity in the observed
window. The native snapshot's SHA-256 is
`049213c75789d3cd6aae7b6f8f40902f57b74f46723b338240dde01d7c46641d`.
The ignored run retains the raw snapshot, durable store, observer result,
independent audit and exact source copies. The selected export redacts the
local Monitor output path. The observer and bridge processes have exited.

This establishes automatic continuation in this human-started Claude session.
The delivery timestamp is the bridge handoff; native receipt and useful work
are separate evidence. Host idleness is inferred from native turn completion
and observed inactivity, without a separate host-status query. Complete request
attempt coverage, strict-idle guarantees, billing and quota savings remain
unproven. This unseeded smoke does not replace Claude's fresh matched baseline,
three A/B pairs or validation of the full `2.1.273` telemetry adapter.

### Claude resume validation on 2026-09-17

The [selected resume audit](probe-claude-resume.v0.13.0.shared-wait-service.json)
records the seven original processes and seeded conversations revalidated after
Windows resumed. The read-only audit at `05:16:19Z` retained new native snapshots;
the exact process/executable binding check at `05:17:22Z` found every process
alive and every transcript byte-identical to its original seed snapshot.
Each conversation still had one human input and its native normal READY end,
with no benchmark, Monitor, intervening input, interruption or compaction.
No session was replaced or reseeded. The paired context differences remain
3.8912%, 0.9678% and 0.5834%. The additional `rules/chat.md` read in six sessions,
but not `pair-03-b`, remains a preparation limitation. Provider and compaction
configuration remain unknown.

Local evidence is under
`a.shared-wait-service/claude-tabs-20260916-180128-11adaf42/resume-audit-20260917-051619/`.
It includes `audit.json`, `resume-bindings.json` and all seven native snapshots.
The replay at `05:43:05Z`, retained in
`a.shared-wait-service/claude-native-replay-20260917-054305.json`, passed all seven
seeded transcripts and the separate unseeded smoke through the common
`2.1.273` adapter without parsing gaps. It detected each seeded native normal
end, including the deferred-tools attachment chain. Identical completed usage
repeated across content blocks is counted once while individual tool calls are
retained. Known versionless, timestamp-less session metadata and textual tool
errors are handled explicitly; unknown evidence still produces a gap.

The common Monitor bridge and Claude observer passed the full Groundhog walk
at `06:14:28Z`: 3,188 tests and 100% configured coverage, with zero failures,
warnings or xfails (`outliers=skipped`, `excluded=skipped`). The retained log is
`a.shared-wait-service/ghog-claude-integration-final.log`. Their file watches
arm before readiness, and event release
requires exact successful Monitor registration plus native normal turn end.
Fresh timing starts with benchmark execution and its new normal end; the
overnight READY interval contributes no measured idle time. A separate audit
retains native receipt, useful continuation, consumption and observation windows
without certifying complete request accounting.

Regression tests first reproduced and then closed an incomplete-JSON publication
race and a functional-audit path that ignored parser-generated gaps. A separate
ordinary Windows file-watch check observed the atomic publication in 0.006 seconds.
Generated child launchers assign unique environment setup IDs so the Monitor and
confirmation processes cannot collide on the setup scripts' temporary files.

The ordinary Windows launcher preflight also passed: the generated Monitor,
confirmation and consumption scripts completed with one compact event line and
one consumption. Its evidence is
`a.shared-wait-service/claude-launcher-preflight-d74d1bd8167d4837bd26e7ac4d373268/`.
This used a one-second synthetic source and an ordinary-code normal-end gate;
it sent no input to Claude and is not a measured trial. Two earlier preflights
remain retained: `claude-launcher-preflight-6a32834d9e704d88909a686920684c02`
hit its outer setup timeout, and
`claude-launcher-preflight-0d9850cf02ac4dfa9c0547db9f6f8528` exposed an incomplete
dummy manifest in the operator check. The successful check corrected that
fixture and allowed longer setup time without changing any measured bound.

The exact seven process and transcript bindings passed another read-only check
at `06:18:32Z`; preparation rechecked every original transcript hash before
claiming its thread. The complete series is frozen under
`a.shared-wait-service/claude-controlled-20260917/`, including exact manifests,
prompt files, stream offsets and copies of the validated implementation.
The [controlled Claude export](probe-claude-controlled.v0.13.0.shared-wait-service.json)
records each run's preparation state and preserves the original ordering.
The baseline observer was verified ready at `06:26:07Z`, bound to its native
session with the file watch armed (Python PID `49456`). Its ordinary process was
waiting for the exact benchmark prompt; no trial observer had been launched.
Readiness evidence is `baseline/observer-ready-verified.json` under
that series directory. No measured source or native benchmark execution had
started at that verification.

The installed CLI help exposes no verified command for subsequent input into
these already-open interactive sessions. Timed prompts therefore require manual
submission, one at a time, after each observer is verified ready. All seven tabs
must remain open until the controlled observations are finished.

The human submitted the exact baseline prompt. Native evidence records actual
benchmark execution at `06:35:06.320Z` and its new normal armed turn completion
at `06:35:45.384Z`. The original observer (PID `49456`) completed and exited after
retaining 600.014624 seconds of unchanged source and a separate 120.013902-second
drain. Observation ended at `06:47:45.412526Z`; `observer-finished.json` was
published at `06:47:45.429115Z`. The overnight READY interval is excluded.

The independent audit passed all 25 checks at `06:48:15.551212Z`. It verifies
the retained stream hashes and original seed prefix, one exact human prompt,
observer readiness before that prompt, exact registration and native normal-end
binding, unchanged exposed configuration, no interruption or compaction, and
both complete observation windows. No Monitor invocation, consumption or
assistant activity occurred after the normal end. Baseline artifacts are
retained under `a.shared-wait-service/claude-controlled-20260917/baseline/`:
`audit.json`, `independent-audit.json`, `report.json`, the exact manifest and both
hashed native/probe snapshots.

The three observed response-usage completions during baseline setup total
322,259 input tokens (237,277 cache-read), 991 output tokens and 624 reported
reasoning tokens. These fields are reported separately; no additional overlap
assumption is introduced. After native normal end there were no observed usage
completions or assistant/tool-call records. One bookkeeping observation remained.
The common accounting report stays inconclusive because complete request-attempt
coverage is unknown; this functional baseline does not prove zero inference or
quota savings.

The `claude-pair-01-a` observer was verified ready at `06:48:44.019346Z`
(Python PID `47452`) before the human submitted its exact prompt. Native
execution began at `06:52:34.755Z`. Its complete observation finished at
`07:01:43.773753Z`; the original observer exited, and the independent audit
passed all 26 functional/evidence checks at `07:02:51.152675Z`.

| Claude A1 boundary | Native or durable evidence, UTC on 2026-09-17 |
| --- | --- |
| Source start | `06:53:08.198024Z` |
| Source ready | `06:57:08.201890Z`; 240.003865 seconds after registration |
| Useful consume invocation | `06:57:13.091Z`; 4.889110 seconds after readiness |
| Durable consumption | `06:57:42.043756Z`; exactly once |
| Native `WAIT_TEST_DONE` normal end | `06:57:43.723Z` |
| Duplicate window ended / separate drain began | `06:59:43.741405Z`; 120.018405 seconds after final end |
| Observation finished | `07:01:43.773753Z`; separate drain 120.032348 seconds |

The useful-wake measure conservatively uses the native consume invocation,
which independently validates the outcome; the wrapper's environment setup
precedes durable consumption. No human nudge, Monitor invocation, changed seed
prefix, parser gap, interruption or compaction occurred. Native consumption and
final completion belong to the original human benchmark turn. Retained evidence
is under `a.shared-wait-service/claude-controlled-20260917/pair-01-a/`:
`audit.json`, `independent-audit.json`, `foreground-protocol-audit.json`,
`report.json`, and both hashed retained streams.

A1 has a retained initial-yield protocol deviation. It launched `source.ps1`
through PowerShell with `run_in_background: true`; the tool returned task
`barr4jagv` after 2.763 seconds. Four subsequent calls on that exact task used
`TaskOutput(block=true, timeout=60000)`. The loaded native TaskOutput schema
confirms that this timeout is a blocking wait bound. Read-only inspection of
the installed PowerShell definition exposes execution timeout and background
options but no initial-yield parameter. A background launch is not a verified
1,000-ms or minimum foreground yield. The separate protocol audit retains the
definition, executable hash, actual arguments and this limitation; functional
success does not turn A1 into an exact implementation of the initial-yield
protocol. The measured run was not retried.

A1's nine observed response-usage completions total 1,007,038 input tokens
(917,588 cache-read), 2,309 output tokens and 1,231 reported reasoning tokens.
During the fixed source interval, five observed completions total 562,167 input
tokens (558,732 cache-read), 928 output tokens and 334 reported reasoning tokens.
After final completion there are 20 bookkeeping observations and no observed
assistant/tool-call or usage-completion records. Request-attempt coverage
remains unknown; neither these counts nor eventual pair differences establish
quota savings. Pair comparisons must retain A1's initial-yield limitation.

### Retained Claude B1 failure and continuation repair

B1 executed in its original session after observer readiness at `07:04:25Z`.
Its Monitor invocation began at `07:24:23.916Z`, registration started the source
at `07:24:45.211884Z`, and the native armed turn ended at `07:24:53.539Z`.
The source became ready at `07:28:45.241160Z`, after 240.029275 seconds.
The ready event reached the same session at `07:28:45.608Z`; a separate native
notification reported that the same Monitor stream ended at `07:28:45.613Z`.
That second notification's parent is the ready notification.

Claude automatically invoked the exact consume script at `07:28:49.474Z`,
4.232840 seconds after source readiness. The observer incorrectly required the
consume turn to have the ready notification's UUID; native telemetry correctly
assigned the second notification's UUID to the continuation. The observer
therefore recorded `Consumption lacks exact native continuation binding` and
suppressed consumption. The script failed, Claude reported failure and did not
emit `WAIT_TEST_DONE`. There was no human nudge or measured retry.

The original observer retained evidence through `07:33:45.263386Z` and exited
with status `failed`. Its independent audit also failed. The missing successful
final prevented explicit duplicate-window and separate-drain markers; the
longer failure retention is not reclassified as passing those gates. Original
manifests, implementation snapshots, native streams, invalidation, audit and
independent audit remain under
`a.shared-wait-service/claude-controlled-20260917/pair-01-b/`.
Native stream SHA-256 is
`d199d839c8b4f88f90a07be205503ac8cf659f01ccb29c97e3e1b6609ac90f32`;
probe stream SHA-256 is
`a4007090450c5e63606bd2f5a1af89f93e8d4ed532cafbfb7b3366e4c6f9d97a`.

The repair binds the inspected ready-to-completed-notification ancestry,
including exact task and Monitor invocation IDs, without merging native UUIDs
or accepting unrelated input. The regression first reproduced B1's exact
binding error. The correction passed 39 focused checks, then a fresh complete
Groundhog walk: 10 affected checks and all 3,198 full-suite tests passed with
100% configured coverage. `ghog status` confirmed `state=done exit=0` at
`2026-09-17T09:47:09+02:00`; failures, warnings and xfails were zero, and
duration outlier/exclusion checks were reported skipped. Retained logs are
`a.shared-wait-service/ghog-claude-continuation-red-regression.log`,
`ghog-claude-continuation-focused-green.log` and
`ghog-claude-continuation-green.log` in that same directory.

Execution revision `monitor-completion-01` records only the changed observer
implementation for the four unstarted trials. Its source snapshot is under
`implementation-revisions/monitor-completion-01/` in the controlled series;
each pending run has an additive `execution-revision.json` binding its original
manifest and prompt hashes to the validated implementation. Original manifests,
prompts, seeds, configuration, UUIDs, offsets, event IDs, timing bounds and thread
claims are unchanged. `continuation-after-pair-01-b.json` records the failed
audit's hash and the continuation assessment. B1 is neither retried nor relabeled.
The four then-unmeasured sessions retained their original seeds.
The `pair-02-b` observer was verified ready at `07:49:28.367945Z` (PID `39212`).
The final handoff check at `07:49:58.480382Z` verified all seven original
processes, unchanged transcripts for the four pending sessions, and the exact
validated execution revision. The human subsequently submitted B2's exact prompt
once; its completed observation is recorded below.
Pair 1 supports only a descriptive comparison with A1's initial-yield deviation
and B1's failed consumption retained. Request accounting remains unknown.
Across the whole benchmark, A1 recorded 1,007,038 input / 2,309 output tokens
in nine usage completions; failed B1 recorded 686,403 input / 1,688 output in
six completions. B minus A is -320,635 input and -621 output, with three fewer
observed completions. During the fixed source interval, A1 recorded five
completions and B1 one, including B1's armed response. B1's interval after
normal end and before readiness contains no observed assistant, tool or
usage-completion activity. These differences compare a successful foreground
run with a failed B run and cannot establish equal completed work or savings.

### Audited Claude B2 continuation after repair

B2's native Monitor invocation began at `07:59:06.166Z`; the source started at
`07:59:29.011345Z` and its native armed turn ended at `07:59:37.137Z`.
The source became ready at `08:03:29.047235Z`, after 240.035891 seconds.
The exact ready notification arrived at `08:03:29.399Z`, followed by the same
Monitor's completed-stream notice at `08:03:29.402Z`. The observer recorded their
exact parent relationship, task `bw3xu9w9q` and invocation
`toolu_016iCZh7YHE8VCkTgqmGv8MU` in `native-continuation.json`.

The automatic continuation invoked consumption at `08:03:34.670Z`, 5.622765
seconds after readiness. Durable consumption succeeded once at
`08:03:57.856954Z`, followed by native normal `WAIT_TEST_DONE` completion at
`08:03:59.517Z`. There was no human nudge. The duplicate window lasted
120.012801 seconds, and the separate drain lasted 120.037018 seconds.
The original observer finished at `08:07:59.566818Z` with all functional checks
passing. Independent replay at `08:08:21.281061Z` passed all 37 checks, including
exact continuation ancestry, both windows, unchanged original seed prefix and
configuration, and the validated execution revision's source and log hashes.

B2 recorded six response-usage completions across the benchmark: 657,026 input
tokens, including 570,308 cached input, and 1,195 output tokens. Its separately
reported reasoning usage is 476. During the 231.910235 seconds after armed
normal end and before source readiness, the native stream contains one
bookkeeping record and no observed assistant, tool or usage-completion activity.
The complete duplicate/drain interval likewise contains only 14 bookkeeping
records. The full source interval includes the armed response's completion;
its observed usage remains separate from the quiet interval in the export.

Retained evidence is under
`a.shared-wait-service/claude-controlled-20260917/pair-02-b/` and in the
[controlled Claude export](probe-claude-controlled.v0.13.0.shared-wait-service.json).
The native stream SHA-256 is
`00c99efa91cf178235adce514523a6874d33fec39897622a03315ec89238458c`;
the probe stream SHA-256 is
`c89c2f28062bc14faedcedbdf5a8a815006665250047f37e4881a5e8d8d4394f`.
B2 demonstrates the repaired functional route; B1's failed result remains
unchanged. The completed pair 2 comparison is recorded below. Request-attempt coverage
remains unknown, and no quota-savings conclusion follows from this pass.

After B2's completed audit, A2's observer was verified ready at
`08:08:45.823717Z` (PID `44488`) in original session
`52f4b8f8-c81a-40c2-b062-adca57d442b9`. A2 was ready for its exact manual benchmark
prompt; A3 and B3 then retained their original seeds with no launched observers.
The final handoff check at `08:10:06.636885Z` confirmed all seven exact original
processes, unchanged transcripts for A2, A3 and B3, and A2's running observer
bound to the validated execution revision. A2 execution had not started.

### Audited Claude A2 and completed pair 2

The human submitted A2's exact prompt once at `08:19:20.367Z`. Its native
registration call began at `08:19:27.746Z`, after verified observer readiness.
The source started at `08:20:03.229763Z` and became ready at
`08:24:03.230529Z`, after 240.000766 seconds. The first useful consume call
followed at `08:24:06.932Z`, giving 3.701471 seconds latency. Durable consumption
succeeded once at `08:24:34.374971Z`, with native normal `WAIT_TEST_DONE`
completion at `08:24:35.957Z`. The original observer retained a 120.001251-second
duplicate window and separate 120.087471-second drain, finishing at
`08:28:36.045721Z`. All 29 independent checks passed at `08:29:06.160037Z`.

The foreground audit retains the installed-schema limitation independently for
A2. Its single PowerShell source launch used `run_in_background=true` and
returned task `bi7na019t` after 2.817 seconds. Four TaskOutput calls used that
exact task with `block=true` and `timeout=60000`; their observed durations were
60.041, 60.109, 60.051 and 37.926 seconds. The exposed PowerShell definition has
no initial-yield parameter. All seven protocol-evidence checks passed, with
classification `deviation-initial-yield-unavailable`, not exact conformance to
the prescribed initial-yield protocol. No measured retry or Monitor substitution
occurred.

Retained A2 evidence is under
`a.shared-wait-service/claude-controlled-20260917/pair-02-a/`. The native stream
SHA-256 is `08be883858213e175329ec11c8bf7f39c20d705d50898c664c4510f065e957dc`;
the probe stream SHA-256 is
`719e3494a34438f33057bc7c7314de82043ec5839df94e30a2cee76874bfd3c3`.
The post-final windows contain 20 bookkeeping records and no observed
assistant, tool or usage-completion activity.

Pair 2 ran in the required B/A order with both arms on the recorded
`monitor-completion-01` execution revision. Their frozen contexts differ by
0.967780%, within the unchanged 5% gate. Both functional results passed.

| Observed measure | A2 | B2 | B minus A |
| --- | ---: | ---: | ---: |
| Whole-benchmark input tokens, including cache | 1,101,870 | 657,026 | -444,844 |
| Cached input tokens | 1,013,738 | 570,308 | -443,430 |
| Output tokens | 2,209 | 1,195 | -1,014 |
| Usage completions | 10 | 6 | -4 |
| Tool calls | 9 | 5 | -4 |
| Source-interval input tokens | 665,078 | 111,638 | -553,440 |
| Source-interval usage completions | 6 | 1 | -5 |
| Source-interval tool calls | 6 | 0 | -6 |

Whole-benchmark usage includes setup, waiting, validation, consumption and final
response, excluding seeding. Reasoning usage is reported separately: 1,052 for
A2 and 476 for B2. The source interval begins at durable registration and can
include setup or armed-response completions. B2's distinct interval after
normal end and before readiness contains no observed assistant, tool or usage
completions. Usage is assigned by completion timestamp; complete request-attempt
coverage remains unknown. These descriptive differences retain A2's protocol
deviation and do not establish strict zero inference, quota or billing savings.

After A2's completed observation and audits, A3's observer was verified ready at
`08:30:04.845702Z` (PID `3960`) in original session
`eb9b9f2e-d5ab-4e7f-8311-18e483c9776a`.
The final handoff check at `08:31:58.471880Z` verified all seven exact original
processes, unchanged A3/B3 transcripts, and A3's running observer with the
validated execution revision. A3 execution had not started at that handoff.

### Audited Claude A3 and final B3 preparation

The human submitted A3's exact prompt once; native registration execution began
at `08:36:25.450Z`, after observer readiness. The source started at
`08:36:47.729Z` and became ready at `08:40:47.733Z`, after 240.003726 seconds.
The first useful consume call followed at `08:40:51.843Z`, giving 4.109808
seconds latency. Durable consumption succeeded once at `08:41:23.755Z`, with
native normal `WAIT_TEST_DONE` completion at `08:41:25.310Z`. The original
observer retained a 120.013253-second duplicate window and separate
120.011632-second drain, finishing at `08:45:25.335Z`. All 29 independent checks
passed at `08:45:53.032Z`, including the unchanged seed, configuration,
preparation and validated execution-revision bindings.

A3's separate foreground audit passed all seven protocol-evidence checks and
retains `deviation-initial-yield-unavailable`. Its single PowerShell source
launch used `run_in_background=true` and returned task `bmkle160g` after
2.596 seconds. Four TaskOutput calls used that exact task with `block=true`
and `timeout=60000`; observed durations were 60.101, 60.023, 60.048 and 35.269
seconds. The installed PowerShell definition exposes no initial-yield
parameter, so exact initial-yield conformance remains unestablished. No
measured retry or Monitor substitution occurred.

Retained A3 evidence is under
`a.shared-wait-service/claude-controlled-20260917/pair-03-a/`. The native stream
SHA-256 is `2445ec15f83d89c0d38d24e892ac8e8b9b9225ada700679de8fb8f91369a69af`;
the probe stream SHA-256 is
`0e091866cbe8d8fd4b06a861b88891160371520a30754551018cc2b7c9bf787e`.
The post-final windows contain 20 bookkeeping records and no observed
assistant, tool or usage-completion activity.

A3's whole benchmark contains 10 usage completions and nine tool calls, with
1,124,069 input tokens including 1,033,952 cached tokens, 2,562 output tokens
and separately reported reasoning usage of 1,474. The source interval contains
six usage completions and six tool calls, with 676,460 input tokens including
671,614 cached tokens, 1,637 output tokens and reasoning usage of 960. These
counts exclude seeding and assign usage by completion timestamp. Complete
request accounting remains unknown; they do not establish quota savings.

After A3's completed observation and audits, B3's observer was verified ready
at `08:46:52.623532Z` (PID `12144`) in original session
`52d8bc32-e3af-4db8-b7b1-a8a22bdaff87`. At that preparation boundary B3 was
the final unmeasured trial. Pair 3's frozen context difference is 0.583372%,
within the unchanged 5% gate. Its completed observation and audit follow.
The final handoff check at `08:48:49.989539Z` verified all seven exact original
processes, B3's unchanged transcript and prepared prompt, and its running
observer bound to the validated execution revision. B3 execution had not started.

### Audited Claude B3 and completed controlled comparison

B3's human-submitted prompt produced native Monitor execution at
`08:57:22.367Z`. Its source started at `08:58:01.265Z`, after which the armed
turn ended normally at `08:58:10.051Z`. Readiness at `09:02:01.289Z` followed
240.023577 source seconds. The native consume invocation at `09:02:13.195Z`
establishes first useful automatic continuation after 11.905928 seconds.
Consumption succeeded once at `09:02:39.831Z`; native `WAIT_TEST_DONE` ended
normally at `09:02:41.487Z`. The 120.019871-second duplicate window and separate
120.046461-second drain finished at `09:06:41.553Z`. All 37 independent checks
passed at `09:11:09.334Z`, including exact Monitor schema, successful startup,
native normal-end gating, both notification UUIDs and their exact ancestry,
one useful consume call, one final completion and unchanged execution revision.

B3 retains original thread `52d8bc32-e3af-4db8-b7b1-a8a22bdaff87`, source
`f5c25865-a938-4f0a-8913-e627990d8a4d`, wait
`456ec300-997a-46e9-ad1f-a659e1c625e1`, and event
`6e410fef-1cf7-43ca-ab18-726b68f6d4d9`. Its native stream SHA-256 is
`c480db242625f4c1550e7373c6941db0e584704754acc8e0ff98458c03a20c21`
(718,464 bytes, offset 628,878); its probe stream SHA-256 is
`95b2c1520a0ff014f735d25b3e390c0e83ffab6522848dde35ac5b67dbaec8cb`
(2,929 bytes, offset 224). No assistant, tool or usage-completion activity was
observed between armed normal end and readiness or after final completion.
Those windows contain one and 14 bookkeeping records respectively.

The [selected Claude export](probe-claude-controlled.v0.13.0.shared-wait-service.json)
contains every original manifest, audit check, revision binding, usage phase
and retained-stream hash. The completed functional results are:

| Run | Result | Source or baseline quiet (s) | First useful wake (s) | Duplicate window (s) | Separate drain (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| Baseline | Passed | 600.014624 | Not applicable | Not applicable | 120.013902 |
| A1 | Passed; initial-yield deviation | 240.003865 | 4.889110 | 120.018405 | 120.032348 |
| B1 | Failed; consumption rejected | 240.029275 | 4.232840 to rejected invocation | No passing final gate | No passing final gate |
| B2 | Passed | 240.035891 | 5.622765 | 120.012801 | 120.037018 |
| A2 | Passed; initial-yield deviation | 240.000766 | 3.701471 | 120.001251 | 120.087471 |
| A3 | Passed; initial-yield deviation | 240.003726 | 4.109808 | 120.013253 | 120.011632 |
| B3 | Passed | 240.023577 | 11.905928 | 120.019871 | 120.046461 |

Whole-benchmark observed response usage excludes seeding. Input includes the
cached portion; reasoning is reported separately and must not be added to
output. A completion count is not a request-attempt count.

| Run | Usage completions | Tool calls | Input | Cached input | Output | Reasoning |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | 9 | 9 | 1,007,038 | 917,588 | 2,309 | 1,231 |
| B1 | 6 | 5 | 686,403 | 597,189 | 1,688 | 735 |
| A2 | 10 | 9 | 1,101,870 | 1,013,738 | 2,209 | 1,052 |
| B2 | 6 | 5 | 657,026 | 570,308 | 1,195 | 476 |
| A3 | 10 | 9 | 1,124,069 | 1,033,952 | 2,562 | 1,474 |
| B3 | 6 | 5 | 683,798 | 593,862 | 1,402 | 638 |

| Pair | Frozen context difference | Both arms passed | B minus A input | B minus A cached input | B minus A output | B minus A tool calls |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 1 | 3.891155% | No; B1 failed | -320,635 | -320,399 | -621 | -4 |
| 2 | 0.967780% | Yes | -444,844 | -443,430 | -1,014 | -4 |
| 3 | 0.583372% | Yes | -440,271 | -440,090 | -1,160 | -4 |

The controlled series tested six A/B trials in three pairs, plus one baseline.
All six trial records passed identity/seed/context integrity checks; none was
invalidated. Five trials passed functionally and one failed (B1), with zero
functionally inconclusive trials. Two pairs passed in both arms and one did
not. The baseline passed separately. Benchmark validity remains qualified by
the initial-yield deviation in all three A trials and the context/configuration
limitations below; these integrity counts are not unqualified protocol passes.
Request-coverage and strict-idle conclusions are inconclusive for all six
trials and the baseline.

The following B-minus-A medians and inclusive min-to-max ranges summarize the
exported pair deltas. The all-pair column retains failed B1 and mixes the
original and repaired implementation revisions; it is descriptive only. The
successful-pair column includes pairs 2 and 3, both using the repaired revision.
For those two observations, the median is their arithmetic midpoint.

| Phase and observed metric | All 3 pairs: median | All 3 pairs: range | Successful pairs 2/3: median | Successful pairs 2/3: range |
| --- | ---: | --- | ---: | --- |
| Whole benchmark input | -440,271 | -444,844 to -320,635 | -442,557.5 | -444,844 to -440,271 |
| Whole benchmark cached input | -440,090 | -443,430 to -320,399 | -441,760 | -443,430 to -440,090 |
| Whole benchmark output | -1,014 | -1,160 to -621 | -1,087 | -1,160 to -1,014 |
| Whole benchmark reasoning | -576 | -836 to -496 | -706 | -836 to -576 |
| Whole benchmark tool calls | -4 | -4 to -4 | -4 | -4 to -4 |
| Whole benchmark usage completions | -4 | -4 to -3 | -4 | -4 to -4 |
| Source interval input | -553,440 | -561,002 to -445,993 | -557,221 | -561,002 to -553,440 |
| Source interval cached input | -548,917 | -557,954 to -444,359 | -553,435.5 | -557,954 to -548,917 |
| Source interval output | -1,241 | -1,390 to -746 | -1,315.5 | -1,390 to -1,241 |
| Source interval reasoning | -587 | -738 to -177 | -662.5 | -738 to -587 |
| Source interval tool calls | -6 | -6 to -5 | -6 | -6 to -6 |
| Source interval usage completions | -5 | -5 to -4 | -5 | -5 to -5 |

Pair 3's source interval contains six A versus one B usage completions and
six A versus zero B tool calls. B3 reports 115,458 input including 113,660
cached tokens, 247 output and 222 reasoning in that interval. Its B-minus-A
differences are -561,002 input, -557,954 cached input, -1,390 output and -738
reasoning. All three pairs' source and whole-benchmark deltas remain exported.

These comparisons are descriptive. Pair 1 compares completed A work with a
failed B consumption and cannot establish savings for equivalent completed
work. Pairs 2 and 3 used the same validated `monitor-completion-01` revision
within each pair and passed functionally. Every A arm retains the unsupported
initial-yield parameter and four supported 60,000-ms blocking waits. Six
sessions read `rules/chat.md` while B3 did not; provider and compaction
configuration remain unknown. Usage is attributed by completion time, without
complete request-start, retry or auxiliary-usage accounting. Three pairs do
not prove zero inference, quota savings or billing savings.

### Final Claude integrity audit and Step 2 closure

The final audit at `2026-09-17T09:11:59.194Z` passed all six aggregate checks
and every per-run integrity check. It verifies exact original identities and
single thread claims, immutable seeds/configuration/offsets, unchanged timing
bounds, sequential execution after each prior observation finished, retained
failed B1 classification, all three context gates, preserved stream hashes,
and no post-observation activity or invalidation. The validated implementation
and full Groundhog log hashes are unchanged. The
[final audit export](probe-claude-series-audit.v0.13.0.shared-wait-service.json)
retains the checks and source hashes without private transcript content.

The closure check at `09:12:14.715Z` verified all seven original processes,
unchanged final native hashes, all observers exited, and no remaining series
timer or helper process. All seven Claude tabs may be closed. No automatic
closure was performed. Raw evidence remains under
`a.shared-wait-service/claude-controlled-20260917/`, including the failed B1
audit and additive repair revision; no measured conversation was retried.

Step 2's code and live-evidence gates are complete. The final implementation
passed 39 focused checks, then 10 affected checks and all 3,198 full tests at
100% configured coverage, with zero failures, warnings or xfails; the full
walk ended at `2026-09-17T09:47:09+02:00`. Functional Codex and Claude routes
are demonstrated for the passing cases, so the no-functional-route checkpoint
does not apply. Host assumptions remain provisional for later production
adapters; Steps 3 through 8 and the eventual A/B-service comparison remain
outstanding. Complete request accounting and strict-idle support remain unknown.

### First human-started Codex baseline

On 2026-09-15, the human supplied a fresh Codex TUI thread in this checkout.
Its native `session_meta` identifies build `0.154.0`; its seed turn ended
normally with exactly `READY` at `19:52:05.784Z`. The selected native rollout
is bound by that exact UUID, rather than by choosing the newest file.

Both complete frozen drafts were verified against the tool output received by
the session. An initial mistyped seed-prompt path was corrected, and truncated
combined output was recovered through complete rereads and contiguous chunks.
After normalizing CRLF line endings, the emitted text matches both full frozen
files. No native compaction record occurred during seeding.

The last native usage record at `READY` reports 69,532 input tokens and five
output tokens: 69,537 is the recorded context-size basis. Cumulative seed usage
is recorded separately: 730,380 input, 658,176 cached input and 1,953 output
tokens. These are preparation costs, not baseline or A/B measurements.

The new measured series is `codex-initial-20260915`, with run `baseline-01`.
It uses the same seed commit and hashes listed below. Native evidence confirms
`gpt-6-astra`, `xhigh`, provider `openai`, approval `never` and full filesystem
access. The home configuration records a 120,000-token automatic-compaction
threshold; project configuration supplies the full-access override. No profile
argument appears on the live Codex process commands. Transport environment
presence is recorded from the independent observer only; the transcript does
not expose the measured process's environment.

The driver successfully published the baseline manifest before its benchmark
prompt. Native evidence records the human-submitted benchmark at
`20:17:28.028Z` and normal completion of its exact registration turn at
`20:18:38.790Z`. The 600-second unchanged-source interval ends at
`20:28:38.790Z`; the separate 120-second telemetry drain ends at
`20:30:38.790Z`. The seed turn's `READY` timestamp does not start this interval.

The first independent observation helper exited before collection because it
expected `event_msg/user_message`; this build retained the submission as
`response_item/message` with role `user`. Its error log is preserved. The
corrected helper bound the existing registration at `20:20:20.330128Z` and
replayed native evidence from the original pre-prompt offset. The measured
conversation and registration were not restarted, and their timestamps remain
unchanged. A separate ordinary process retained the finite native snapshot and
baseline summary after observation finished at `20:30:38.865443Z`.

**Baseline observation completed; strict-idle evidence remains inconclusive.**
The source stayed unchanged through the full 600-second interval and separate
120-second drain. The selected native transcript contains no usage records,
tool calls or user messages after normal completion during those windows.
Before normal completion, the benchmark turn produced six usage-bearing
completions totaling 439,843 input tokens, 432,000 cached input tokens and
1,086 output tokens. Seed usage is excluded from those totals.

The collector retains `status: inconclusive`, incomplete request/usage coverage,
and no strict-zero-inference claim. Its trial-shaped report also lacks source
readiness and final-wake boundaries, which an unchanged-source baseline does
not produce; baseline duration is recorded separately in `baseline-summary.json`.
No observed usage after normal end is not proof of complete request coverage,
and this baseline does not test automatic wake. Local evidence is retained under
`a.shared-wait-service/inspection/` and
`a.shared-wait-service/codex-initial-20260915/baseline-01/`, including seed proof,
request, manifest, benchmark prompt, original helper error, recovery evidence,
`report.json`, `baseline-summary.json` and `native-final-snapshot.jsonl`.

### First Codex A trial completed

The next human-started session ended its seed turn with exactly `READY` at
`20:34:13.938Z` on 2026-09-15. Both complete frozen seed texts were verified
against the native tool outputs after an initially truncated combined read was
recovered with individual chunks. Its latest native context total is 73,033
tokens, with no recorded compaction. Exposed native settings and both configuration
file hashes match the frozen series; the measured process environment remains
unexposed.

The exact UUID is bound in the local `pair-01-a` manifest. The benchmark prompt
was published after that manifest, and an independent observer started at
`20:40:07.824Z`, before human benchmark submission at `20:43:04.555Z`.
It bound the committed registration and exact registering turn, then observed
the source, duplicate window and telemetry drain.

| Measurement | Observed result |
| --- | --- |
| Source interval | `20:44:20.3088965Z` to `20:48:20.3211224Z`, 240.012 seconds |
| Initial pending return | `20:44:35.872Z`; 224.449 seconds before readiness |
| First useful consume invocation | `20:48:29.187Z`, 8.866 seconds after readiness |
| Consumption | Once at `20:48:57.4549844Z`; no duplicate consumption |
| Final normal completion | Exact `WAIT_TEST_DONE` at `20:49:01.778Z` |
| Duplicate observation | Through `20:51:01.778Z` |
| Separate telemetry drain | Through `20:53:01.778Z`; observer finished at `20:53:01.805512Z` |
| Benchmark to final completion | 357.223 seconds |

The source's initial call requested a 1,000 ms yield; the host applied its
10,000 ms minimum, with 10.015 seconds reported for the initial execution.
Four subsequent source waits requested 60,000 ms each on the same execution.
One separate setup wait was also observed. No follow-up user message occurred
between benchmark submission and consumption. This is foreground continuation;
it does not demonstrate an idle native wake.

The selected transcript contains 13 usage completions after the manifest offset,
totaling 1,082,013 input tokens, including 1,064,320 cached input tokens,
and 1,533 output tokens. It separately reports 339 reasoning tokens and zero
cache-write tokens. Seed usage is excluded. Four completions during the
pending-to-readiness interval account for 345,970 input tokens and 375 output
tokens, assigned by completion timestamp only. Request-start attribution is
unavailable. No usage completions, tool calls or user input were observed after
final completion through the duplicate window and drain.

The original collector rejected the recorded `pending_return` marker, leaving
its wait duration unknown. A regression reproduced that defect; the corrected
parser and CLI accept this timing marker without giving it coverage authority.
`report-reprocessed-01.json` replays the retained native snapshot and probe
journal, preserving the original manifest, report and summary. It restores
the 224.449-second interval and leaves usage and other measured totals unchanged.
`reprocessing-01.json` records hashes, offsets and the method. Replay uses its
actual ingestion time; original per-record ingestion and monotonic drain samples
were not retained, so it does not manufacture those values and keeps
`collection_complete: false`.

Both reports remain `inconclusive`: request/usage completeness is unknown and
strict-zero-inference is false. Native tool calls currently remain generic
observations in the collector; its zero tool counters do not establish absence.
The source/setup wait counts above come from `trial-summary.json` and native
call IDs. The original manifest's `native_evidence` pointer references the
baseline proof; the separate UUID-named seed proof verifies this trial's reads.

Evidence is retained under
`a.shared-wait-service/codex-initial-20260915/pair-01-a/` and the corresponding
UUID-named seed proof under `a.shared-wait-service/inspection/`.

### First Codex B trial completed observation without a wake

On 2026-09-16, the next human-started session completed its seed turn with
exactly `READY` at `06:46:02.860Z`. Both full frozen seed texts were verified
against the retained native outputs after bounded reads recovered an initially
truncated combined read. Its context total is 72,325 tokens, a 0.9694% difference
from the paired A trial's 73,033, within the required 5%. No compaction was
recorded. Native build `0.154.0`, exposed settings and both configuration-file
hashes match the frozen series. The next calendar day does not change its seed
revision or configuration.

The `pair-01-b` manifest binds the new UUID and its own seed proof before
publishing `benchmark.txt`. An independent observer started at
`06:48:51.889947Z`. The human submitted the benchmark at `06:50:18.151Z`;
the observer bound the committed registration and its exact native turn.

| Measurement | Observed result on 2026-09-16, UTC |
| --- | --- |
| Source interval | `06:51:13.4589336Z` to `06:55:13.4845824Z`, 240.026 seconds |
| Registration turn ended normally | `06:51:17.539Z`; direct native turn evidence |
| Actual quiet source interval | 235.946 seconds from normal end to readiness |
| Recipient-status result | `bridge-failed`; queue delivery `not-attempted` |
| Useful continuation and consumption | Neither observed; no final `WAIT_TEST_DONE` |
| Predeclared wake deadline | `06:56:13.4589336Z` |
| Post-wake-bound observation | Through `06:58:13.4589336Z` |
| Separate telemetry drain | Through `07:00:13.4589336Z`; observer finished at `07:00:13.523665Z` |

The registration turn ended normally before readiness. When the source became
ready, the existing-backend route could not establish an idle matching recipient,
so it retained the source result and suppressed delivery. No queue command was
submitted. The frozen native snapshot contains no later tool calls, usage
completions, user messages or compaction through observer completion. No human
nudge was submitted. With no final completion, this run has no post-completion
duplicate window or end-to-end completion time; the finite post-wake-bound
observation is reported separately.

The selected transcript contains six usage completions after the manifest offset,
all before registration's normal end: 453,897 input tokens, including 446,336
cached input tokens, and 718 output tokens. It separately reports 157 reasoning
tokens and zero cache-write tokens. Seed usage is excluded. Completion timestamps
do not establish request-start attribution or prove zero request attempts.

The observer finished its finite window, but the collector remains `inconclusive`
with `collection_complete: false`: the final measurement boundary is absent and
usage completions have no request-attempt records. Request and usage coverage
remain incomplete; `strict_zero_inference` is false. The route finding is
unavailable, not a functional pass.

A fresh read-only backend check still failed to connect to the selected local
control socket with Windows error `10050`. That diagnostic is retained in
`a.shared-wait-service/inspection/codex-backend-before-pair-01-b.json`.
Trial files are under
`a.shared-wait-service/codex-initial-20260915/pair-01-b/`, including the manifest,
benchmark, probe journal, observer bindings, `report.json`, `trial-summary.json`
and frozen `native-final-snapshot.jsonl`. The snapshot SHA-256 is
`fbb26f6fc48be859a8903e3a5381864055b8e9ba6e4eb6612fc4c681eb181557`.
UUID-named seed proof and its complete native snapshot remain under
`a.shared-wait-service/inspection/`.

### First Codex pair comparison and remaining trials

The selected pair uses A's `report-reprocessed-01.json` and B's original
`report.json`, one version per run. The existing report summarizer confirms
matching exposed configuration, seed hashes, repository identity and timing
bounds, with distinct threads and a 0.9694% context difference. The measured
process environments are not independently exposed. Both raw collector verdicts
remain inconclusive, so the passing-trial aggregate stays empty.

| Native measurement, excluding seed | A | B-prototype |
| --- | --- | --- |
| Usage completions | 13 | 6 |
| Input tokens, including cached input | 1,082,013 | 453,897 |
| Cached input tokens | 1,064,320 | 446,336 |
| Output tokens | 1,533 | 718 |
| Reasoning tokens, separately reported | 339 | 157 |
| Actual quiet source interval | 224.449 seconds | 235.946 seconds |
| First useful tool after readiness | 8.866 seconds | Not observed |
| Useful consumption | Once | None |
| Final completion | `WAIT_TEST_DONE` | Not observed |

The observed input difference is B minus A = -628,116 tokens. B did not complete
the task, so this difference does not establish savings for equivalent completed
work. Adapter attempt counts of zero in the pair summary reflect absent request
records and cannot establish zero requests or an actual request-count delta.

`a.shared-wait-service/codex-initial-20260915/pair-01-summary.json` retains both
selected reports, their hashes, matching result and interpretation limits.
The second pair's B result is recorded below; its fresh A remains outstanding,
followed by the third A/B pair. Every trial requires a fresh human-started
thread. The available-Claude determination and any required Claude baseline/trials
remain outstanding. No native route has passed; the host interface remains
provisional and item 1 cannot close.

### Second Codex B trial completed without native wake

The next human-started session completed its seed turn with exactly `READY`
at `07:12:30.278Z` on 2026-09-16. Its retained context is 67,139 tokens, with no
recorded compaction. Complete native output verification recovered both frozen
texts after an initially truncated combined read: the umbrella through a separate
complete response, and the focused draft through four bounded chunks. Verification
normalizes CRLF and ignores only trailing newline count from host rendering.
The frozen file hashes, exposed settings and both configuration-file hashes match.

B opens `pair-02`; its following fresh A must satisfy the 5% context tolerance.
The manifest binds this UUID and its own seed proof before publishing
`a.shared-wait-service/codex-initial-20260915/pair-02-b/benchmark.txt`.
A new independent observer started at `07:15:19.074199Z`, before human
benchmark submission at `07:29:38.356Z`. It bound the committed registration
and exact native registering turn.

| Measurement | Observed result on 2026-09-16, UTC |
| --- | --- |
| Registering turn ended normally | `07:30:32.372Z`, from direct native turn evidence |
| Source interval | `07:30:28.181354Z` to `07:34:28.217626Z`, 240.036 seconds |
| Quiet interval before source readiness | 235.846 seconds after normal turn end |
| Recipient status at source readiness | `bridge-failed`; delivery suppressed before queue submission |
| Useful continuation and consumption | Neither observed |
| Declared wake-window end | `07:35:28.181354Z` |
| Post-wake-bound observation end | `07:37:28.181354Z` |
| Separate telemetry drain end | `07:39:28.181354Z` |
| Observer finished | `07:39:28.214303Z` |

The frozen native evidence contains no post-registration-end tool calls, usage
completions, user messages or compaction through observer completion. The source
finished independently; no human nudge was submitted. With no final completion,
there is no post-completion duplicate window or end-to-end completion time.

Five usage completions after the manifest offset all precede registration's
normal end: 353,802 input tokens, including 345,088 cached input tokens, and 804
output tokens. Native usage separately reports 102 reasoning tokens and zero
cache-write tokens. Seed usage is excluded. Completion timestamps do not establish
request-start attribution, and the missing wake prevents an equivalent-work
savings claim. Pair 2 remains unmatched until its fresh A trial is retained.

The collector verdict is `inconclusive`, with `collection_complete: false` and
strict-zero-inference false. Its gaps are missing request-attempt records for
usage completions and a missing measurement boundary because no final completion
was observed. Request completeness remains unknown; zero observed activity does
not establish strict idle support.

The manifest, benchmark, probe journal, observer bindings, `report.json`,
`trial-summary.json` and frozen `native-final-snapshot.jsonl` are retained under
`a.shared-wait-service/codex-initial-20260915/pair-02-b/`. The snapshot SHA-256 is
`f5873976e8e7130447cbb028886c91db068a7c04e356a036e0033a951985ca29`.
The UUID-named seed proof and complete native seed snapshot remain under
`a.shared-wait-service/inspection/`. This repeats B1's unavailable route finding;
it does not establish the underlying backend failure's cause.

### First A2 preparation rejected for context mismatch

The human-started thread `01a0a934-f1de-70c3-ba3e-ef45dc4b11c6` completed its
seed turn with exactly `READY` at `07:55:10.889Z` on 2026-09-16. Both frozen
texts were verified in full through four native output chunks each after a
truncated combined read. Exposed settings and both configuration-file hashes
match the series; no compaction was recorded.

Its retained context is 72,982 tokens against B2's 67,139. The driver's declared
comparison, `abs(A - B) / max(A, B)`, is 8.006%, exceeding the fixed 5% limit.
The driver retained `pair-02-a-invalid-01/invalid.json` with reason
`Pair context differs by more than five percent`. It published no manifest or
benchmark, and the measured trial order remains unchanged. No benchmark observer
or synthetic source was started for this preparation. The rejected UUID remains
claimed against reuse; A2 requires another fresh human-started session.

The original request and rejection are retained under
`a.shared-wait-service/codex-initial-20260915/pair-02-a-invalid-01/`. The exact
UUID's READY evidence, full-read proof and frozen native seed snapshot remain
under `a.shared-wait-service/inspection/`. The snapshot SHA-256 is
`b579d6871ff719fa42d7b5559c4f75e1b040140c8ca982754a889ea9fc3df15d`.
This preparation rejection is separate from the two B trials' route failures.

### Second A2 preparation and proposed repeatable seeding

The next human-started thread `01a0a939-4b84-7f51-8a46-8374482d62d8` reached
`READY` at `08:00:26.712Z` on 2026-09-16. Full reads were verified against the
frozen hashes. Native settings and configuration-file hashes match; there was
no compaction. Its 76,401-token context differs from B2's 67,139 by 12.123%
using the declared comparison. The driver retained `pair-02-a-invalid-02` as
invalid and claimed its UUID against reuse. No manifest, benchmark, source or
benchmark observer was started; measured trial order remains unchanged.

Its native seed snapshot SHA-256 is
`1e030261885bde16577b3b0d7937744f6fba9bb78574793c058a3fdf0f1363d1`.
The original request and rejection remain in that run directory; UUID-named
READY evidence, full-read proof and snapshot remain in the inspection directory.
Both rejected preparations also have allowlisted entries in the redacted
manifest artifact. Neither contributes a measured A outcome.

The transcripts show different tool-discovery output, truncated combined reads
and repeated file content during seeding. These are observed sources of starting
context variation, not measured treatment effects. Two fresh preparations have
now failed the same matching gate. A [repeatable seed-delivery proposal](seed-procedure.v0.13.0.shared-wait-service.md)
uses 17 ordered chunks, each at most 9,000 UTF-8 bytes, with exact reconstruction
of both frozen files verified independently. The proposed input and chunk hashes
are retained under `a.shared-wait-service/codex-controlled-proposal-20260916/`.
No replacement series has started. Adopting that procedure requires a separate
series and fresh baseline/matched trials; it cannot repair or replace B2's
existing context evidence.

### Overnight interruption and backend availability check

The human reported an interrupted Windows session overnight and asked whether
it affected a monitoring process. The first B observer was started anew on
2026-09-16 at `06:48:51.889947Z` and finished normally at `07:00:13.523665Z`.
It observed the registering turn, source readiness and all finite windows.
That trial did not depend on a harness observer surviving overnight.

The same Codex control-socket error `10050` was already retained during the A
trial on 2026-09-15, before the reported overnight interruption. At
`07:13:00.1148478Z` on 2026-09-16, a new read-only check again returned exit 1
and error `10050`; the selected control-socket path did not exist, and the
point-in-time process inventory contained no `codex app-server` process.
Windows reported its last boot at `2026-09-13T23:42:49.500Z`. This excludes an
intervening OS restart in that observation, but does not establish sign-out or
sleep history, nor the underlying cause of the backend error.

The evidence does not support an overnight loss of the harness observer as
the cause of B1's failure. The unavailable backend was observed both before and
after the interruption. The harness has not started a managed Codex daemon.
The [documented thread read](https://learn.chatgpt.com/docs/app-server#read-a-stored-thread-without-resuming)
checks runtime status without loading a stored thread, which preserves the
experiment's requirement to target the already open conversation.

The current diagnostic, redacted process roles, boot timestamp and raw local
CLI outputs are retained under
`a.shared-wait-service/inspection/codex-backend-before-pair-02-b.json` and its
adjacent stdout/stderr logs. The earlier A and B1 diagnostics remain unchanged.
No host settings or backend lifecycle were changed for B2.

### Windows local socket capability follow-up

A read-only check at `08:07:15.483506Z` on 2026-09-16 successfully created and
closed an unbound Windows AF_UNIX stream socket. `sc.exe query afunix` reported
the driver running with exit code zero. Python does not expose its named AF_UNIX
constant in this environment, so the follow-up used Microsoft's documented
[AF_UNIX numeric value](https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/Networking/WinSock/constant.AF_UNIX.html).
The earlier named-constant check was insufficient to assess Windows support.

This establishes socket creation support, not a running Codex daemon, a working
control-socket connection or a loaded measured thread. It does not explain
Codex's earlier error `10050`. No listener, connection, daemon start or settings
change was made. Evidence is retained in
`a.shared-wait-service/inspection/windows-socket-capability-20260916.json` and
`windows-afunix-20260916.json` beside it.

### Configuration recorded without modification

The implementing Codex session reported model `gpt-6-astra`, reasoning effort
`xhigh`, and configured automatic-compaction threshold `120000`. HTTP and HTTPS
proxy variables and `NODE_EXTRA_CA_CERTS` were present. Certificate paths,
proxy addresses, credentials, and raw conversation content are excluded here.
Actual trial settings must be captured from each fresh measured host session;
these inspection values are not proof that another session matches.

## Bridge investigation on 2026-09-16

The operator deferred further TUI trials to investigate the bridge. Separate,
unmeasured checks used empty temporary Codex homes and the installed `0.154.0`
executable. They started no conversation, resumed no thread and submitted no
queue message. Every diagnostic app-server/proxy process was stopped after its
bounded check; raw logs and temporary homes remain local.

| Check | Observed result |
| --- | --- |
| Windows AF_UNIX bind, listen, connect and data exchange | Passed using Winsock; Windows socket support is present |
| `app-server daemon start` in an empty temporary home | Refused because that home lacks the managed standalone installation; no daemon started |
| `app-server --listen stdio://` with JSON lines | Initialization and `thread/loaded/list` succeeded; no loaded threads |
| `app-server --listen unix://` with plain JSON lines through `app-server proxy` | Socket was created, but no JSON-RPC response arrived before the deadline |
| Same Unix listener with HTTP Upgrade and WebSocket frames | Initialization and `thread/loaded/list` succeeded, both directly and through the proxy; no loaded threads |
| `app-server daemon version`, before and after creating an isolated listener | Missing socket produced `10050`; running listener produced exit `0`, status `running`, matching CLI/server version `0.154.0` |

This isolates a prototype defect: `codex app-server proxy` tunnels raw bytes;
it does not convert JSON lines into WebSocket messages. The original adapter
used the stdio wire format on that tunnel. The
[app-server transport documentation](https://developers.openai.com/codex/app-server/)
specifies HTTP Upgrade and WebSocket framing for Unix sockets. A running backend
would therefore not have been sufficient for the original adapter.

The historical B trials still failed before any queue submission. The original
home also lacked a control socket, so this new finding does not establish that
framing was their only obstacle. A controlled before/after check reproduced
`10050` with the socket absent and success with the listener present. This shows
that the diagnostic does not by itself establish broken Windows networking.
The default proxy also reached that listener with the corrected framing.
An ordinary TUI's implicit backend routing was not established by these isolated
checks. The later human check below uses explicit attachment to the same socket.

Retained evidence beneath `a.shared-wait-service/inspection/`:

- `bridge-isolation-20260916/failure.txt`: first Python address-decoding failure;
  retained separately from the subsequent Winsock check.
- `bridge-isolation-02-20260916/result.json`: Windows socket exchange and isolated
  daemon lifecycle refusal.
- `bridge-direct-20260916/result.json`: stdio success versus raw-JSONL proxy timeout.
- `bridge-websocket-20260916/result.json`: direct and proxied WebSocket success.
- `bridge-fixed-20260916/result.json`: the corrected Python transport initialized,
  listed zero loaded threads and rejected an absent UUID with an RPC error on
  the installed app server, from `08:38:00Z` through `08:38:27Z`.
- `bridge-routing-20260916/result.json`: absent-listener `10050`, running-listener
  version success and default-socket proxy success, from `08:41:14Z` through
  `08:41:49Z`.

The adapter now uses `wsproto` for HTTP Upgrade and masked WebSocket messages.
The dependency is loaded only when the native bridge is used; standalone
collection and local harness actions retain their isolated `python -I -S`
startup support.
It handles fragmented text and server pings, bounds the total input to 1 MiB,
and retains an absolute ten-second deadline for each handshake/RPC response.
Metadata reads use `app-server proxy --sock <exact-home-control-socket>`;
queue delivery specifies `--remote unix://<same-socket>`. Both retain the frozen
home/profile and exact UUID. Missing, closed or incompatible recipients still
block delivery. The transport starts only its child proxy, and never starts the
backend or loads a saved conversation.

Regression tests use a real in-memory WebSocket peer instead of a JSONL fake.
They exercise byte/message fragmentation, Unicode, pings, unrelated responses,
handshake rejection, RPC errors, EOF, read failures, size limits and deadlines.
The plan's existing no-additional-PBT decision still applies: these are fixed
adapter protocol boundaries; `wsproto` owns the general frame parser.

Further measured sessions remain deferred. Before each baseline or B trial,
the exact human-started recipient must be shown loaded and idle in the same
backend used for queue delivery. The human connection check below demonstrates
the installed CLI's explicit `--remote unix://` TUI/queue attachment. Transport
or seed changes require freshly recorded series controls; the original failed
and rejected runs remain unchanged.

### Human connection and automatic wake check

After the operator asked for the next action, a local backend was started for
one unmeasured connection check. At `2026-09-16T09:26:36Z`, its version command
reported matching CLI/server `0.154.0`; the corrected transport reached the
exact control socket and `thread/loaded/list` returned no loaded conversations.
The backend remains running for the operator's fresh TUI. This preparation
started no conversation and submitted no queue message.

The local artifacts are under
`a.shared-wait-service/codex-bridge-smoke-20260916/`: `backend-start.json`
records process ownership, `backend-ready.json` records the successful read-only
check, and `open-tui.ps1` explicitly connects a human-started TUI to that socket
and asks only for `BRIDGE_READY`. The launcher was syntax-checked but not run by
the implementing session. The human launched it and supplied the exact UUID
`01a0a9ab-22fe-7a80-a6a2-db41f36e41b6`.

The corrected transport found that UUID loaded and idle in the prepared backend.
Native metadata confirmed build `0.154.0`, model `gpt-6-astra`, effort `xhigh`
and this checkout. Its initial turn ended normally with `BRIDGE_READY` at
`10:02:45.947Z`. Before sending, the diagnostic rechecked idle status and verified
that the bound native stream had not changed since that completion.

One exclusively created, flushed send intent recorded event
`93f3eab7-5014-4e0d-8e4c-3d13037fea95`, the exact UUID and expected reply before
invoking `queue --remote unix://<same-socket> --thread <exact-UUID> --message ...`.
It sent once and did not resume or replace the conversation.

| Observation on 2026-09-16 | Retained result |
| --- | --- |
| Dispatch began | `10:06:18.090217Z` |
| Queue acceptance | Exit `0`; message `01a0a9ae-88a5-77f0-aece-563793f04293` |
| New native turn started | `10:06:22.973Z`; turn `01a0a9ae-88bc-7752-8914-5b2e032be53a` |
| Expected reply and normal completion | `10:06:25.806Z`; exact `BRIDGE_WAKE_OK 93f3eab7-5014-4e0d-8e4c-3d13037fea95` |
| Dispatch-to-completion interval | 7.715783 seconds, within the diagnostic's 60-second observation bound |
| Human observation | The operator confirmed that the reply appeared automatically in the open idle TUI, without typing or clicking |

`recipient-check.json` and `recipient-before.jsonl` retain the pre-send identity,
normal completion and stream snapshot. `wake-intent.json`, `wake-result.json`
and `wake-observed.jsonl` retain dispatch and native response evidence.
`operator-confirmation.json` retains the separate human observation. The file
observer exited after the response; no retry or benchmark observer is running.

This demonstrates a basic automatic reply in the human-started idle TUI through
the corrected bridge. It is not a baseline or matched trial, does not exercise
durable wait-result consumption or the full duplicate/drain windows, and cannot
establish strict-idle savings or complete request coverage. The smoke TUI may
be closed; the backend remains available and the matched series stays deferred.

### Named Terminal tabs and file delivery on 2026-09-16

The operator requested a launcher to replace repeated manual TUI opening, UUID
reporting and instruction pasting. The
[named-tab procedure](codex-tabs.v0.13.0.shared-wait-service.md) opens fresh TUIs
on the existing backend, uses a unique setup message to bind each exact UUID,
assigns a native session name and queues instruction-file contents by that
binding. It records setup separately from seed and benchmark delivery. The
controlled preparation requires a new baseline and trial series.

An initial one-tab diagnostic passed. A subsequent single-window, two-tab
diagnostic verified distinct bindings and delivery to each original live TUI:

| Tab alias | Exact thread UUID | Final native reply |
| --- | --- | --- |
| smoke-a | `01a0a9c6-64f5-7a70-8ba6-f14dbbf04128` | `TAB_ROUTED_A_é` |
| smoke-b | `01a0a9c6-90ff-7672-9b33-461e4ba0089b` | `TAB_ROUTED_B` |

Each thread completed three unmeasured turns: identity setup, seed-file delivery
and a distinct routing check. Native user-message records preserved the exact
file contents, including Unicode, quotes, backticks and shell-like expressions.
The verification also rejected a duplicate seed delivery and a benchmark
manifest naming the other thread, without sending either rejected message.
Queue receipts and native completion evidence are retained locally under
`a.shared-wait-service/codex-tabs-smoke-two-20260916/`; `verification.json` was
written at `2026-09-16T10:40:07.083776+00:00`.

The setup-only single-tab check is retained separately under
`a.shared-wait-service/codex-tabs-smoke-20260916/`. None of these diagnostic
conversations is a measured trial or a substitute for the fresh seven-session
series. Automatic named delivery is proven; full seed reads, context matching,
the timed baseline and complete A/B workflow still need their own evidence.

The final `ghog day` completed at `2026-09-16T12:39:27+02:00` with exit 0.
Repository code checks passed; the full test run reported zero failures,
warnings or expected failures and 100% coverage of its configured `tools`
scope. The standalone launcher under `docs` is outside that coverage scope;
the native diagnostics above exercise its real Terminal and queue behavior.
The log is retained at
`a.shared-wait-service/inspection/tab-launcher-green-20260916.log`.
The PowerShell wrapper's Status action also passed when invoked from outside
this checkout, returning both saved UUID bindings.

### Controlled Codex seed preparation on 2026-09-16

The human invoked the seven-tab launcher. All seven conversations completed
the common setup turn and then read each of the 17 frozen chunks exactly once,
in order, before replying `READY`. Each seed used 18 tool calls, including the
required shell-policy read. Full chunk text was verified against its matching
native tool output after CRLF normalization, and concatenated chunk bytes
match both frozen draft hashes. No seed compaction occurred.

| Tab | Exact thread UUID | Retained context tokens |
| --- | --- | --- |
| baseline | `01a0aa06-a232-75e2-88d4-c26eebd6041d` | 51,356 |
| pair-01-a | `01a0aa06-a56b-74d0-8c59-5017deb3cabb` | 51,393 |
| pair-01-b | `01a0aa06-a56d-7100-83f6-4ad9a29b235a` | 51,337 |
| pair-02-b | `01a0aa06-a3fa-7f32-908e-60ae12d363bd` | 51,369 |
| pair-02-a | `01a0aa06-a796-7852-85be-356cd13e7749` | 51,332 |
| pair-03-a | `01a0aa06-a9c2-7463-8a2a-01478ded0b74` | 51,376 |
| pair-03-b | `01a0aa06-a9f5-7893-b90f-0718110a56f6` | 51,346 |

Pair context differences are 0.109%, 0.072% and 0.058%, all below the fixed
5% limit. Proofs, native seed snapshots and queue receipts are retained under
`a.shared-wait-service/codex-tabs-20260916/`; its `seed-summary.json` was written
at `2026-09-16T11:53:17.584012+00:00`.

The independent driver froze the separate `codex-controlled-20260916` series
and queued its baseline benchmark only after the durable manifest. All seed
loading finished before this measurement preparation. The driver runs the
baseline followed by A, B, B, A, A, B sequentially, preserving the original
source, wake, duplicate and drain bounds. Preparation success alone does not
establish a functional A/B result.

### Controlled-series recovery and first measured native wake

On resuming the implementing session on 2026-09-16, the original ordinary
driver process was absent. Its completed baseline, A1 and B1 reports and native
snapshots were intact. B2 had registered and ended normally, but its source
deadline had not yet elapsed. No driver completion or exception record existed;
the exact cause and duration of the observer outage are unknown.

The replacement observer verified that the original process identity was gone,
that B2 had no report or prior delivery, and that its original TUI was alive and
idle. It recorded recovery at `12:35:47.707606Z`, before the unchanged source
deadline at `12:35:48.511723Z`. It replayed the persistent native stream from the
original manifest offset without resending the benchmark or resetting the
source, wake, duplicate or drain bounds. The recovery record remains part of
B2's evidence; B2 must be distinguished from uninterrupted trials.

The resumed driver ran detached and completed the original B2, A2, A3, B3
sequence. A source deadline, queue receipt or growing log does not establish
trial completion: each run needs its immutable report, final native snapshot
and `observer-finished.json` after the required windows.

| Completed observation | Native evidence |
| --- | --- |
| Controlled baseline | Normal end `11:57:36.358Z`; 600 unchanged-source seconds and 120-second drain completed at `12:09:36.441733Z`; no tool calls or usage completions after normal end |
| A1 | Four source waits, each requesting 60,000 ms; first consume call 8.316 seconds after readiness; one consumption and exact `WAIT_TEST_DONE`; full duplicate window and drain retained |
| B1 | Original registering turn ended normally; one exact native wake message reached the same thread; first validation call 48.863 seconds after readiness, within 60 seconds; one consumption and exact `WAIT_TEST_DONE`; full duplicate window and drain retained |
| B2, recovered observer | First validation call 27.169 seconds after readiness; exact native wake reached the original idle thread; one consumption and exact `WAIT_TEST_DONE`; full duplicate window and drain completed at `12:40:48.568264Z`; observer outage remains a protocol deviation |

B1's first useful action was the post-wake tool invocation that read the
manifest and durable source status. Queue acceptance is not used as its wake
latency endpoint. Its native stream contains exactly the benchmark message and
the expected identity-bound automatic wake message, with no intervening user
nudge. No tool calls or usage completions followed final completion through
the recorded duplicate and drain windows. B1 therefore demonstrates the
measured functional route, beyond the earlier unmeasured connection check.
B2 has the same exact-message and consumption evidence, with no tool calls or
usage completions in its 234.441-second quiet interval. It records 533,684 input
and 1,544 output tokens across nine usage completions, retaining its observer
recovery qualification.

The first pair records 707,627 input / 1,972 output tokens for A1 and 511,633
input / 2,072 output tokens for B1. A1 has four usage completions during its
213.496-second pending interval; B1 has none during its 179.434-second interval
between normal end and readiness. These are observed completion totals,
including registration work, rather than complete request counts or a savings
claim. Preparation and runtime behavior vary despite matched seed context.
In particular, B1 has 69,393 uncached input tokens versus A1's 46,507, despite
195,994 fewer total input tokens. The observed cache difference prevents
treating total-input reduction as billing or quota savings.

The original collector reports remain immutable and `inconclusive`: native
request attempts are not exposed, native tool calls remain generic observations,
and useful/pending timing markers were not populated by this series driver.
The supplemental `trial-audit.json` files derive timings and tool counts from
the retained call IDs and byte offsets, verify original hashes and observed
usage totals, and preserve unknown request coverage and unsupported strict idle.
They do not turn original zero counters into evidence of absence.

Local evidence: `a.shared-wait-service/codex-controlled-20260916/`, including
`driver-resumed.json`, `resume.stdout.log`, `resume.stderr.log`, and each
completed run's `trial-audit.json`. The resumed driver and audit helper are
`a.step2-tabs-resume.py` and `a.step2-controlled-summary.py`. A separately detached
`a.step2-controlled-finalize.py` verified the exact resumed driver process
identity and recorded `finalizer-started.json` at `12:48:09.250553Z`. It waited on
that Windows process handle without interval polling. The driver recorded
completion at `13:10:12.128787Z`; the finalizer verified all seven immutable
observations and wrote `series-audit.json`, `series-audit.md` and
`finalizer-finished.json` at `13:10:13.155633Z`. No resumed-driver or finalizer
failure marker was present at the completion check. No benchmark was retried.
The audit includes seed costs, completion-timestamp phase subtotals, all paired
deltas, medians and ranges; request-start attribution remains unavailable.
The final audit hash is
`0b940ed48755fe8ce6369baada5a980798edd8089799aea83d1e83286d3d7ab9`.
The selected public export was generated only after rechecking that hash and
each original manifest, report, native snapshot, finish record and probe journal.

### Completed controlled Codex comparison

All seven observations finished: one 600-second unchanged-source baseline and
six measured trials in A/B, B/A, A/B order. Each trial retained the full
120-second duplicate window and separate 120-second drain. All six consumed
their event exactly once and completed with the exact sentinel. No duplicate
consumption, post-final tool call, post-final usage completion, native
compaction or measured-turn interruption was observed in those windows.

The three B trials each contain the expected automatic identity-bound wake
message in the original conversation after its registering turn ended normally.
Their first useful validation calls met the fixed 60-second bound. B2 retains
the observer-outage deviation described above; its measured TUI was not
restarted or prompted again. The six functional checks succeeded, with zero
functional failures in this series. Five trials had uninterrupted observers;
one recovered its observer. All six remain inconclusive for complete request
accounting. The baseline is also inconclusive for strict zero inference.
Earlier failed and invalid series are retained separately above.

| Run | Total input | Cached input | Uncached input | Output | Usage completions | Quiet/pending completions | First useful latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline registration | 227,365 | 218,880 | 8,485 | 879 | 4 | 0 | n/a |
| A1 | 707,627 | 661,120 | 46,507 | 1,972 | 12 | 4 | 8.316 |
| B1 | 511,633 | 442,240 | 69,393 | 2,072 | 9 | 0 | 48.863 |
| B2, recovered observer | 533,684 | 459,392 | 74,292 | 1,544 | 9 | 0 | 27.169 |
| A2 | 630,259 | 568,960 | 61,299 | 1,724 | 11 | 4 | 13.438 |
| A3 | 614,623 | 606,464 | 8,159 | 1,856 | 11 | 4 | 8.340 |
| B3 | 530,173 | 516,736 | 13,437 | 1,819 | 9 | 0 | 20.380 |

Input includes cached input. Uncached input is their difference. These counts
exclude seed loading and include benchmark setup, registration/startup,
waiting, validation, consumption and final response. Reasoning usage is retained
separately in the JSON export; it is not added to output to invent a billing
total. None of these completion counts certifies every request attempt.

| Run | Setup to quiet/pending (s) | Quiet/pending (s) | Readiness to final (s) | End to end (s) | Setup / quiet / after-readiness input |
| --- | ---: | ---: | ---: | ---: | --- |
| A1 | 87.531 | 213.496 | 11.734 | 312.761 | 340,600 / 243,680 / 123,347 |
| B1 | 166.104 | 179.434 | 86.231 | 431.769 | 331,392 / 0 observed / 180,241 |
| B2, recovered observer | 54.501 | 234.441 | 59.964 | 348.906 | 280,933 / 0 observed / 252,751 |
| A2 | 67.318 | 221.484 | 15.833 | 304.635 | 277,942 / 233,827 / 118,490 |
| A3 | 63.578 | 222.423 | 10.843 | 296.844 | 272,527 / 227,060 / 115,036 |
| B3 | 81.079 | 234.631 | 51.427 | 367.137 | 281,393 / 0 observed / 248,780 |

Phase usage is assigned by completion timestamp only, because request starts
are unavailable. Boundary-crossing requests cannot be attributed precisely.
Setup starts at benchmark delivery; A's pending interval starts at the first
pending fixture return, while B's quiet interval starts at normal turn end.
Recorded source durations range from 240.001 to 240.038 seconds. Each A trial
made four source-wait calls requesting 60,000 ms; each B trial made none.
No tool calls were observed during the B quiet intervals.

| Pair | Context difference | B minus A input | B minus A uncached input | B minus A output | B minus A completions | B minus A end-to-end (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.109% | -195,994 | +22,886 | +100 | -3 | +119.008 |
| 2, recovered B observer | 0.072% | -96,575 | +12,993 | -180 | -2 | +44.271 |
| 3 | 0.058% | -84,450 | +5,278 | -37 | -2 | +70.293 |
| Median | | -96,575 | +12,993 | -37 | -2 | +70.293 |
| Range | | -195,994 to -84,450 | +5,278 to +22,886 | -180 to +100 | -3 to -2 | +44.271 to +119.008 |

The median B-minus-A quiet-interval completion input is -233,827 tokens,
ranging from -243,680 to -227,060. This describes the observed completion
timestamps over unequal quiet intervals, not verified wait-induced requests.
The aggregate includes the explicitly qualified second pair; it is not a claim
of three uninterrupted valid pairs. In all three pairs, B has fewer total input
tokens and completions, more uncached input, and a longer end-to-end duration.
Cache differences and setup/resumption costs therefore remain visible.

| Seed turn | Input | Cached input | Output | Final seed-response input | First measured-response input |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 682,361 | 645,248 | 1,819 | 51,351 | 51,518 |
| A1 | 682,817 | 628,224 | 1,855 | 51,388 | 51,640 |
| B1 | 682,149 | 644,992 | 1,797 | 51,332 | 51,531 |
| B2 | 682,713 | 622,464 | 1,829 | 51,364 | 51,563 |
| A2 | 682,240 | 645,120 | 1,792 | 51,327 | 51,575 |
| A3 | 682,344 | 644,992 | 1,836 | 51,371 | 51,621 |
| B3 | 679,604 | 612,352 | 1,806 | 51,341 | 51,542 |

Each seed turn has 19 observed usage completions. These seed-only totals exclude
the earlier common tab-setup turn and are separate from benchmark totals.
Final seed-response input and retained-context token count are different native
fields; neither is silently substituted for the other.

The Codex controlled observations and evidence audit are complete. They establish
functional feasibility for the tested prototype route, with B2's recovery
qualification. They do not establish strict zero inference, quota or billing
savings, or behavior of the future shared service. Effective approval-review
settings, complete model transport/retry evidence and auxiliary usage remain
unavailable. At this Codex audit boundary, Step 2 still awaited Claude live
work. The completed Claude comparison and final Step 2 assessment appear above.

## Reproducible operator procedure

The driver is [probe.shared-wait-service.py](probe.shared-wait-service.py).
It uses its physical checkout to resolve imports from any working directory.
All run files belong under an explicit ignored `a.shared-wait-service` directory.

### Freeze an initial host series

Use the verified project interpreter. In this checkout it is
`venvs/python_3.13.9_llm-shared_no_polling/Scripts/python.exe`.

Prepare a local settings JSON with `series_id`, `host`, `build`, `schema`,
`model`, `profile`, absolute `home`, and a `configuration` object containing the
observed model, reasoning, compaction, provider, permission and transport settings.
Keep private raw settings local. Codex's base profile is named `default` in this
driver; a named profile is passed unchanged to the installed CLI.
Native schema names are `codex-native-0.154.0`, `claude-native-2.1.272`, and
`claude-native-2.1.273`. The controlled Claude series uses the last of these and
freezes the inspected actual-session `monitor_schema` in its settings.

```powershell
$repo = (Get-Location).Path
$python = Join-Path $repo 'venvs/python_3.13.9_llm-shared_no_polling/Scripts/python.exe'
$probe = Join-Path $repo 'docs/v0.13.0/probe.shared-wait-service.py'
$series = Join-Path $repo 'a.shared-wait-service/codex-initial'
$settings = Join-Path $repo 'a.shared-wait-service/settings.codex.json'
& $python $probe freeze --directory $series --repository $repo --commit 3d4b5a4643d1fba65434877d965d2c051b65e1a3 --settings $settings
```

The driver writes both full frozen copies, `series.json`, `seed-prompt.txt`, and
an indexed trial registry. The initial controls are fixed at a 240-second source,
60-second wake bound, 120-second duplicate window after final completion, and a
separate 120-second telemetry drain. An unchanged-source baseline lasts at least
600 seconds after normal end. Changed seeds/settings require a fresh series;
previous runs remain intact. The shared evidence root also prevents thread reuse
across series, including invalid attempts.

The implementing session exercised `freeze` against the recorded commit and
retained `a.shared-wait-service/codex-preparation-20260915/seed-prompt.txt`.
Its configuration is explicitly labeled inspection-only; it is not a measured
series. Both full copies were produced, with these reproducible hashes:

| Source at the recorded commit | Frozen SHA-256 |
| --- | --- |
| `docs/v0.13.0/draft.v0.13.0.no_polling.md` | `239b4aeb946909a3e6f22813cb5962dcbcdc83d7a16d775ea028d188792bf23a` |
| `docs/v0.13.0/draft.v0.13.0.shared-wait-service.md` | `fbf6f41c9fa1bb6203739519104bcede98030cd596ae39c061a466947df84f48` |

### Seed and bind each fresh conversation

1. Start a new Codex TUI, or a new available Claude session, through normal human
   input. Never measure the implementing conversation or reuse a measured thread.
2. Submit the generated `seed-prompt.txt`. Verify both files were read completely,
   record any compaction/truncation, and inspect retained context after `READY`.
3. Prepare an absolute request JSON path containing `run_id`, exact thread UUID,
   `arm`, `pair_id`, UTC epoch `ready_at`, positive `context_tokens`,
   `complete_reads: true`, `ready_marker: "READY"`, the exact `seed_hashes` from
   `series.json`, `mode: "trial"` or `"baseline"`, and `streams` containing the
   absolute native rollout/transcript path for that exact thread.
4. Run `prepare` from the independent operator process. It captures native file
   positions, verifies the exact native header and host home, and freezes durable
   controls before publishing `benchmark.txt`. An empty or unrelated log is invalid.
5. Submit that benchmark prompt through normal TUI input only after preparation
   succeeds and the Claude observer's native preflight and file-watch readiness
   are verified. Use fresh IDs for any repeat. Pair contexts must differ by at most 5%.

For the preserved seven Claude sessions, seeding is already complete. Revalidate
their exact process, transcript and frozen-seed bindings, then prepare manifests
for those identities. Do not repeat the launcher or seed input after a pause.

```powershell
$request = Join-Path $repo 'a.shared-wait-service/request.json'
& $python $probe prepare --directory $series --request $request
```

Preparation failures retain `request.json` and `invalid.json`. They do not
publish a benchmark prompt. No invalid, failed, or inconclusive result is replaced
by a later success.

### Run the independent observation

For Codex, the measured prompt performs `register --directory <absolute-run>` once. The
operator identifies that exact native turn, then starts the independent observer
in a separate ordinary terminal after registration exists:

```powershell
$run = Join-Path $series 'run-one'
$codex = Join-Path $env:USERPROFILE '.codex/packages/standalone/current/bin/codex.exe'
& $python $probe observe --directory $run --registering-turn EXACT_REGISTERING_TURN_UUID --codex-executable $codex
```

The observer and source deadlines run without model polling. For A, the measured
conversation uses the foreground `source` command with an initial 1,000 ms yield
(or the host minimum), followed by 60,000 ms waits on that same execution.
Record the actual minimum when it differs. A's source completion does not use
a native queue wake. The new named-tab procedure can queue both arms' seed and
initial benchmark instructions before their measured source interval begins.

For Codex B-prototype, native completion of the registering turn and an idle,
loaded matching recipient are required before one queue attempt. The TUI must
then automatically perform useful work, validate source/wait/event/thread IDs,
consume once, and finish exactly `WAIT_TEST_DONE`. Queue acceptance alone is
insufficient. Lost acknowledgements are retained and never automatically retried.

For Claude `2.1.273`, start `observe --directory <absolute-run>` in an independent
ordinary process **before** prompt submission. Verify `observer-process.json`
against the running process and require `observer-ready.json` with the exact
thread, passed native preflight and armed file watch. The observer binds the
prepared prompt from new native input; it does not reuse the seed's READY end.
The existing Claude launcher has no verified subsequent-prompt delivery route.
When manual input is required, provide the complete `benchmark.txt` and exact tab
only after readiness; leave all other tabs untouched.

The prepared Claude baseline invokes `register.ps1` once and ends normally with
its exact armed marker. Arm A invokes `register.ps1` and `source.ps1`, then uses
the installed foreground tool's supported initial yield and 60,000 ms waits.
Retain the actual arguments and any unsupported-protocol deviation. A tool's
execution timeout is not a yield interval.

Arm B loads the actual Monitor schema and invokes the exact `monitor_input`
frozen in the manifest. `monitor.ps1` captures launcher diagnostics separately;
its only stdout is one compact event. `confirm.ps1` verifies durable bridge
arming before the exact armed marker and native normal end. Only this native
gate permits event release. The native task notification must bind the same
thread, task, source, wait and event before useful continuation. `consume.ps1`
validates identities and outcome independently and rejects repeat consumption.

Claude observations retain `execution-started.json`, native normal end, receipt,
consumption, separate drain boundaries, stream snapshots and `audit.json`.
`observer-finished.json` records audited completion; `observer-failed.json`
records a process failure. A prompt, readiness marker or `WAIT_TEST_DONE` alone
does not permit advancing to the next trial. Preserve failures and wait until
the full observation is retained. Accounting uncertainty remains explicit even
when every functional check passes.

An operator normal-end timestamp is optional measurement evidence:

```powershell
& $python $probe mark-normal-end --directory $run
```

Use `mark --directory <run> --measurement <absolute-json>` to retain the exact
benchmark submission, A-arm `pending_return`, first useful continuation, or final completion timestamp
from observed native evidence. Its JSON contains `kind`, `at`, and `data` with an
`evidence` reference. For useful continuation also record `automatic: true` only
after observing no Enter, nudge, manual resume or replacement session; for final
completion include `marker: "WAIT_TEST_DONE"`. These are measurement records,
not native request-coverage certificates. Missing or uncertain observations
remain inconclusive.

### Retain trial outcomes and interruptions

The observer finishes a finite duplicate window and then a separate telemetry
drain, publishing immutable `report.json`. Retain `manifest.json`,
`probe-events.jsonl`, `prototype.sqlite3`, prompts, raw native evidence, and the
original configuration locally. Publish only redacted summaries.

On Stop, Cancel, closure, or a broken bridge, record the terminal reason through
`suppress --directory <run> --reason stop|cancel|interrupted|closed|stale|bridge-failed`.
Interrupted trials remain in the series. The observer retains source readiness
without attempting a suppressed delivery. Repeated useful consumption is rejected.

## Validation record for the implementation

The 2026-09-16 bridge regression first failed with
`The Unix proxy requires binary WebSocket transport`; its original walk log is
retained at `a.shared-wait-service/inspection/bridge-regression-red-20260916.log`.
That walk also exposed the eager dependency import breaking the collector's
isolated startup. After the transport/import fixes, the affected run passed all
91 selected tests and reported 100% coverage. After the final lint correction,
the fresh `ghog day` passed the check gate, 14 affected tests and all 3,126 full
suite tests. `ghog status` confirmed `state=done exit=0` at
`2026-09-16T10:58:00+02:00`. The full phase took 3 minutes 36.8 seconds and
reported `fail=0 warn=0 xfail=0 cov=100 outliers=skipped excluded=skipped exit=0`.
The retained log is
`a.shared-wait-service/inspection/bridge-regression-green-20260916.log`.
`git diff --check` also passed. These results verify the bridge implementation.
The separately recorded human connection check demonstrates a basic automatic
idle TUI reply; neither result completes Step 2.

Tests use fake clocks and fake native transports; they make no model calls and
do not substitute for live measurements. Targeted Groundhog checks exercised
durability, native usage uncertainty, driver ordering, command startup from both
working directories, and observer lifecycle.

After the pending-return correction, `ghog day` completed on 2026-09-15 at
`23:05:24+02:00`, exit `0`. The check gate passed, the affected run passed 149
tests, and the full run passed 3,109 tests with no failures, warnings or expected
failures. Groundhog reported 100% coverage and `ghog status` confirmed
`state=done`. The full test phase took 2 minutes 42.4 seconds; the closing report
marked duration-outlier checks `skipped`. This paragraph retains that earlier
verification record; `a.ghog.log` now contains the latest walk.
The new regression first reproduced the missing A-arm interval, then passed
with timing restored and request coverage still incomplete. A first full walk
flagged its complexity; the simplified test retains every assertion and passed
the fresh walk above.

Final regressions verify bounded SQLite reservation work with 6,000 retained
trials and durable cancellation during a host-status callback. Native status
I/O runs outside the write transaction; eligibility is rechecked before the
send intent is committed.

The coverage source scope is `tools` with the configured exclusions in
`pyproject.toml`; the thin script under `docs` is outside that percentage. Its
startup and explicit registration paths were exercised by bounded subprocess
smoke tests from both the checkout and another working directory. All changed
Python files remain below the 650-line ceiling; the largest is the existing
collector at 548 lines.

The unresolved live gate follows the
[Step 2 procedure](plan.v0.13.0.shared-wait-service.md#step-2-run-the-minimal-native-wake-prototype-and-matched-trials).
If no functional route passes, take the documented human checkpoint before
freezing host interfaces or closing item 1. Independent core work keeps provisional
ports and requires the plan's Step 2 start gate.
