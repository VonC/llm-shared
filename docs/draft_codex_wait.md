# Codex Wait Token Analysis

## general context

> You mention lower tokens for today, but does that include the fact my use of Codex sessions was lower? (I simply had fewer tasks to perform with Codex today.)

Yes, the raw **118M vs 216M daily total is confounded by workload**, so by itself it would not prove an improvement.

But the normalized telemetry does show a real efficiency gain, and interestingly you actually had **slightly more model requests today**, despite doing fewer tasks:

* September 9: 1,476 model requests, 216.31M input tokens, about **146.6K input/request**.
* September 10: 1,500 model requests, 118.08M input tokens, **78.7K input/request**.

So the average context replay per model request fell by roughly **46%**. That improvement cannot be explained by simply having fewer Codex tasks.

It looks even better if we remove `wait` turns:

* September 9: 1,137 non-wait requests consumed about 173.0M input tokens, roughly **152K per useful/non-wait request**.
* September 10: 1,210 non-wait requests consumed about 90.3M, roughly **75K per non-wait request**.

That is approximately a **51% reduction in context carried by ordinary model turns**.

This lines up very well with the 120K auto-compaction change: yesterday long sessions could reach ~200-243K context, whereas today your heaviest sessions top out around **119K**. So I am confident that **early compaction has materially reduced token consumption per model interaction**.

What has *not* improved enough is waiting:

```text
Sep 9:  wait input = 43.3M / 216.3M = 20.0%
Sep 10: wait input = 27.8M / 118.1M = 23.6%
```

Absolute wait-token consumption fell, but waits are actually a **larger fraction** of today's total. That is why eliminating those remaining 60-second Groundhog polls is now worth doing.

So I would describe the result as:

> **Total daily usage was lower partly because my workload differed, but normalized usage improved substantially: average context per model request fell from ~147K to ~79K, and non-wait requests fell from ~152K to ~75K. Early 120K compaction appears to be working; polling is now the main remaining avoidable overhead.**

For tomorrow's comparison, I would focus much less on `Input_M` and much more on **Input/request, non-wait input/request, wait-input %, compaction count, and weekly quota points consumed**.

## Issue with Wait Token Consumption

> Why wait input tokens are so larges? What in waiting make a Codex consume tokens? Is it about the all context being re-read on each wait?

Yes. That is essentially the mechanism.

A Codex `wait` is not a cheap local sleep. In the current code-mode design, when a long-running command yields, the harness gives the model a cell ID. To learn whether that process has finished, the model later emits another `wait(...)`. **That `wait` is a new model turn**, so Codex sends the conversation context back to the model again. ([GitHub][1])

That is why a wait can cost, say, 80K or 120K input tokens even though the useful new information may be only:

```text
still running
```

or:

```text
process completed
```

The expensive part is not the act of sleeping for 60 seconds. It is the **model waking up after that interval and reprocessing the existing context so it can decide to issue another `wait`**.

In simplified form:

```text
Model turn
  context = 100K tokens
  -> exec(...)

command still running

Model turn
  context ~= 100K tokens
  -> wait(60000)

still running

Model turn
  context ~= 100K tokens
  -> wait(60000)

still running

Model turn
  context ~= 100K tokens
  -> wait(60000)

...
```

Three essentially empty status checks can therefore process another ~300K input tokens. Most of that may be cached, but cached input is still metered and can consume quota. This is exactly what the Codex reports measure: #35259 found repeated wait/status-only turns re-ingesting large cached prefixes, with 96.8% of that wait/status input cached. ([GitHub][2])

### Why your 27.82M wait input makes sense

You had:

```text
290 wait calls
27.82M wait input tokens
```

That gives an average of roughly:

```text
27.82M / 290 ~= 96K input tokens per wait
```

That is completely consistent with your sessions now operating mostly below the 120K compaction threshold.

So, very roughly, each status check costs you:

```text
~96K input tokens
```

even though the response may only be a few dozen tokens.

This is also why your auto-compaction change helped twice:

* ordinary turns now carry a smaller context;
* **wait turns also carry a smaller context**.

Before compaction tuning, a wait in a 200K context could cost about twice as much as one in a 100K context.

### Longer waits help because they reduce the number of model wakeups

