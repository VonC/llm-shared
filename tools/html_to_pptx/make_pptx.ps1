<#
.SYNOPSIS
    One-line rebuild of docs\llm-shared_presentation.pptx from the HTML deck.

.DESCRIPTION
    Wraps everything the generation needs: installs python-pptx when it is
    missing, then runs build_llm_shared_pptx.py (which mirrors
    docs\llm-shared_presentation.html slide by slide).

    Branding: set LLM_SHARED_BRAND and LLM_SHARED_BRAND_SUB in the
    environment (or pass -Brand / -BrandSub) to replace the
    "Organization name" / "ORGANIZATION SUBTITLE" placeholders. Leave them
    unset to keep the placeholders.

.PARAMETER Brand
    Overrides LLM_SHARED_BRAND for this run.

.PARAMETER BrandSub
    Overrides LLM_SHARED_BRAND_SUB for this run.

.EXAMPLE
    powershell -File tools\html_to_pptx\make_pptx.ps1

.EXAMPLE
    powershell -File tools\html_to_pptx\make_pptx.ps1 -Brand "ACME" -BrandSub "IT DIVISION"
#>
param(
    [string]$Brand,
    [string]$BrandSub
)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($Brand) { $env:LLM_SHARED_BRAND = $Brand }
if ($BrandSub) { $env:LLM_SHARED_BRAND_SUB = $BrandSub }

python -c "import pptx" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Output "python-pptx not found: installing it (see README.md)."
    python -m pip install python-pptx
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

python (Join-Path $here "build_llm_shared_pptx.py")
exit $LASTEXITCODE
