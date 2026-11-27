# Test resume_paused in an independent tuitp desktop

## Invocation model

A human operator runs the live cases from a Windows terminal inside the disposable guest and records what appeared in each pane. An agent or a human can run the offline companion and list cases from the candidate checkout.

Run the automated companion from a Windows candidate checkout. It exercises the resume unit and acceptance tests with fake TUIOS and temporary files. The second command lists the live cases and their step counts. Both commands work outside the lab.

```powershell
.\tests\acceptance\resume_paused\lab.bat verify
.\tests\acceptance\resume_paused\lab.bat cases
```

## Prepare the guest once

1. Create a disposable Windows VM with computer name `RP-LAB` and a fresh, local user profile. Use a hypervisor that can checkpoint a running guest **including memory**. For the hibernation case, check that `powercfg /a` in the guest offers hibernation. Choose a guest with S4 support for that case.
2. Install Windows Terminal, Git, the global senv installation with `%USERPROFILE%\senv.bat`, its Windows `tuitp.bat` launcher, TUIOS, and the current Codex and Claude CLIs inside the VM. Use guest-specific sign-ins and local storage. The candidate checkout, including any uncommitted changes under test, must be on a guest disk. Open a human Windows Terminal outside TUIOS and initialize the checkout with its own `senv.bat`. Check that `where.exe tuitp.bat` and `where.exe tuios` resolve to this guest installation. Leave the default TUIOS namespace and agent configuration directories in use.
3. Install the candidate's adapters into the fresh guest profile. From the candidate root in PowerShell run the following commands. The junction target is the checkout under test. Check for any existing skills directory before creating the Claude junction.

   ```powershell
   .\bin\codex_skills_link.bat --create
   New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude" | Out-Null
   New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target (Resolve-Path .claude\skills).Path
   ```

4. In the same human terminal, from the candidate root, run the commands below. An alternate `tuitp --list` reconciles the user's **entire** launcher ledger and TUIOS namespace. The VM provides the independent desktop. The runner requires an empty guest namespace and ledger before opening the lab. It sets `TUITP_RESUME=0` during launch and restore so that startup cannot consume a fixture.

   ```powershell
   $lab = (Resolve-Path .\tests\acceptance\resume_paused\lab.bat).Path
   & $lab open
   ```

5. In the `Acceptance` tab, finish sign-in and trust prompts. In `rp-primary`, check that Codex and Claude both open in `alpha`. `rp-peer` has a second Codex in `alpha`, and `rp-secondary` has Claude in `bravo`. Each session also has a CMD pane. Confirm that the native pause, resume and review-resume skills resolve to the candidate and that the receiver can run the candidate's validators. Leave all four agents idle with empty editors. Take a running VM checkpoint called **ready** before saving any pauses.

## Run one story

Restore **ready** before each case. The restored human terminal retains `$lab`. Start with `bulk`.

```powershell
& $lab seed bulk
& $lab next
& $lab next
& $lab next
& $lab status
& $lab verdict
```

For the other cases, substitute the case name, make the indicated operator gesture, and run `next` once per step. Wait for a step to finish before advancing. `status` shows the next step, a locked attempt, or the final pass. For a single-agent delivery, also look for the saved objective's reply (`RP-ACK-alpha` or `RP-ACK-bravo`) in its intended pane. A receipt proves consumption. The reply checks that the host actually continued the task. Keep unrelated panes idle.

