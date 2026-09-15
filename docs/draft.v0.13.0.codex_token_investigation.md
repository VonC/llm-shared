# Codex token/quota consumption investigation

## 1. Environment and objective

I am investigating unexpectedly high Codex CLI token/quota consumption on Windows, mainly with long-running development/test workflows.

Current relevant environment:

```text
OS: Windows 11 Enterprise
Codex CLI: 0.154.0 during most recent investigation
Model: gpt-6-astra
Typical reasoning effort: xhigh
Shell: CMD, with PowerShell used for telemetry analysis
Codex usage: CLI/TUI only
Main repositories observed:
- cplx
- eye-focus
- my-project_rct_pollution
- my-project
- llm-shared
```

Important current Codex settings include approximately:

```toml
approval_policy = "never"
sandbox_mode = "workspace-write"

model = "gpt-6-astra"
model_reasoning_effort = "xhigh"

model_auto_compact_token_limit = 120000

[features.code_mode]
default_exec_yield_time_ms = 120000
```

Selected repositories that need unrestricted unattended operation have their own:

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

The global `workspace-write` setting remains the safer default.

`remote_compaction_v2` is already stable/enabled in Codex and does not need an explicit config entry:

```cmd
codex features list | findstr /i remote_compaction_v2
```

It reported:

```text
remote_compaction_v2    stable    true
```

---

## 2. The two main token-consumption problems we found

There were two substantially different problems.

### A. Context growth/replay even without polling

One especially revealing September 9 `cplx` session had:

```text
Requests:           471
Input tokens:       88.48M
Average/request:   187.9K
Wait calls:           0
Compactions:           0
```

Its context grew approximately like this:

```text
09:00   ~104K/request
10:00   ~156K
11:00   ~186K
12:00   ~192K
...
17:00   ~220K
18:00   ~242K
```

So that session was expensive **without any polling at all**.

The conversation context simply kept accumulating, and almost every ordinary model turn replayed an increasingly large prefix.

This led to:

```toml
model_auto_compact_token_limit = 120000
```

That change was highly effective.

A later `cplx` session with almost exactly the same number of requests showed:

```text
Before:
471 requests
88.48M input
187.9K average/request
~242K eventual context
0 compactions

After:
467 requests
33.27M input
71.2K average/request
119.5K maximum
```

For nearly the same number of model interactions, input fell by roughly **62%**.

This is one of the strongest results of the investigation.

I would currently **keep the 120K auto-compaction threshold** rather than reducing it further.

---

### B. Model-driven polling repeatedly replays the context

The second major problem is `wait`.

A Codex `wait` is not merely a local sleep.

Conceptually, the expensive sequence is:

```text
model executes command
       ↓
command still running
       ↓
model turn ends / execution yields
       ↓
model is invoked again with existing conversation
       ↓
model asks wait(...)
       ↓
nothing changed
       ↓
model is invoked again with existing conversation
       ↓
wait(...)
       ↓
...
```

The expensive operation is not sleeping for 60 seconds.

It is **returning control to the model**, causing another model request carrying most of the conversation context.

Most of those input tokens are cached, typically around 94-99% in our traces, but they are still submitted/metered and correlate with quota consumption.

For example:

```text
290 wait requests
27.82M wait input
```

means approximately:

```text
27.82M / 290 ≈ 96K input tokens per wait
```

even though the new information might amount to only:

```text
still running
```

This explains why polling can become an enormous fraction of the day's activity.

---

## 3. Historical measurements

These measurements are useful baselines for future comparisons.

### September 8, before most fixes

Early/full-day figures:

```text
Requests:             2,746
Input:                394.66M
Cached input:         388.85M
Cached ratio:          ~98.5%
Uncached input:         5.81M
Output:                 0.69M

Wait calls:              778
Wait input:           126.13M
Wait share:              ~32%
```

Wait intervals:

```text
1 second      180
10 seconds    242
20 seconds      6
30 seconds     20
60 seconds    330
```

There were also:

```text
Guardian sessions:     12
Guardian requests:    294
Guardian input:     18.69M
```

Those Guardian sessions originated from:

```toml
approvals_reviewer = "auto_review"
```

With:

```toml
approval_policy = "never"
```

the automatic reviewer provided little value while consuming significant quota.

We removed `approvals_reviewer = "auto_review"`.

After that:

```text
Guardian sessions: 0
Guardian input:    0
```

This fix has remained effective.

---

## 4. September 9 baseline

Overall:

```text
Requests:          1,476
Input:            216.31M
Cached:           212.9M
Cached ratio:       98.4%
Uncached:            3.4M
Output:              0.41M

Wait calls:           340
Wait input:          43.3M
Wait share:           20.0%
```

The important discovery that day was the runaway non-wait `cplx` context:

