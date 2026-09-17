<#
.SYNOPSIS
Open named Codex tabs, inspect their UUIDs, or send an instruction file by name.
.DESCRIPTION
Arguments travel as JSON in this process environment, never interpolated shell
code. The project environment owns Python selection. Open creates fresh TUIs
and sends their seeds; measured benchmarks require a separate Send action.
#>
[CmdletBinding()]
param(
    [ValidateSet('Open', 'Bind', 'Status', 'Send')]
    [string]$Action = 'Open',
    [string]$Directory,
    [string]$Name,
    [string]$InstructionFile,
    [ValidateSet('seed', 'benchmark', 'diagnostic')]
    [string]$Kind = 'benchmark',
    [string]$SeedFile,
    [string[]]$Names,
    [string]$CodexHome,
    [string]$CodexExecutable,
    [string]$Terminal
)
$ErrorActionPreference = 'Stop'
$repository = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$launcherArgs = @($Action.ToLowerInvariant())
$options = [ordered]@{
    '--directory' = $Directory
    '--name' = $Name
    '--file' = $InstructionFile
    '--kind' = $Kind
    '--seed-file' = $SeedFile
    '--codex-home' = $CodexHome
    '--codex-executable' = $CodexExecutable
    '--terminal' = $Terminal
}
foreach ($key in $options.Keys) {
    if ($options[$key]) { $launcherArgs += @($key, $options[$key]) }
}
if ($Names) {
    $expandedNames = @($Names | ForEach-Object { $_ -split ',' })
    $launcherArgs += @('--names') + $expandedNames
}
$previousArguments = $env:LLM_WAIT_TABS_ARGUMENTS
try {
    $env:LLM_WAIT_TABS_ARGUMENTS = ConvertTo-Json -InputObject $launcherArgs -Compress
    Push-Location -LiteralPath $repository
    try {
        & cmd.exe /d /v:on /c 'set NO_MORE_SENV_%PRJ_DIR_NAME%=& senv.bat && python docs/v0.13.0/codex-tabs.shared-wait-service.py'
        if ($LASTEXITCODE -ne 0) { throw "Codex tab launcher failed with exit $LASTEXITCODE. Existing run records were retained." }
    }
    finally { Pop-Location }
}
finally { $env:LLM_WAIT_TABS_ARGUMENTS = $previousArguments }

# eof