| Case | What to do and what to check |
| --- | --- |
| `bulk` | Preview both saved pauses, deliver both, then repeat. Check both replies. The repeated launch must skip both checkouts. `bravo` uses its own artifact-home declaration. |
| `clear` | Leave a short completed conversation visible in each target before the first step. Preview with clear enabled, deliver, then repeat. Observe the fresh conversation on each host and check both receipts. |
| `already-cleared` | After seeding, manually submit `/clear` in Claude secondary. Leave the new conversation idle. Run the step and check that Claude reports `already cleared`, receives just the resume and gives its reply. The case requires a public clear event in this guest's TUIOS integration. Codex should receive both commands. |
| `manual` | After seeding, invoke the native unmarked resume in Claude primary for the Codex pause saved in `alpha`. Decline the author override and wait for the question to close. Run the step and check that the report identifies the manual Claude attempt, Codex peer receives no input and the prompt is still unused. |
| `names` | Advance through an unmatched exclusion, an unmatched switch and a switch on a single-agent pause. Each launch must refuse or diagnose its named checkout with zero dispatches. |
| `exclude` | Exclude `bravo` on the first launch. The second launch must consume only its still-unused pause. |
| `routes` | Run against a legacy pause in `alpha` and an absent target UUID in `bravo`. Expect distinct routing and target diagnostics. |
| `history` | Run with an unsupported pausing agent in `alpha` and a later journal-only resume by Codex for the unused Claude pause in `bravo`. Expect both skips, the journal evidence in the report, and zero new dispatches. |
| `damaged` | Run with the malformed `alpha` receipt. Expect a failing exit alongside a successful `bravo` receipt. |
| `concurrent` | Run one step to release two real launchers concurrently. Check one successful delivery per checkout across their two reports, then run the repeat check. |
| `draft` | After seeding, type `RP-UNSENT-472` into Codex peer and leave it unsubmitted. Run the step and verify that the draft remains visible and editable. |
| `busy` | After seeding, give Codex peer a harmless long-running foreground task, such as waiting for two minutes. Run the step while it is working. Expect a busy skip. |
| `blocked` | After seeding, ask Codex peer to present a user-input choice. Leave its interactive menu open while running the step. Expect a blocked skip and the same question still open. |
| `capture-pair` | **Before seeding**, run `& $lab prepare-pair`. In Codex primary, use the native pause skill to save a requestor handoff. Identify Claude primary as reviewer, `docs/plan.v0.11.0.review-exchange-core.md` as the plan, `docs/draft.v0.11.0.review-mode.md` as the umbrella, step 3, occurrence 1 and round 1. Once paused, run `& $lab seed capture-pair` and `& $lab next`. Check that the saved assignment resumes Codex first and starts exactly one Claude reviewer. |
| `pair` | Resume the prepared code review. Watch Codex primary resume as requestor, then Claude primary enter as reviewer. Check the two reported generations and one reviewer. |
| `later` | Launch with the reviewer excluded, then launch again. Only the missing reviewer should receive the second delivery. |
| `switch` | Resume Claude primary as requestor with Codex primary excluded. Run the ordinary continuation and observe the switch-required skip. Repeat with the switch and check the sole Codex reviewer. |
| `hibernate` | After seeding, open a second human terminal inside the guest, change to the candidate and run `.\tests\acceptance\resume_paused\lab.bat waiter`. Once it is waiting, run step 1 in the first terminal. Hibernate and wake **Windows inside the VM**. Run step 2 with the same waiter alive. Press Ctrl+C in the second terminal, then run step 3. Expect pending, pending, then one reviewer. The runner verifies the waiter's process identity, unchanged boot and Windows S4 event. |
| `reboot` | Run step 1, restart Windows fully, sign in and return to the candidate in a human terminal. Recreate `$lab` with the command above, run `& $lab restore`, wait for the agents to become ready, then run step 2. The runner requires a new boot, a full-start event and the original pane UUIDs. Check for one reviewer and no second requestor resume. |
| `stall` | The first step drops one confirmed ask after reserving the real target. Expect an unconfirmed failure. The next step uses the shipping wrapper and must suppress a second send. |
| `recovery` | The runner pastes the marked instruction into the real Codex peer without submitting it. Observe one targeted recovery Enter and a matching receipt. |
| `capture` | **Before seeding**, ask Codex peer and Claude secondary to use their native pause skill for an implementation session, each with a next task to reply with its checkout's `RP-ACK` string and stop. Wait for both pauses to finish. Seed adopts and validates both routes. Preview, deliver, and check both replies. |
| `copied` | Preview. Copy only the native command and its complete marker from `step-1/launch-1.stdout` into Codex peer and submit it. Wait for the marked failure. Advance, then submit the *new* preview command from step 2 into Codex primary. Wait for its marked failure and advance again. Both attempts must leave the checkout untouched. With a shared Codex app-server, also record which pane the validator identified and its mismatch diagnostic. |
| `caller` | Run twice from the human terminal. The harness supplies a Codex caller environment to the first child and a Claude caller environment to the preview child. Both shipping-wrapper invocations must refuse before input. The companion tests cover recognized process ancestry. |

## Read and retain the result

Once the command checks pass, cases with a visible outcome ask for an operator observation. Run `& $lab verdict`, select `pass` or `fail`, and record the reply, reviewer count, or pane state you saw. The runner saves this once in `observation.json`. Until then, `status` reports the outstanding observation. A recorded failure remains visible and returns a failing exit code. Cases whose outcome is fully checked by the runner report their verdict immediately.

The human terminal prints the evidence path under `%LOCALAPPDATA%\resume-paused-acceptance`. Each attempted step has a private directory with stdout, stderr, exit code when available, and artifact hashes before and immediately after launch. A passed step also records its final observations and `passed.json`. The checks bind receipts and claims to the saved prompt digest, full pane identity, role and exchange. Each accepted resume must add one journal entry for its checkout and host.

A failed or interrupted launch stays locked. Inspect its output and the affected pane, record the first failing step, and retain a guest checkpoint before reverting to **ready**. Record the candidate revision, installed host versions, case name, observed replies or reviewer roles, and verdict outside the reverted snapshot. Keep transcripts, private artifact contents, ownership material and sign-ins inside the guest. Dispose of the guest when verification is complete.

The ordinary live scenarios run the shipping batch launcher. The two fault cases substitute the outbound transport for one step while using the normal planner, observers, reservations, real pane and receiver. They make the lost-send and recovery branches repeatable. A naturally occurring daemon stall or OS-level delivery failure needs its own observation. The project validation record maps the live cases and automated checks to each requirement. [Validation record](../../docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md#independent-tuitp-acceptance)