```text
cplx
471 requests
88.48M input
187.9K average input/request
0 wait calls
0 compactions
context eventually ~240K
```

That is what motivated the explicit 120K auto-compaction threshold.

---

## 5. September 10 after auto-compaction

```text
Requests            : 1506
Input_M             : 118.67
AvgInput_K          : 78.8
Cached_pct          : 96.0
Uncached_M          : 4.71
Output_M            : 0.500

Wait_calls          : 291
Wait_requests       : 290
Wait_input_M        : 27.82
Wait_input_pct      : 23.4

NonWait_requests    : 1216
NonWait_input_M     : 90.85
NonWait_avg_K       : 74.7

Compactions         : 16
Compaction_errors   : 15

Guardian_sessions   : 0

Weekly_start_used   : 47
Weekly_end_used     : 58
Weekly_delta_points : 11
```

Wait distribution:

```text
1 sec         2
60 sec      217
120 sec       5
300 sec      49
900 sec      14
3600 sec      4
```

The important normalized improvement compared with September 9 was:

```text
Sep 9 average input/request:   ~146.6K
Sep 10 average input/request:    78.8K
```

The compaction limit clearly worked.

---

## 6. September 11: the polling pathology became dominant

September 11 was particularly revealing:

```text
Requests       : 1240
Input_M        : 94.59

Wait_calls     : 635
Wait_input_M   : 51.54
Wait_input_pct : 54.5%
```

Wait distribution:

```text
1 sec         5
60 sec      598
120 sec       4
300 sec      28
```

So:

```text
598 / 635 ≈ 94%
```

of all waits were exactly one minute.

More importantly:

```text
Total input:       94.59M
Wait input:        51.54M   54.5%
Non-wait input:    43.05M   45.5%
```

More than half of all input tokens for the day were associated with waiting.

Average wait cost:

```text
51.54M / 635 ≈ 81K input tokens/wait
```

### Where the waits came from

Per-project breakdown:

```text
Project                   Yield_ms   Count
------------------------------------------------
cplx                         60000     382
cplx                        120000       4
cplx                        300000      28

eye-focus                    60000     177

my-project                   1000       5

my-project_rct_pollution    60000      39
```

So `cplx` and `eye-focus` generated:

```text
382 + 177 = 559
```

of the 598 one-minute waits, about **93.5%**.

This proved that simply telling the model to prefer longer waits was not a sufficiently reliable solution.

---

## 7. September 12: clean baseline after quota reset

A weekly quota reset occurred before this work.

The UI went approximately:

```text
100% remaining
↓
91% remaining
```

after roughly eight hours, meaning around **9 weekly percentage points consumed**.

Telemetry:

```text
Requests            : 1112
Input_M             : 81.74
AvgInput_K          : 73.5
Cached_pct          : 96.2
Uncached_M          : 3.11
Output_M            : 0.406

Wait_calls          : 154
Wait_requests       : 154
Wait_input_M        : 11.78
Wait_input_pct      : 14.4

NonWait_requests    : 958
NonWait_input_M     : 69.96
NonWait_avg_K       : 73.0

Compactions         : 17
Compaction_errors   : 2

Guardian_sessions   : 0

Weekly_start_used   : 0
Weekly_end_used     : 9
Weekly_delta_points : 9
```

Wait distribution:

```text
1 sec        2
60 sec     147
300 sec      5
```

This day was substantially healthier.

Comparison:

| Metric            |  Sep 10 | Sep 11 | Sep 12 |
| ----------------- | ------: | -----: | -----: |
| Requests          |   1,506 |  1,240 |  1,112 |
| Input             | 118.67M | 94.59M | 81.74M |
| Avg input/request |   78.8K | ~76.3K |  73.5K |
| Wait calls        |     291 |    635 |    154 |
| Wait input        |  27.82M | 51.54M | 11.78M |
| Wait share        |   23.4% |  54.5% |  14.4% |
| Non-wait requests |   1,216 |    605 |    958 |
| Non-wait input    |  90.85M | 43.05M | 69.96M |
| Non-wait avg      |   74.7K | ~71.2K |  73.0K |
| Compactions       |      16 |     13 |     17 |
| Compaction errors |      15 |      2 |      2 |
| Guardian          |       0 |      0 |      0 |

An important observation is that September 12 involved **58% more non-wait requests than September 11**:

```text
605 → 958
```

yet wait-related input fell:

```text
51.54M → 11.78M
```

So September 12's improvement was not simply "I used Codex less."

---

## 8. Current interpretation of the problems

The investigation has identified four distinct sources of avoidable consumption:

* **Unbounded context accumulation.** Solved largely by `model_auto_compact_token_limit = 120000`.
* **Model-driven polling.** Still present. One model wake can carry ~70-100K input tokens even if nothing changed.
* **Automatic Guardian/review turns.** Removed by eliminating `approvals_reviewer = "auto_review"`.
* **Transport/compaction failures.** Significantly improved after fixing the certificate environment.

