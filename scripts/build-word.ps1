# Build the .docx versions of every manuscript from the LaTeX sources.
# Uses pandoc + citeproc; pandoc must be on PATH (winget JohnMacFarlane.Pandoc).
#
# Covers all five manuscripts (each <variant>/tex/main.tex -> <variant>/word/main.docx):
#   conference (P2), journal (P1),
#   journal_v_sweep (P3), journal_backbone_factorial (P4), journal_interpretability (P5)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$pandoc = (Get-Command pandoc -ErrorAction SilentlyContinue).Source
if (-not $pandoc) {
    $cand = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter "pandoc.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($cand) { $pandoc = $cand } else { throw "pandoc not found. Install with: winget install JohnMacFarlane.Pandoc" }
}

foreach ($variant in @("conference", "journal", "journal_v_sweep", "journal_backbone_factorial", "journal_interpretability")) {
    $tex = Join-Path $root "$variant\tex\main.tex"
    $outDir = Join-Path $root "$variant\word"
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    $out = Join-Path $outDir "main.docx"
    Push-Location (Join-Path $root "$variant\tex")
    try {
        & $pandoc -s "main.tex" --bibliography "..\..\bibliography\refs.bib" --citeproc -o $out
        Write-Host "wrote $out"
    } finally {
        Pop-Location
    }
}
