# Serve a markdown folder as a local website (tools/serve_docs).
#
# PowerShell launcher: unlike a .bat wrapper, Ctrl-C stops the server
# cleanly without cmd's "Terminate batch job (Y/N)?" question. It
# self-locates the llm-shared folder and its bundled Python from its
# own path, so a full-path call works from any shell with no
# environment setup:
#
#   powershell -ExecutionPolicy Bypass -File "<llm-shared>\bin\mds.ps1" path\to\docs

$llmShared = Split-Path -Parent $PSScriptRoot
$pythonBase = Join-Path $llmShared "venvs"
$latest = Get-ChildItem -Path $pythonBase -Directory -Filter "python_3*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending | Select-Object -First 1
if ($null -eq $latest) {
    Write-Error "No python_3* directory found in $pythonBase"
    exit 1
}
$scripts = Join-Path $latest.FullName "Scripts"
$env:PATH = "$scripts;$env:PATH"
$python = Join-Path $scripts "python.exe"
$script = Join-Path $llmShared "tools\serve_docs\serve_docs.py"
& $python $script @args
exit $LASTEXITCODE
