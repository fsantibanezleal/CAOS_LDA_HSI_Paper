#!/usr/bin/env bash
# Build every supplementary PDF and DOCX.
#
# Requires: pdflatex + bibtex (TeX Live or MiKTeX) and pandoc.

set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"

for variant in conference journal; do
    src_dir="$repo/supplementary/$variant"
    docx_dir="$repo/supplementary/word/$variant"
    mkdir -p "$docx_dir"
    for tex in "$src_dir"/*.tex; do
        base="$(basename "$tex" .tex)"
        (
            cd "$src_dir"
            pdflatex -interaction=nonstopmode "$base.tex" > /dev/null
            bibtex "$base" > /dev/null || true
            pdflatex -interaction=nonstopmode "$base.tex" > /dev/null
            pdflatex -interaction=nonstopmode "$base.tex" > /dev/null
        )
        mv "$src_dir/$base.pdf" "$repo/supplementary/build/${variant}_${base}.pdf" 2>/dev/null \
          || mv "$src_dir/$base.pdf" "$repo/supplementary/build/$base.pdf"
        # Pandoc DOCX
        (
            cd "$src_dir"
            pandoc -s "$base.tex" \
                --bibliography "$repo/bibliography/refs.bib" \
                --citeproc \
                -o "$docx_dir/$base.docx"
        )
        echo "built $variant / $base"
        # Clean tex transients
        rm -f "$src_dir"/*.aux "$src_dir"/*.bbl "$src_dir"/*.blg \
              "$src_dir"/*.log "$src_dir"/*.out "$src_dir"/*.fls \
              "$src_dir"/*.fdb_latexmk
    done
done
echo "all supplements built"
