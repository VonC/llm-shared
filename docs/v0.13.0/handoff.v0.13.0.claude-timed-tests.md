# Claude timed-test handoff for 2026-09-17

Resume Step 2 of the shared wait service effort in
`%USERPROFILE%\git\llm-shared_no_polling`.
The user confirms that all seven Claude sessions will remain open across the
overnight Windows suspension and resume tomorrow. Preserve those sessions.
The next task is to finish the Claude benchmark integration, then run the
controlled baseline and three matched pairs in those existing conversations.

## State at handoff

A read-only check at **2026-09-16 20:45:11 Paris time**
(`18:45:11.7707257Z`) found all seven exact Claude session processes alive.
Each native transcript still ended with `READY`, contained one human prompt,
zero Monitor calls, and zero assistant records after that final response.
**No Claude matched-series timed test has started.** Nothing was started while
preparing this handoff. The unfinished integration will not progress overnight.

- The controlled Codex baseline and all six trials are complete and audited.
  All three B trials woke automatically; retain B2's observer-recovery deviation.
- Claude's separate, unseeded Monitor smoke `claude-smoke-20260916-04` passed:
  600.008 seconds quiet, useful continuation after 5.257 seconds, one consumption,
  and complete duplicate/drain observation. All 24 independent checks passed.
  That smoke's session was closed and is separate from these seven sessions.
- The seven-session seed audit passed: identical seed prompts, complete reads
  of all 17 frozen chunks, native normal `READY` completions, and matching exposed
  Claude `2.1.273`, `claude-opus-5`, effort `xhigh`, permission mode `auto`.
  Pair context differences were 3.8912%, 0.9678%, and 0.5834%, within 5%.
- Step 2 remains incomplete. Functional wake success does not establish strict
  zero inference, complete request accounting, quota savings, or billing savings.

## Existing sessions and evidence

The existing launcher run is:

```text
a.shared-wait-service/claude-tabs-20260916-180128-11adaf42/
```

Use its `launcher.json` for exact bindings and its
`seed-audit-20260916-181001/` directory for original seed snapshots and audit
evidence. Native transcripts are the exact UUID-named JSONL files under:

```text
%USERPROFILE%\.claude\projects\C--Users-vonc-git-llm-shared-no-polling\
```

| Execution order / tab title | Existing session UUID |
| --- | --- |
| `claude-baseline` | `bb916b36-b9ff-4f2b-aef8-93a894811cc6` |
| `claude-pair-01-a` | `7a7346da-4e8c-4d99-91ee-1c76fbd51478` |
| `claude-pair-01-b` | `73ea435e-a5b4-4375-a14b-57c8ee3d9a2f` |
| `claude-pair-02-b` | `fa51e1c2-13e7-4634-a748-bea78b2a519e` |
| `claude-pair-02-a` | `52f4b8f8-c81a-40c2-b062-adca57d442b9` |
| `claude-pair-03-a` | `eb9b9f2e-d5ab-4e7f-8311-18e483c9776a` |
| `claude-pair-03-b` | `52d8bc32-e3af-4db8-b7b1-a8a22bdaff87` |

Seed commit: `3d4b5a4643d1fba65434877d965d2c051b65e1a3`.
The frozen drafts, chunk hashes, context counts and exact native identities are
recorded in [the selected seed audit](probe-claude-seeds.v0.13.0.shared-wait-service.json).
Preserve that seed revision and existing working-tree changes, including
untracked prototype files and ignored local evidence.

## Work to resume tomorrow

