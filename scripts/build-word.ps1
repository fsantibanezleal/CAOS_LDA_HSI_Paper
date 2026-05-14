# Build the .docx versions of both manuscripts from the LaTeX sources.
# Uses pandoc + citeproc; pandoc must be on PATH (winget JohnMacFarlane.Pandoc).
#
# Conference: conference/tex/main.tex -> conference/word/main.docx
# Journal   : journal/tex/main.tex    -> journal/word/main.docx

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$pandoc = (Get-Command pandoc -ErrorAction SilentlyContinue).Source
if (-not $pandoc) {
    $cand = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter "pandoc.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($cand) { $pandoc = $cand } else { throw "pandoc not found. Install with: winget install JohnMacFarlane.Pandoc" }
}

foreach ($variant in @("conference", "journal")) {
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