The dominant remaining architectural problem is polling.

---

## 9. Certificate / transport finding

Codex sessions originally started with:

```text
⚠ Falling back from WebSockets to HTTPS transport.
stream disconnected before completion:
invalid peer certificate: UnknownIssuer
```

The environment included:

```text
HTTP_PROXY=http://127.0.0.1:3128
HTTPS_PROXY=http://127.0.0.1:3128
```

with local Px forwarding to the corporate proxy.

There was also:

```text
SSL_CERT_FILE=<corporate CA-only PEM>
CODEX_CA_CERTIFICATE=<corporate CA PEM>
```

An OpenSSL probe through the exact proxy path showed that `chatgpt.com` was presenting a normal public Let's Encrypt chain, not a corporate TLS-intercepted certificate:

```cmd
openssl s_client -proxy 127.0.0.1:3128 -connect chatgpt.com:443 -servername chatgpt.com -showcerts <NUL 2>NUL | openssl x509 -noout -subject -issuer -dates
```

The issuer was public Let's Encrypt.

Our working hypothesis was that forcing `SSL_CERT_FILE` to the corporate-only bundle prevented Codex/Rust TLS from using the normal public trust store.

Launching Codex with these variables cleared dramatically improved stability:

```cmd
set "SSL_CERT_FILE="
set "CODEX_CA_CERTIFICATE="
codex
```

A DOSKEY-style wrapper used was conceptually:

```cmd
codex=cmd /d /c "set ""CODEX_CA_CERTIFICATE="" $T set ""SSL_CERT_FILE="" $T ""%USERPROFILE%\.codex\packages\standalone\current\bin\codex.exe"" $*"
```

After this change, `UnknownIssuer` dropped to zero in the later hourly telemetry.

Compaction errors also went roughly:

```text
Sep 10: 15 errors / 16 successes
Sep 12:  2 errors / 17 successes
```

The causal link is highly plausible but should still be described as observational rather than mathematically proven.

---

## 10. Current instruction changes

Global `AGENTS.md` now contains quota-hygiene instructions such as:

```text
- Avoid repeated short polling of long-running commands.
- Do not repeatedly re-enter the model merely to check a healthy process.
- Prefer 120000 ms or longer.
- For several-minute operations, prefer waits of several minutes.
- Do not use 1000 ms or 10000 ms polling unless there is a specific reason.
- For delegated agents, use long wait_agent waits and avoid status-only polling.
```

Groundhog documentation was also changed conceptually from:

```text
poll no closer than 60 seconds
```

toward:

```text
minimum around 120 seconds
prefer several minutes / roughly five minutes for a full walk
```

A crucial distinction was added:

```text
60-second progress silence floor != 60-second polling cadence
```

The former can be a legitimate logging policy. It should not be interpreted by the model as "wake every 60 seconds."

Even with those instructions, September 11 still generated 598 one-minute waits and September 12 generated 147.

This is why the current direction is to remove model polling architecturally rather than rely on prompt discipline.

---

## 11. Most useful telemetry commands

For reusable commands, first set the date:

```cmd
set AUDIT_DATE=2026-09-12
```

Replace that date when starting a new investigation.

### A. Full normalized daily audit

This is the most important command.