Suppose a background operation takes 15 minutes and the surrounding context is 100K.

At 60-second polling:

```text
~15 model wakeups x 100K ~= 1.5M input tokens
```

At 5-minute polling:

```text
~3 wakeups x 100K ~= 300K input tokens
```

At a 15-minute wait:

```text
~1 wakeup x 100K ~= 100K input tokens
```

The elapsed wall-clock time is basically the same. What changes is how many times Astra has to re-enter the conversation.

That is why #38495 describes the problem as a **"full-context model polling loop"**. Its representative trace measured roughly 240K input tokens for individual no-op wait turns. ([GitHub][1])

### The ideal implementation would not involve the model at all

Architecturally, the efficient behavior would be:

```text
model starts process
        ↓
harness waits locally
        ↓
process emits output / exits
        ↓
harness wakes model
```

No inference while nothing changes.

Instead, today's generic `wait` mechanism is effectively:

```text
model starts process
        ↓
timer expires
        ↓
wake model + resend context
        ↓
model asks "done yet?"
        ↓
no
        ↓
timer expires
        ↓
wake model + resend context
        ...
```

That is the fundamental inefficiency. The open issues explicitly propose making waiting event-driven so a timeout with no state change does **not** cause another model turn. ([GitHub][3])

### One nuance: the whole context is not necessarily recomputed from scratch

Because you are seeing cache rates around 94-99%, the server is heavily benefiting from prompt caching. So "re-read" is a good conceptual description, but not literally "re-run every transformer computation from token 1 with no cache."

More precisely:

> The full conversation prefix is **submitted/re-metered as input for the new turn**, and most of that prefix can be served from prompt cache.

That distinction matters technically, but from your quota perspective the key fact remains: **cached input still counts**, so a no-op wait with a 100K cached prefix is not free. #37299 observed ~137-141K input tokens per polling turn with 97-98% cache hit rates, while still seeing severe quota depletion. ([GitHub][4])

So yes: your intuition is right. **The large `Wait_input_M` is primarily the cost of repeatedly carrying the existing conversation into fresh model turns merely to ask whether background work has finished.**

[1]: https://github.com/openai/codex/issues/38495?utm_source=chatgpt.com "Code-mode `exec` silently degrades a long-running command into a full-context model polling loop (34.6M tokens burned after the task already completed) · Issue #38495 · openai/codex · GitHub"
[2]: https://github.com/openai/codex/issues/35259?timeline_page=1&utm_source=chatgpt.com "Codex Desktop repeatedly re-enters the model during wait/status polling, consuming substantial credits · Issue #35259 · openai/codex · GitHub"
[3]: https://github.com/openai/codex/issues/41875?utm_source=chatgpt.com "Align wait_agent default timeout with prompt-cache TTL (30 min on GPT-5.6+) to cut parent-agent polling cost · Issue #41875 · openai/codex · GitHub"
[4]: https://github.com/openai/codex/issues/37299?utm_source=chatgpt.com "Desktop wait/status orchestration re-meters full cached context every 10-30s; stale 'running' subagents keep it looping (90% of weekly Pro in 15.5h) · Issue #37299 · openai/codex · GitHub"

## Possible Wait Mechanism

> So how would you build a wait mechanism driven by script, waking up the model (and what kind of written instruction can convince a model to not wait, but to stop until being wake up?)

Yes, but with one important limitation: **a normal script cannot asynchronously wake Codex by itself**. In the current CLI, the model resumes when a tool call returns. So the cleanest design is to make the waiting logic a **single blocking direct tool call**, rather than letting code mode yield and making the model poll with `wait`.

That gives you the behavior you want:

```text
Astra starts job
      |
      v
detached process runs
      |
      v
Astra calls await_job(...) ONCE
      |
      v
local waiter blocks/polls locally     <-- no model inference, no token burn
      |
      v
job finishes / sentinel changes
      |
      v
await_job returns
      |
      v
Astra is sampled again exactly once
```

This is materially different from today's built-in `wait`, where each timeout returns control to the model and causes another full-context turn. ([GitHub][1])

## I would implement it as a tiny local MCP server

That is better than just writing `wait-job.py` and launching it through code-mode `exec`, because **the `exec` itself may yield**, putting you straight back into the polling loop.

