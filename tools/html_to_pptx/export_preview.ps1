<#
.SYNOPSIS
    Export every slide of a .pptx to PNG through the installed PowerPoint, for
    a quick visual check against the source HTML.

.DESCRIPTION
    This is a verification aid only -- the PNGs are throwaway. The shipped deck
    stays 100% text and vector shapes; nothing here converts the deck into
    images. It drives PowerPoint via COM (SaveAs format 18 = ppSaveAsPNG), so
    PowerPoint must be installed. Open the resulting folder and compare each
    slide side by side with the browser rendering of the HTML.

.PARAMETER Pptx
    Path to the .pptx to export. Defaults to the llm-shared deck.

.PARAMETER OutDir
    Folder to receive Slide1.PNG, Slide2.PNG, ... It is recreated each run.

.EXAMPLE
    powershell -File tools\html_to_pptx\export_preview.ps1
#>
param(
    [string]$Pptx = "docs\llm-shared_presentation.pptx",
    [string]$OutDir = "$env:TEMP\pptx_preview"
)

$Pptx = (Resolve-Path $Pptx).Path
if (Test-Path $OutDir) { Remove-Item $OutDir -Recurse -Force }
New-Item -ItemType Directory -Path $OutDir | Out-Null

try {
    $pp = New-Object -ComObject PowerPoint.Application
} catch {
    Write-Output "PowerPoint is not available on this machine."
    exit 1
}

$pres = $pp.Presentations.Open($Pptx, $true, $false, $false)
$pres.SaveAs($OutDir, 18)   # 18 = ppSaveAsPNG, exports all slides
$pres.Close()
$pp.Quit()

Write-Output "Exported to $OutDir"
Get-ChildItem $OutDir -Recurse -Filter *.PNG |
    Select-Object -ExpandProperty Name