```cmd
powershell -NoProfile -Command "$tz=[TimeZoneInfo]::FindSystemTimeZoneById('Romance Standard Time');$day=[datetime]$env:AUDIT_DATE;$end=$day.AddDays(1);$req=0;$inp=0L;$cached=0L;$out=0L;$tot=0L;$wc=0;$wr=0;$wi=0L;$nwr=0;$nwi=0L;$sw=0;$wb=@{};$comp=0;$cerr=0;$gr=0;$gi=0L;$gs=New-Object 'System.Collections.Generic.HashSet[string]';$mods=New-Object 'System.Collections.Generic.HashSet[string]';$q1t=$null;$q2t=$null;$q1=$null;$q2=$null;foreach($f in Get-ChildItem \"$env:USERPROFILE\.codex\sessions\" -Recurse -Filter 'rollout-*.jsonl'|Where-Object{$_.LastWriteTime -ge $day}){try{$m=Get-Content -LiteralPath $f.FullName -TotalCount 1|ConvertFrom-Json}catch{continue};$root=[string]::IsNullOrEmpty([string]$m.payload.parent_thread_id);$guardian=($m.payload.source.subagent.other -eq 'guardian');$live=$root;$prev=-1L;$pending='';$model='unknown';$effort='unknown';foreach($line in Get-Content -LiteralPath $f.FullName){try{$j=$line|ConvertFrom-Json}catch{continue};if(!$j.timestamp){continue};try{$dto=[DateTimeOffset]::Parse($j.timestamp)}catch{continue};$lt=[TimeZoneInfo]::ConvertTime($dto,$tz).DateTime;$inside=($lt -ge $day -and $lt -lt $end);if(!$root -and $j.type -eq 'event_msg' -and $j.payload.type -eq 'task_started'){$live=$true;$prev=-1L;$pending=''};if($j.type -eq 'turn_context'){$model=[string]$j.payload.model;$effort=[string]$j.payload.effort;continue};if($live -and $j.type -eq 'response_item' -and $j.payload.type -eq 'function_call'){$pending=[string]$j.payload.name;if($inside -and $pending -eq 'wait'){$wc++;$a=$j.payload.arguments;if($a -is [string]){try{$a=$a|ConvertFrom-Json}catch{$a=$null}};$y=if($null -eq $a -or $null -eq $a.yield_time_ms){10000}else{[int64]$a.yield_time_ms};if($y -lt 120000){$sw++};$k=[string]$y;if(!$wb.ContainsKey($k)){$wb[$k]=0};$wb[$k]++};continue};if($inside -and $j.type -eq 'compacted'){$comp++};if($inside -and $j.type -eq 'event_msg' -and $j.payload.type -eq 'task_complete' -and $null -ne $j.payload.error -and [string]$j.payload.error.message -match 'remote compact'){$cerr++};if($j.type -eq 'event_msg' -and $j.payload.type -eq 'token_count'){$rl=$j.payload.rate_limits;if($inside -and $null -ne $rl -and $rl.limit_id -eq 'codex'){$v=$null;if($null -ne $rl.primary -and [int]$rl.primary.window_minutes -eq 10080){$v=$rl.primary}elseif($null -ne $rl.secondary -and [int]$rl.secondary.window_minutes -eq 10080){$v=$rl.secondary};if($null -ne $v -and $null -ne $v.used_percent){if($null -eq $q1t -or $dto -lt $q1t){$q1t=$dto;$q1=[double]$v.used_percent};if($null -eq $q2t -or $dto -gt $q2t){$q2t=$dto;$q2=[double]$v.used_percent}}};$info=$j.payload.info;if($live -and $null -ne $info -and $null -ne $info.total_token_usage){$cum=[int64]$info.total_token_usage.total_tokens;if($cum -gt $prev){$prev=$cum;if($inside -and $null -ne $info.last_token_usage){$u=$info.last_token_usage;$i=[int64]$u.input_tokens;$c=[int64]$u.cached_input_tokens;$o=[int64]$u.output_tokens;$t=[int64]$u.total_tokens;$req++;$inp+=$i;$cached+=$c;$out+=$o;$tot+=$t;[void]$mods.Add(($model+'/'+$effort));if($pending -eq 'wait'){$wr++;$wi+=$i}else{$nwr++;$nwi+=$i};if($guardian){$gr++;$gi+=$i;[void]$gs.Add($f.Name)}};$pending=''}}}}};[pscustomobject]@{Requests=$req;Input_M=[math]::Round($inp/1e6,2);AvgInput_K=if($req){[math]::Round(($inp/$req)/1000,1)}else{0};Cached_pct=if($inp){[math]::Round(100*$cached/$inp,1)}else{0};Uncached_M=[math]::Round(($inp-$cached)/1e6,2);Output_M=[math]::Round($out/1e6,3);Wait_calls=$wc;Wait_requests=$wr;Wait_input_M=[math]::Round($wi/1e6,2);Wait_input_pct=if($inp){[math]::Round(100*$wi/$inp,1)}else{0};NonWait_requests=$nwr;NonWait_input_M=[math]::Round($nwi/1e6,2);NonWait_avg_K=if($nwr){[math]::Round(($nwi/$nwr)/1000,1)}else{0};Waits_below_120s=$sw;Short_wait_pct=if($wc){[math]::Round(100*$sw/$wc,1)}else{0};Compactions=$comp;Compaction_errors=$cerr;Guardian_sessions=$gs.Count;Guardian_input_M=[math]::Round($gi/1e6,2);Weekly_start_used=$q1;Weekly_end_used=$q2;Weekly_delta_points=if($null -ne $q1 -and $null -ne $q2){$q2-$q1}else{$null};Models=(($mods|Sort-Object)-join ', ')}|Format-List;'WAIT INTERVALS';$wb.GetEnumerator()|Sort-Object{[int64]$_.Name}|ForEach-Object{[pscustomobject]@{Yield_ms=[int64]$_.Name;Count=$_.Value}}|Format-Table -AutoSize"
```

The fields I care about most are:

```text
Requests
Input_M
AvgInput_K

NonWait_requests
NonWait_input_M
NonWait_avg_K

Wait_calls
Wait_input_M
Wait_input_pct

Compactions
Compaction_errors

Guardian_sessions

Weekly_start_used
Weekly_end_used
Weekly_delta_points
```