Codex has a configuration specifically useful here:

```toml
[features.code_mode]
direct_only_tool_namespaces = ["mcp__local_waiter"]
```

A namespace listed there is exposed as a direct model tool and omitted from the code-mode nested tool path. ([GitHub][2])

There is already a live-verified Codex issue demonstrating exactly this workaround: a blocking MCP call routed through `direct_only_tool_namespaces` remained pending for almost five minutes with **zero `wait` calls and zero intermediate model resampling**, and the model resumed once the tool returned. ([GitHub][3])

For example, your global config could eventually contain:

```toml
[features.code_mode]
default_exec_yield_time_ms = 120000
direct_only_tool_namespaces = ["mcp__local_waiter"]

[mcp_servers.local_waiter]
command = "C:\\Users\\example\\venvs\\codex-waiter\\Scripts\\python.exe"
args = ["-m", "codex_waiter"]

# Allow one blocking wait to remain pending for up to six hours.
tool_timeout_sec = 21600
```

The normal MCP tool timeout is finite, so for multi-hour jobs it needs to be explicitly raised. Current Codex supports `mcp_servers.<id>.tool_timeout_sec`; the current implementation otherwise has a much shorter default. ([GitHub][4])

The exact `mcp__local_waiter` naming is current Codex behavior, but that prefix is under-documented/internal enough that I would verify the generated namespace once from the Codex logs rather than regard it as an eternal contract. ([GitHub][5])

## For `ghog`, make the waiter understand `ghog`

I would not expose a generic `sleep(900)` tool. Give it semantics.

Conceptually, its implementation would be:

```python
def await_ghog(repo: Path, timeout_seconds: int = 21600) -> Result:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        result = subprocess.run(
            [
                "cmd", "/d", "/c",
                r"..\llm-shared\bin\ghog.bat status",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
        )

        if result.returncode != 6:
            return Result(
                exit_code=result.returncode,
                output=result.stdout,
            )

        # This polling costs CPU milliseconds, not LLM tokens.
        time.sleep(10)

    return Result(timed_out=True)
```

It could poll `ghog status` every 5 or 10 seconds internally if you wanted. **That is cheap**, because no model is involved.

The distinction becomes:

```text
Bad:
Astra -> wait -> Astra -> wait -> Astra -> wait
          100K       100K       100K input

Good:
Astra -> await_ghog
              |
              +-- status
              +-- sleep
              +-- status
              +-- sleep
              +-- status -> done
              |
          return to Astra

          one model continuation
```

And since your `ghog status` already has a meaningful exit protocol (`6=running`, `7=killed`, anything else final), it is particularly well suited to this design.

I would have the MCP tool return only a compact result, for example:

```json
{
  "state": "done",
  "exit_code": 0,
  "elapsed_seconds": 1837,
  "log_tail": [
    "...",
    "ghog day: PASS ..."
  ]
}
```

Not the complete accumulated log.

## The instruction I would give Astra

The wording should not merely say "wait less often". It should explicitly establish the blocking tool as the **only permitted waiting mechanism for supported jobs**.

I would add something like this to the relevant shared Groundhog instruction:

```markdown
## Blocking waits

For a detached Groundhog walk, do not monitor completion with the Codex
built-in `wait`, `sleep`, repeated `ghog status`, process inspection, or any
other model-driven polling loop.

After launching the walk, call `local_waiter.await_ghog` exactly once with
the repository path and a timeout long enough for the walk.

`local_waiter.await_ghog` is a blocking tool: while it is pending, no model
action or progress check is required. It monitors the job locally and returns
when the walk finishes, is killed, or reaches its timeout.

Once the blocking tool returns, resume from the status and bounded log tail
it reports.

Do not replace this blocking wait with shorter Codex `wait` calls merely to
provide progress updates.
```

The crucial sentence is:

> **while it is pending, no model action or progress check is required**

But the instruction alone is not what saves the tokens. The real guarantee comes from making `await_ghog` a **direct blocking tool**.

Once Astra has emitted that tool call, it literally does not get another turn in which it can decide "I'll check again". The tool remains pending in Codex until your local waiter returns.

## Could you do it without MCP?

There is a simpler but weaker approach: add:

