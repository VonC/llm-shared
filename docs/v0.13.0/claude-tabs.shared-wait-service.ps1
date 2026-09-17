<#
.SYNOPSIS
Open seven fresh interactive Claude sessions in one new Windows Terminal window.
.DESCRIPTION
Freezes the Step 2 drafts and supplies the same initial seed prompt to every
session. Records exact UUIDs before opening tabs. Timed trials start separately.
Use -PrepareOnly to write and inspect the launch records without opening tabs.
#>
[CmdletBinding()]
param(
    [ValidateSet('Open', 'Tab')]
    [string]$Action = 'Open',
    [string]$Directory,
    [string]$Name,
    [string]$SeedCommit = '3d4b5a4643d1fba65434877d965d2c051b65e1a3',
    [string]$ClaudeExecutable,
    [string]$Terminal,
    [switch]$PrepareOnly
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repository = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$utf8 = New-Object System.Text.UTF8Encoding($false)
$names = @('baseline', 'pair-01-a', 'pair-01-b', 'pair-02-b', 'pair-02-a', 'pair-03-a', 'pair-03-b')

function Write-Json([string]$Path, $Value) {
    [IO.File]::WriteAllText($Path, (ConvertTo-Json -InputObject $Value -Depth 12) + "`n", $utf8)
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Resolve-Executable([string]$Requested, [string]$Default) {
    if (-not $Requested) { $Requested = $Default }
    $command = Get-Command -Name $Requested -CommandType Application -ErrorAction Stop | Select-Object -First 1
    return $command.Source
}

function Get-ClaudeVersion([string]$Executable) {
    $output = & $Executable --version
    if ($LASTEXITCODE -ne 0) { throw "Claude --version failed: $LASTEXITCODE" }
    return ($output -join "`n").Trim()
}

if ($Action -eq 'Tab') {
    if (-not $Directory -or $Name -notin $names -or $PrepareOnly) {
        throw 'Tab requires the original -Directory and one recorded -Name.'
    }
    $Directory = (Resolve-Path -LiteralPath $Directory).Path
    $config = Get-Content -LiteralPath (Join-Path $Directory 'launcher.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($config.repository -ne $repository) { throw 'Launcher checkout differs from the recorded checkout.' }
    $matches = @($config.tabs | Where-Object { $_.name -eq $Name })
    if ($matches.Count -ne 1) { throw "Missing or ambiguous tab: $Name" }
    $tab = $matches[0]
    $null = [guid]::Parse($tab.session_id)
    foreach ($item in @($config.seeds) + @($config.chunks) + @($config.prompt)) {
        if ((Get-Sha256 $item.path) -ne $item.sha256) { throw "Seed changed: $($item.path)" }
    }
    if ((Get-ClaudeVersion $config.claude_executable) -ne $config.claude_version) {
        throw 'Claude version changed after preparation. Retain this preparation and start a new series.'
    }
    $prompt = [IO.File]::ReadAllText($config.prompt.path, $utf8)
    $claudeArgs = @('--session-id', $tab.session_id, '--name', $tab.session_name, $prompt)
    $recordPath = Join-Path $Directory "$Name.started.json"
    # A failed or uncertain launch also reserves the UUID. Never retry it silently.
    $claim = [IO.File]::Open($recordPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $claim.Dispose()
    Write-Json $recordPath ([ordered]@{
        name = $Name
        session_id = $tab.session_id
        wrapper_pid = $PID
        started_utc = [DateTime]::UtcNow.ToString('o')
        prompt_sha256 = $config.prompt.sha256
        meaning = 'Launch intent; native transcript must establish prompt delivery and READY.'
    })
    Push-Location -LiteralPath $repository
    try {
        Write-Host "Claude tab: $Name | Session: $($tab.session_id)"
        Write-Host 'The seed prompt is supplied automatically. Leave this tab open after READY.'
        & $config.claude_executable @claudeArgs
        $claudeExit = $LASTEXITCODE
        Write-Json (Join-Path $Directory "$Name.exited.json") ([ordered]@{
            session_id = $tab.session_id
            exited_utc = [DateTime]::UtcNow.ToString('o')
            exit_code = $claudeExit
        })
        if ($claudeExit -ne 0) { throw "Claude exited with code $claudeExit. Records were retained." }
    }
    finally { Pop-Location }
    return
}

if ($Name) { throw '-Name is reserved for the internal Tab action.' }
$ClaudeExecutable = Resolve-Executable $ClaudeExecutable 'claude.exe'
$Terminal = Resolve-Executable $Terminal (Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\wt.exe')
$powershell = Resolve-Executable $null (Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe')
$git = Resolve-Executable $null 'git.exe'
$version = Get-ClaudeVersion $ClaudeExecutable
$revision = & $git -C $repository rev-parse --verify "$SeedCommit^{commit}"
if ($LASTEXITCODE -ne 0 -or $revision -notmatch '^[0-9a-f]{40}$') { throw 'Cannot resolve the seed commit.' }
$runId = [guid]::NewGuid().ToString('N')
if (-not $Directory) {
    $Directory = Join-Path $repository ('a.shared-wait-service\claude-tabs-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss') + '-' + $runId.Substring(0, 8))
}
$Directory = [IO.Path]::GetFullPath($Directory)
# Windows Terminal uses semicolons as command separators, even across arguments.
foreach ($path in @($Directory, $repository, $PSCommandPath, $powershell)) {
    if ($path.Contains(';')) { throw 'Windows Terminal launch paths must not contain semicolons.' }
}
if (Test-Path -LiteralPath $Directory) {
    throw "Run directory already exists. Retain it and use a fresh directory: $Directory"
}
$null = New-Item -ItemType Directory -Path $Directory
$seedSources = @(
    'docs/v0.13.0/draft.v0.13.0.no_polling.md',
    'docs/v0.13.0/draft.v0.13.0.shared-wait-service.md'
)
$archive = Join-Path $Directory 'seeds.zip'
& $git -C $repository archive --format=zip "--output=$archive" $revision -- @seedSources
if ($LASTEXITCODE -ne 0) { throw 'Cannot freeze both seed drafts. Partial preparation was retained.' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$seedDirectory = Join-Path $Directory 'seeds'
[IO.Compression.ZipFile]::ExtractToDirectory($archive, $seedDirectory)
$chunkDirectory = Join-Path $Directory 'chunks'
$null = New-Item -ItemType Directory -Path $chunkDirectory
$seeds = @()
$chunks = @()
foreach ($source in $seedSources) {
    $frozen = Join-Path $seedDirectory $source
    $expectedBlob = & $git -C $repository rev-parse "${revision}:$source"
    if ($LASTEXITCODE -ne 0) { throw "Cannot resolve source blob: $source" }
    $actualBlob = & $git -C $repository hash-object --no-filters -- $frozen
    if ($LASTEXITCODE -ne 0 -or $actualBlob -ne $expectedBlob) { throw "Frozen bytes differ from Git: $source" }
    $bytes = [IO.File]::ReadAllBytes($frozen)
    $seeds += [ordered]@{ source = $source; path = $frozen; sha256 = Get-Sha256 $frozen; bytes = $bytes.Length; git_blob = $expectedBlob }
    $offset = 0
    $part = 0
    while ($offset -lt $bytes.Length) {
        $end = [Math]::Min($offset + 9000, $bytes.Length)
        if ($end -lt $bytes.Length) {
            while ($end -gt $offset -and $bytes[$end - 1] -ne 10) { $end-- }
            if ($end -eq $offset) { throw "Seed line exceeds 9000 bytes: $source" }
        }
        $part++
        $path = Join-Path $chunkDirectory (([IO.Path]::GetFileNameWithoutExtension($source)) + ('-{0:D2}.txt' -f $part))
        $chunk = New-Object byte[] ($end - $offset)
        [Array]::Copy($bytes, $offset, $chunk, 0, $chunk.Length)
        [IO.File]::WriteAllBytes($path, $chunk)
        $chunks += [ordered]@{ source = $source; part = $part; path = $path; bytes = $chunk.Length; sha256 = Get-Sha256 $path }
        $offset = $end
    }
}
$orderedPaths = ($chunks | ForEach-Object { '- ' + $_.path }) -join "`n"
$prompt = @"
Read both frozen drafts completely and keep their contents in context for the
next task. The ordered chunk files below concatenate to the exact full drafts.

Read rules/run_commands.md once first. Then use the Read tool to read each chunk
once, in the listed order, with its complete contents. No shell command or
repository inventory is needed for these reads. Do not additionally read the
original drafts. If a read fails or is truncated, stop and report SEED_READ_FAILED.

Do not analyze or summarize the drafts, implement their instructions, start a
benchmark, or spawn an agent. After all chunks have been read completely, reply
exactly READY and wait for the next user instruction.

$orderedPaths
"@ + "`n"
$promptPath = Join-Path $Directory 'seed-prompt.txt'
[IO.File]::WriteAllText($promptPath, $prompt, $utf8)
$tabs = @($names | ForEach-Object {
    [ordered]@{ name = $_; session_id = [guid]::NewGuid().ToString(); session_name = "sw-claude-$($runId.Substring(0, 8))-$_" }
})
$config = [ordered]@{
    schema = 1
    created_utc = [DateTime]::UtcNow.ToString('o')
    repository = $repository
    directory = $Directory
    seed_commit = $revision
    claude_executable = $ClaudeExecutable
    claude_version = $version
    settings = 'Inherited unchanged; verify actual native configuration before measurements.'
    seeds = $seeds
    chunks = $chunks
    prompt = [ordered]@{ path = $promptPath; sha256 = Get-Sha256 $promptPath }
    tabs = $tabs
    automatic_benchmarks = $false
    context_gate = 'Verify full native reads, READY, matching settings and retained context within 5%, then write trial manifests.'
}
Write-Json (Join-Path $Directory 'launcher.json') $config
$terminalArgs = @('-w', 'new')
foreach ($tab in $tabs) {
    if ($terminalArgs.Count -gt 2) { $terminalArgs += ';' }
    $terminalArgs += @(
        'new-tab', '--title', "claude-$($tab.name)", '--suppressApplicationTitle', '-d', $repository,
        $powershell, '-NoProfile', '-NoExit', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath,
        '-Action', 'Tab', '-Directory', $Directory, '-Name', $tab.name
    )
}
Write-Json (Join-Path $Directory 'terminal-command.json') ([ordered]@{ executable = $Terminal; arguments = $terminalArgs })
Write-Host "Run records: $Directory"
Write-Host "Initial prompt: $promptPath"
if ($PrepareOnly) {
    Write-Host 'Prepared only; no terminal or Claude session was started. A live launch uses a fresh directory.'
    return
}
Write-Json (Join-Path $Directory 'terminal-started.json') ([ordered]@{ attempted_utc = [DateTime]::UtcNow.ToString('o') })
& $Terminal @terminalArgs
$terminalExit = $LASTEXITCODE
Write-Json (Join-Path $Directory 'terminal-result.json') ([ordered]@{ exit_code = $terminalExit; returned_utc = [DateTime]::UtcNow.ToString('o') })
if ($terminalExit -ne 0) { throw "Windows Terminal exited with code $terminalExit. Inspect the retained records before a fresh launch." }
Write-Host 'Seven Claude tabs requested. The prompt is supplied automatically; leave each tab open after READY.'
Write-Host 'Terminal acceptance is not proof of seed completion. No timed benchmark has started.'

# eof