`Input_M` alone is not enough because daily workload varies.

`NonWait_avg_K` is particularly useful for checking whether context/compaction behavior remains healthy.

---

### B. Top expensive sessions for the day

```cmd
powershell -NoProfile -Command "$tz=[TimeZoneInfo]::FindSystemTimeZoneById('Romance Standard Time');$day=[datetime]$env:AUDIT_DATE;$end=$day.AddDays(1);$rows=@();foreach($f in Get-ChildItem \"$env:USERPROFILE\.codex\sessions\" -Recurse -Filter 'rollout-*.jsonl'|Where-Object{$_.LastWriteTime -ge $day}){try{$m=Get-Content -LiteralPath $f.FullName -TotalCount 1|ConvertFrom-Json}catch{continue};$root=[string]::IsNullOrEmpty([string]$m.payload.parent_thread_id);if(!$root){continue};$prev=-1L;$pending='';$req=0;$inp=0L;$cached=0L;$wi=0L;$wc=0;$maxI=0L;$comp=0;$cerr=0;$first=$null;$last=$null;$model='unknown';$effort='unknown';foreach($line in Get-Content -LiteralPath $f.FullName){try{$j=$line|ConvertFrom-Json}catch{continue};if(!$j.timestamp){continue};try{$dto=[DateTimeOffset]::Parse($j.timestamp)}catch{continue};$lt=[TimeZoneInfo]::ConvertTime($dto,$tz).DateTime;$inside=($lt -ge $day -and $lt -lt $end);if($j.type -eq 'turn_context'){$model=[string]$j.payload.model;$effort=[string]$j.payload.effort;continue};if($j.type -eq 'response_item' -and $j.payload.type -eq 'function_call'){$pending=[string]$j.payload.name;if($inside -and $pending -eq 'wait'){$wc++};continue};if($inside -and $j.type -eq 'compacted'){$comp++};if($inside -and $j.type -eq 'event_msg' -and $j.payload.type -eq 'task_complete' -and $null -ne $j.payload.error -and [string]$j.payload.error.message -match 'remote compact'){$cerr++};if($j.type -eq 'event_msg' -and $j.payload.type -eq 'token_count' -and $null -ne $j.payload.info.total_token_usage){$cum=[int64]$j.payload.info.total_token_usage.total_tokens;if($cum -gt $prev){$prev=$cum;if($inside -and $null -ne $j.payload.info.last_token_usage){$u=$j.payload.info.last_token_usage;$i=[int64]$u.input_tokens;$c=[int64]$u.cached_input_tokens;$req++;$inp+=$i;$cached+=$c;if($i -gt $maxI){$maxI=$i};if($pending -eq 'wait'){$wi+=$i};if($null -eq $first){$first=$lt};$last=$lt};$pending=''}}};if($req -gt 0){$rows+=[pscustomobject]@{Project=Split-Path $m.payload.cwd -Leaf;Start=$first.ToString('HH:mm:ss');End=$last.ToString('HH:mm:ss');Model=($model+'/'+$effort);Requests=$req;Input_M=[math]::Round($inp/1e6,2);AvgInput_K=[math]::Round(($inp/$req)/1000,1);MaxInput_K=[math]::Round($maxI/1000,1);Cached_pct=[math]::Round(100*$cached/$inp,1);Waits=$wc;WaitInput_M=[math]::Round($wi/1e6,2);WaitInput_pct=[math]::Round(100*$wi/$inp,1);Compactions=$comp;CompactErrors=$cerr;Thread=$m.payload.id}}};$rows|Sort-Object Input_M -Descending|Format-Table -AutoSize|Out-String -Width 4096"
```

This is how the runaway `cplx` session was discovered.

Watch especially:

```text
AvgInput_K
MaxInput_K
WaitInput_pct
Compactions
CompactErrors
```

A healthy maximum with the current configuration should normally stay around the 120K compaction boundary instead of growing toward 200K+.

---

### C. Which projects are generating the waits?

