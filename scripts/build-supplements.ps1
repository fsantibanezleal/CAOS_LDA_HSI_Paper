# Build every supplementary PDF and DOCX (Windows PowerShell).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$pandoc = (Get-Command pandoc -ErrorAction SilentlyContinue).Source
if (-not $pandoc) {
    $cand = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter "pandoc.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($cand) { $pandoc = $cand } else { throw "pandoc not found." }
}

foreach ($variant in @("conference", "journal")) {
    $srcDir = Join-Path $root "supplementary\$variant"
    $docxDir = Join-Path $root "supplementary\word\$variant"
    New-Item -ItemType Directory -Path $docxDir -Force | Out-Null
    Get-ChildItem -Path $srcDir -Filter "*.tex" | ForEach-Object {
        $base = $_.BaseName
        Push-Location $srcDir
        try {
            & pdflatex -interaction=nonstopmode "$base.tex" *> $null
            try { & bibtex "$base" *> $null } catch {}
            & pdflatex -interaction=nonstopmode "$base.tex" *> $null
            & pdflatex -interaction=nonstopmode "$base.tex" *> $null
        } finally {
            Pop-Location
        }
        $pdfSrc = Join-Path $srcDir "$base.pdf"
        $pdfDst = Join-Path $root "supplementary\build\${variant}_${base}.pdf"
        if (Test-Path $pdfSrc) { Move-Item -Force $pdfSrc $pdfDst }
        # DOCX via pandoc
        Push-Location $srcDir
        try {
            & $pandoc -s "$base.tex" --bibliography "$root\bibliography\refs.bib" --citeproc -o (Join-Path $docxDir "$base.docx")
        } finally {
            Pop-Location
        }
        Write-Host "built $variant / $base"
        # Clean transients
        Get-ChildItem -Path $srcDir -Include *.aux,*.bbl,*.blg,*.log,*.out,*.fls,*.fdb_latexmk -File -ErrorAction SilentlyContinue | Remove-Item -Force
    }
}
Write-Host "all supplements built"