1. Read `AGENTS.md` and `rules/run_commands.md`, then the
   [Step 2 implementation and live procedure](plan.v0.13.0.shared-wait-service.md#step-2-run-the-minimal-native-wake-prototype-and-matched-trials),
   [validation plan's missing work](plan.v0.13.0.shared-wait-service.validation.md#missing-work-for-step-2),
   [probe results](probe-results.v0.13.0.shared-wait-service.md), and
   [Claude launcher notes](claude-tabs.v0.13.0.shared-wait-service.md).

2. Recheck the exact existing processes and native transcripts after Windows
   resumes. The read-only helper is
   `a.shared-wait-service/check-claude-benchmark-status.ps1`.
   Verify that no extra user turns, measured work, interruption, compaction or
   relevant configuration changes occurred. Revalidate seed/context gates from
   native evidence. Do not rerun the seven-tab launcher, resend the seed, or send
   conversational status prompts to the measured sessions. An overnight pause
   before measurement does not by itself require replacing a seeded session.
   Preserve and report any actual invalidation before replacing an affected one.

3. Finish and test the Claude integration before preparing a timed run:
   - `tools/wait_evidence/telemetry.py` currently accepts Claude `2.1.272`, not
     the actual sessions' `2.1.273`. Add inspected-version normalization and
     regression fixtures; changing only the accepted version is insufficient.
   - Normalize exact tool calls, tool results, usage, interruptions and native
     normal turn completion for the common collector/observer. Handle the
     `pair-03-a` normal-end parent chain through a `deferred_tools_record`
     attachment, plus identified sessionless bookkeeping and `away_summary`.
     Preserve identity rejection and unknown request-attempt coverage.
   - Integrate the proven Monitor handshake, normal-end gate, event emission and
     consumption with `tools/wait_evidence/probe_driver.py`,
     `probe_observer.py`, and the shared collector. The common observer currently
     installs a native route only for Codex B trials.
   - Reuse the evidence and working behavior in
     `claude-probe.shared-wait-service.py` and
     `claude-probe-state.shared-wait-service.py` beside this handoff.
     Keep launcher diagnostics off Monitor event stdout, use explicit executable
     paths, and retain startup validation before acknowledging observer readiness.
   - Verify the actual Monitor schema in the measured sessions through the
     prepared protocol. The smoke exposed no `persistent` parameter; its declared
     timeout maximum was 3,600,000 ms with a documented runtime cap of 1,800,000 ms.
     Do not assume a monitor armed before suspension can cover tomorrow's trials.
   - Preserve the seed variation: six sessions also read `rules/chat.md`, while
     `pair-03-b` did not. Provider and compaction configuration remain unestablished.

4. Prepare exact per-session manifests, transcript offsets, commands and prompt
   files only after the gates pass. Verify the observer is ready before prompt
   submission. Capture fresh measurement boundaries tomorrow; the overnight
   interval since `READY` is not the ten-minute baseline or a measured trial.
   The Claude launcher only delivered the initial seed prompt: automatic delivery
   of the timed prompts into existing Claude TUIs has not been demonstrated.
   Prepare everything first, then give the user the exact tab and prompt when
   manual submission is needed. Do not claim the tests started merely because
   prompts or launch records exist.

5. Run the measurements sequentially in the table's order: baseline, A1, B1,
   B2, A2, A3, B3. Keep the computer awake during the measurement series.
   Retain the fixed bounds: at least 600 seconds of unchanged source after normal
   end for the baseline; 240-second trial source interval; 60-second bound to
   first useful continuation; 120-second post-completion duplicate window and a
   separate 120-second telemetry drain. A uses the documented foreground-wait
   benchmark protocol; B ends normally and wakes through Monitor without a
   human nudge. A's short waits are the benchmark-only exception, not a pattern
   for the implementing session. Keep timers and collection in independent
   ordinary processes, with durable status and completion records. Avoid model
   polling and duplicate drivers. `WAIT_TEST_DONE` alone does not end observation.

6. Retain every failure, interruption and qualification. Audit single consumption,
   useful continuation latency, duplicates, observed usage, and accounting limits.
   Run the required focused checks and full Groundhog walk following
   `instructions/groundhog.md`; prior green results do not validate new integration
   changes. Update the probe results, redacted Claude evidence and validation plan.
   Close Step 2 only when its code and live-evidence gates are satisfied, with
   unsupported accounting claims explicitly recorded. Later service work is
   outside this handoff.

The user's next action is to resume Windows with the same seven tabs intact and
tell the implementing conversation to continue from this handoff. No additional
prompt needs to be pasted into a Claude tab until its timed instruction is ready.