```cmd
powershell -NoProfile -Command "$tz=[TimeZoneInfo]::FindSystemTimeZoneById('Romance Standard Time');$day=[datetime]$env:AUDIT_DATE;$end=$day.AddDays(1);$r=@();foreach($f in Get-ChildItem \"$env:USERPROFILE\.codex\sessions\" -Recurse -Filter 'rollout-*.jsonl'|Where-Object{$_.LastWriteTime -ge $day}){try{$m=Get-Content -LiteralPath $f.FullName -TotalCount 1|ConvertFrom-Json}catch{continue};if($m.payload.parent_thread_id){continue};foreach($line in Get-Content -LiteralPath $f.FullName){try{$j=$line|ConvertFrom-Json}catch{continue};if(!$j.timestamp -or $j.type -ne 'response_item' -or $j.payload.type -ne 'function_call' -or $j.payload.name -ne 'wait'){continue};try{$dto=[DateTimeOffset]::Parse($j.timestamp)}catch{continue};$lt=[TimeZoneInfo]::ConvertTime($dto,$tz).DateTime;if($lt -lt $day -or $lt -ge $end){continue};$a=$j.payload.arguments;if($a -is [string]){try{$a=$a|ConvertFrom-Json}catch{$a=$null}};$y=if($null -eq $a -or $null -eq $a.yield_time_ms){10000}else{[int64]$a.yield_time_ms};$r+=[pscustomobject]@{Project=Split-Path $m.payload.cwd -Leaf;YieldMs=$y}}};$r|Group-Object Project,YieldMs|ForEach-Object{[pscustomobject]@{Project=$_.Group[0].Project;Yield_ms=$_.Group[0].YieldMs;Count=$_.Count}}|Sort-Object Project,Yield_ms|Format-Table -AutoSize|Out-String -Width 4096"
```

This produced the revealing September 11 result:

```text
cplx                      60000   382
eye-focus                 60000   177
my-project_rct_pollution 60000    39
```

---

### D. Group waits by underlying cell/process

Useful when one long-running operation may be responsible for hundreds of wakes:

```cmd
powershell -NoProfile -Command "$tz=[TimeZoneInfo]::FindSystemTimeZoneById('Romance Standard Time');$day=[datetime]$env:AUDIT_DATE;$end=$day.AddDays(1);$r=@();foreach($f in Get-ChildItem \"$env:USERPROFILE\.codex\sessions\" -Recurse -Filter 'rollout-*.jsonl'|Where-Object{$_.LastWriteTime -ge $day}){try{$m=Get-Content -LiteralPath $f.FullName -TotalCount 1|ConvertFrom-Json}catch{continue};if($m.payload.parent_thread_id){continue};foreach($line in Get-Content -LiteralPath $f.FullName){try{$j=$line|ConvertFrom-Json}catch{continue};if(!$j.timestamp -or $j.type -ne 'response_item' -or $j.payload.type -ne 'function_call' -or $j.payload.name -ne 'wait'){continue};try{$dto=[DateTimeOffset]::Parse($j.timestamp)}catch{continue};$lt=[TimeZoneInfo]::ConvertTime($dto,$tz).DateTime;if($lt -lt $day -or $lt -ge $end){continue};$a=$j.payload.arguments;if($a -is [string]){try{$a=$a|ConvertFrom-Json}catch{$a=$null}};$y=if($null -eq $a -or $null -eq $a.yield_time_ms){10000}else{[int64]$a.yield_time_ms};$r+=[pscustomobject]@{Project=Split-Path $m.payload.cwd -Leaf;Thread=$m.payload.id;Cell=[string]$a.cell_id;YieldMs=$y;Time=$lt}}};$r|Group-Object Project,Thread,Cell,YieldMs|ForEach-Object{$g=$_.Group|Sort-Object Time;[pscustomobject]@{Project=$g[0].Project;Thread=$g[0].Thread;Cell=$g[0].Cell;Yield_ms=$g[0].YieldMs;Count=$g.Count;First=$g[0].Time.ToString('HH:mm:ss');Last=$g[-1].Time.ToString('HH:mm:ss')}}|Sort-Object Count -Descending|Select-Object -First 30|Format-Table -AutoSize|Out-String -Width 4096"
```

This is useful for distinguishing:

```text
600 unrelated waits
```

from:

```text
one long-running command polled 300 times
another command polled 200 times
...
```

The latter is precisely what a blocking/event-driven monitor can eliminate.

---

### E. Search instructions for lingering 60-second policies

Useful in `llm-shared` and consuming repositories:

```cmd
rg -n -i -g "*.md" -e "60000" -e "60 seconds" -e "60-second" -e "60 second" -e "one minute" .
```

Do **not** blindly replace every `60 seconds`.

Some occurrences represent legitimate **progress-output silence floors**, not model polling policies.

The distinction should remain explicit.

---

## 12. How to evaluate daily usage correctly

Raw daily token totals are heavily affected by workload.

For comparisons, prioritize:

```text
AvgInput_K
NonWait_avg_K
Wait_input_pct
Wait_calls
Compactions
Compaction_errors
Weekly_delta_points
```

For example:

```text
Sep 10:
118.67M total input
1,506 requests
78.8K/request

Sep 12:
81.74M total input
1,112 requests
73.5K/request
```

The lower total on September 12 partly reflects fewer requests.

But normalized context cost also improved.

Similarly, when comparing quota use, do not assume:

```text
1 token = fixed fraction of weekly quota
```

because cached/uncached input, output, reasoning, model configuration and server-side quota accounting may have different weights.

Use weekly percentage points as an empirical metric, not as a simple linear conversion from input tokens.

