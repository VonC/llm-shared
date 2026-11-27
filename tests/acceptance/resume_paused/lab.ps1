# Run in the candidate checkout from a human PowerShell terminal.
$ErrorActionPreference = 'Stop'
$repo = (Get-Item -LiteralPath "$PSScriptRoot\..\..\..").FullName
$venv = Get-ChildItem -Directory -LiteralPath "$repo\venvs" -Filter 'python_3*llm-shared*' |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $venv) { throw "Activate the candidate checkout's senv.bat once to build its Python environment." }
Push-Location -LiteralPath $repo
try {
    if ($args.Count -eq 1 -and $args[0] -eq 'verify') {
        $env:PRJ_DIR = $repo
        $env:LLM_SHARED_DIR = $repo
        Remove-Item Env:GHOG_SENV_READY -ErrorAction SilentlyContinue
        $files = @(Get-ChildItem -LiteralPath "$PSScriptRoot\test_resume_paused_acceptance" -Filter 'test_*.py')
        $files += @(Get-ChildItem -Path "$repo\tests\unit\tools\test_resume_paused_*\test_*.py")
        $paths = @($files | ForEach-Object { Resolve-Path -LiteralPath $_.FullName -Relative })
        & "$repo\bin\ghog.bat" single --whole-suite @paths
    } else {
        & "$($venv.FullName)\Scripts\python.exe" -E -m tests.acceptance.resume_paused.live_lab @args
    }
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $code