```cmd
ghog await
```

to your existing batch wrapper, where `ghog await` internally loops on `ghog status` until completion.

Then tell Astra:

```text
After ghog day --detach, run ghog await once.
Never poll ghog status yourself.
```

The problem is that if Astra invokes `ghog await` through code-mode `exec`, Codex's `Execute` operation still has a yield deadline. When that deadline expires, the cell becomes pending and the model again needs the built-in `wait`. The current protocol explicitly models `Execute` as returning when the execution **yields or completes**; a later `Wait` is still pull-based. ([GitHub][6])

You can make the yield huge, but that is still a heuristic.

So I would rank the approaches:

1. **Direct blocking local MCP waiter**: genuine zero-token waiting until completion.
2. Long blocking shell wrapper + very large `yield_time_ms`: simpler, but not guaranteed.
3. Current `wait(300000/900000/...)`: better than one-minute polling, but every expiry still costs a full model turn.

For your setup, I think **#1 is worth building**. You now have enough measured evidence that 20-25% of a day's input can be status-only waiting; replacing those hundreds of model wakeups with a single direct blocking `await_ghog` call could remove most of that class of waste.

[5]: https://github.com/openai/codex/issues/29122?utm_source=chatgpt.com "[URGENT] Stable IDE extension ships a prerelease CLI with under-development \"Code mode\" silently active, breaking any long-running MCP calls and burning tokens while waiting · Issue #29122 · openai/codex · GitHub"
[6]: https://github.com/openai/codex/blob/main/codex-rs/code-mode-protocol/src/grpc/codex.code_mode.v1.proto?utm_source=chatgpt.com "codex/codex-rs/code-mode-protocol/src/grpc/codex.code_mode.v1.proto at main · openai/codex · GitHub"

## Example of Codex wait session that might consume tokens

```txt
• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Round 1 is published and awaiting reviewer pickup. The configured wait is three hours, and the exchange is healthy. The review transcript (docs/v10.0.0/
  review.issue.v10.0.0.stuck_en_cours_log.md) now contains the request.

• Waiting for further input

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• No reviewer answer has arrived yet. The published round remains pending, and the same wait is still running.

• Considering user invocation timing

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The request is available for an independently started reviewer session. This session will process the answer when it arrives; the review skill keeps the requestor and reviewer roles
  separate.

• Assessing execution and token limits

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The exchange is still waiting for round 1’s answer. There is no feedback to apply yet.

• Avoiding excessive execution time

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Round 1 remains pending after about six minutes. The wait has reported no errors.

• Clarifying notification vs commentary

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The reviewer has not published an answer yet. I’m keeping the existing request and wait active.

• Waiting for process completion

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The review is still pending. Once feedback arrives, I can handle requested revisions automatically; consolidation will remain at the human decision gate.

• Avoiding long blocking waits

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Round 1 is still awaiting an answer, with no errors reported by the exchange.

• Managing sustained execution loop

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The request has been pending for ten minutes. The configured wait remains active, so I’m continuing to wait for the reviewer’s response.

• Clarifying instruction needs

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• No answer has arrived. The issue and published round 1 request remain ready for review.

• Noticing pending status delay

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The exchange still reports request-pending. That status does not tell me whether a reviewer is currently reading it; it only confirms that no answer has been published.

• Adding frequent comments

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The wait is healthy and still pending. There is no new reviewer feedback to report.

• Considering update timing constraints

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Round 1 is still open after roughly fifteen minutes. The review request is published; completion now depends on the independent reviewer’s answer.

• Clarifying session persistence

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• The answer is still pending. I’m preserving the active round and its evidence while the configured wait continues.

• Noting time spent and need for interruption

• Waited for background terminal · & C:\Users\example\git\llm-shared\bin\review_exchange.bat wait-answer --family specification --document docs/v10.0.0/
issue.v10.0.0.stuck_en_cours_log.md --convergence-signal consolidation-ready --another-round-label 'Revise and review again' --continue-owning-workflow-label Consolidate --ownership-
generation 1 --ownership-token <ownership-token>

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• No reviewer answer or protocol error has appeared. Round 1 remains pending.

• Working (21m 31s • esc to interrupt) · 1 background terminal running · /ps to view · /stop to close
...
```