---

## 13. Why simply using longer waits helps but does not solve the problem

Suppose context is 80K and a job takes 15 minutes.

Polling every minute can cause roughly:

```text
15 × 80K ≈ 1.2M input tokens
```

Polling every five minutes might cause roughly:

```text
3 × 80K ≈ 240K
```

That is much better.

But it still performs model inference merely to discover:

```text
still running
```

The correct architectural solution is:

```text
model starts/registers work
       ↓
model finishes its turn
       ↓
ordinary code waits/monitors
       ↓
NO MODEL CALLS
       ↓
actionable event happens
       ↓
host wakes exact conversation once
       ↓
model continues useful work
```

The latest drafts explicitly define **no LLM polling**, rather than banning ordinary OS/database/file polling. A local service may use process handles, filesystem notifications, or bounded status reconciliation without generating model requests.

---

## 14. Proposed no-polling architecture

The current `llm-shared` proposal is named:

```text
Wake Me When It Matters
```

Its contract is:

```text
1. Agent identifies work.
2. Agent registers the exact wait.
3. Service durably records registration.
4. Host-specific wake route is armed.
5. Agent acknowledges registration.
6. Agent FINISHES THE TURN NORMALLY.
7. Model is completely idle.
8. Ordinary code monitors the source.
9. Source reaches an actionable state.
10. Monitoring service validates/persists the result.
11. Host adapter delivers one compact event.
12. Exact original conversation resumes.
13. Model validates the registered result and continues.
```

The service itself should:

```text
- not call an LLM;
- not hold conversation context;
- store durable wait/result/delivery state;
- coalesce identical source watches;
- prefer notifications/blocking IPC;
- keep polling/retries/heartbeats in ordinary code;
- never emit progress merely to prove it is alive.
```

The design explicitly separates:

```text
source adapters
```

which decide whether a condition is actually satisfied, from:

```text
host adapters
```

which wake the correct conversation.

---

## 15. Codex-specific wake approach

For Codex 0.154.0, research found a particularly interesting mechanism:

```text
codex queue
```

with an exact thread UUID.

Illustrative shape:

```text
codex queue --thread <thread-uuid> --message "Machine event: wait_id=w17 event_id=e17. Read the registered result and resume the authorized workflow."
```

The Codex TUI includes a host-side queue watcher that checks SQLite state approximately every ten seconds.

Critically:

```text
SQLite polling by Codex host != LLM polling
```

If no model request occurs, that ten-second check is cheap from a token perspective.

The proposed flow is:

```text
register exact wait
→ arm exact thread
→ end Codex turn
→ ordinary service monitors
→ event occurs
→ service invokes codex queue ONCE
→ idle owning TUI resumes
```

This still requires end-to-end verification on the actual Windows TUI. The current drafts explicitly treat it as a candidate until the live wake is demonstrated.

---

## 16. Why this is preferable to the earlier blocking-MCP idea

An earlier idea was:

```text
model calls await_job(...)
tool itself blocks for hours
model resumes when tool returns
```

That is already better than repeated model waits because the model does not wake during the blocking tool call.

But it leaves the original model turn pending.

The stronger architecture is:

```text
register
→ turn completes normally
→ model is idle
→ event wakes a new useful continuation
```

The current drafts intentionally prefer this stronger behavior while retaining a direct blocking tool as a possible fallback for unsupported hosts.

---

## 17. Controlled A/B benchmark planned for the solution

The latest draft defines three experimental arms:

```text
A: classic polling

B-prototype:
small local harness + native host wake primitive

B-service:
actual shared monitoring service + real durable registration
```

A prototype result must not later be relabelled as proof of the full service.

### Context seeding

Each trial should use a fresh conversation with equivalent substantial context.

Proposed seed:

```text
Read these two files completely and keep their contents in context for the next task:

- docs/v0.13.0/draft.v0.13.0.no_polling.md
- docs/v0.13.0/draft.v0.13.0.shared-wait-service.md

Do not analyze or summarize them yet. When finished, reply exactly:

READY
```

The files should be frozen at the same revision/hash for both arms.

Do not assume `READY` proves contexts are identical.

Record observed context/token size and use a predefined tolerance, e.g. ~5%. The draft now explicitly requires this.

---

## 18. Classic-polling benchmark prompt

Use a 240-second synthetic operation.

Conceptual benchmark prompt:

```text
This is a controlled benchmark of classic polling. Do only this work:

1. Start the prepared 240-second synthetic completion fixture as one foreground
   execution. It produces WAIT_TEST_DONE when complete.

2. Make the initial execution yield after 1000 ms if supported.

3. While that exact execution remains active, use the normal built-in wait
   mechanism with yield_time_ms=60000.

4. After each pending return, issue another 60000 ms wait until the same
   execution completes.

5. Do not use the shared monitoring service, queue, MCP monitoring,
   detached execution, another agent, status commands, progress narration,
   or unrelated work.

6. After successful completion, reply exactly:

WAIT_TEST_DONE

For this controlled benchmark only, the 60000 ms polling requirement overrides
the normal instruction to avoid frequent polling.
```

