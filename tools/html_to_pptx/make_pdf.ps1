<#
.SYNOPSIS
    One-line rebuild of docs\llm-shared_presentation.pdf from the HTML deck.

.DESCRIPTION
    Runs make_pptx.ps1 first (same LLM_SHARED_BRAND / LLM_SHARED_BRAND_SUB
    handling: env vars or -Brand / -BrandSub, placeholders kept when unset),
    then drives the installed PowerPoint through COM (SaveAs format 32 =
    ppSaveAsPDF) to export the freshly built pptx as
    docs\llm-shared_presentation.pdf. PowerPoint must be installed.

    The PDF route goes HTML -> build script -> pptx -> PowerPoint export, so
    the PDF pages match the editable deck one for one.

.PARAMETER Brand
    Overrides LLM_SHARED_BRAND for this run.

.PARAMETER BrandSub
    Overrides LLM_SHARED_BRAND_SUB for this run.

.EXAMPLE
    powershell -File tools\html_to_pptx\make_pdf.ps1

.EXAMPLE
    powershell -File tools\html_to_pptx\make_pdf.ps1 -Brand "ACME" -BrandSub "IT DIVISION"
#>
param(
    [string]$Brand,
    [string]$BrandSub
)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path

& (Join-Path $here "make_pptx.ps1") -Brand $Brand -BrandSub $BrandSub
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$pptx = Resolve-Path (Join-Path $here "..\..\docs\llm-shared_presentation.pptx")
$pdf = [System.IO.Path]::ChangeExtension($pptx.Path, ".pdf")

try {
    $pp = New-Object -ComObject PowerPoint.Application
} catch {
    Write-Output "PowerPoint is not available on this machine."
    exit 1
}

$pres = $pp.Presentations.Open($pptx.Path, $true, $false, $false)
$pres.SaveAs($pdf, 32)   # 32 = ppSaveAsPDF
$pres.Close()
$pp.Quit()

Write-Output "Saved $pdf"