The latest draft deliberately says to **measure** how many waits occur rather than assuming exactly four.

---

## 19. No-polling benchmark prompt

Conceptually:

```text
This is a controlled benchmark of the shared no-polling wait mechanism.
Do only this work:

1. Register one prepared 240-second synthetic wait with the shared service.

2. Bind it to this exact conversation and establish the supported wake route.

3. Obtain acknowledgement that:
   - durable registration succeeded;
   - host arming succeeded.

4. Acknowledge registration briefly and finish this turn normally.

5. Do not call wait or status tools.
   Do not sleep in a pending foreground tool.
   Do not narrate progress.
   Do not launch another agent.
   Do not perform model-driven polling.

6. Leave monitoring and delivery entirely to ordinary service code.

7. When the event automatically resumes this conversation:
   - validate wait/event identity;
   - read the synthetic result;
   - consume the event once;
   - reply exactly:

WAIT_TEST_DONE
```

For the prototype stage, replace "shared service" with the temporary ordinary-code harness and label the result `B-prototype`.

---

## 20. What the A/B benchmark should measure

Primary metric:

```text
wait-induced model requests during unchanged interval
```

and:

```text
input tokens submitted by those requests
```

Also record:

```text
end-to-end input
cached input
uncached input
output
available reasoning usage

registration/setup cost
quiet-wait cost
useful-continuation cost

source duration
actual model-idle duration
delivery latency
logical wake count
event-consumption count

compactions
network retries
telemetry gaps
context mismatch
```

A successful B result should ideally show:

```text
quiet interval:

wait-induced requests:       0
repeated context submissions: 0
wait tool calls:             0
```

but:

```text
registration cost > 0
wake/continuation cost > 0
```

is completely legitimate.

`Wait_input_M = 0` by itself is **not** proof of success because the model could be polling through another tool or status command.

The latest draft captures that distinction explicitly.

---

## 21. A/B repetitions

The planned protocol is at least three fresh runs per arm, counterbalanced:

```text
A B
B A
A B
```

Keep:

```text
successful trials
failed wakes
invalid trials
inconclusive telemetry
```

Do not silently discard inconvenient results.

Report median and range, not just one apparently good run.

---

## 22. Important improvement over the early PowerShell benchmark command

The quick daily PowerShell commands above are useful operational diagnostics.

For the actual A/B proof, the draft now proposes building a dedicated collector.

That collector should use:

```text
exact thread identity
run manifest
pre-start cumulative baseline
exact start/end boundaries
request/tool IDs where available
```

rather than merely:

```text
cwd + timestamp + one $pending variable
```

It should account for:

```text
duplicate token reports
counter resets
compactions
network retries
rotated JSONL files
delayed writes
nested tool calls
failed requests
unknown/malformed evidence
```

and avoid counting pre-seed usage as benchmark usage.

This is more rigorous than the exploratory one-liners we used during diagnosis.

---

## 23. Current draft structure

The umbrella currently breaks the project into:

```text
1. Run one durable monitoring service
2. Report authoritative check completion
3. Deliver review availability and answers
4. Wake the owning Codex TUI
5. Wake Claude through Monitor
6. Wake the originating Copilot chat
7. End turns instead of polling
8. Prove quiet waits and document support
9. Add Gemini background completion
```

Importantly, the latest umbrella now explicitly requires the early matched Codex A/B test before substantial implementation and requires the final proof stage to reuse the same accounting methodology.

---

## 24. Current conclusion

The evidence so far suggests:

```text
Problem 1: runaway context
Status: largely solved by 120K auto-compaction

Problem 2: Guardian/auto-review
Status: solved; Guardian sessions remain zero

Problem 3: TLS/compaction instability
Status: substantially improved after clearing forced CA vars

Problem 4: model-driven polling
Status: still the major architectural inefficiency
```

The strongest historical evidence for the polling problem is:

```text
Sep 11:
94.59M total input
51.54M wait input
54.5% of all input associated with wait turns
635 wait calls
598 of them at exactly 60 seconds
```

The healthier September 12 baseline is:

```text
81.74M total input
11.78M wait input
14.4% wait share
154 waits
17 successful compactions
2 compaction errors
0 Guardian sessions
9 weekly quota points consumed
```

Even on that healthier day, 147 of 154 waits were still one-minute waits.

So the remaining opportunity is significant.

The desired end state is not:

```text
poll less often
```

but:

```text
do not invoke the model at all while nothing has changed
```

That is the purpose of the shared monitoring/event-driven wake architecture.
