#!/usr/bin/env bash
# Build the .docx versions of both manuscripts from the LaTeX sources.
# Uses pandoc + citeproc; pandoc must be on PATH.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"

command -v pandoc >/dev/null 2>&1 || {
    echo "ERROR: pandoc not found; install via your package manager"
    exit 2
}

for variant in conference journal; do
    out_dir="$repo/$variant/word"
    mkdir -p "$out_dir"
    (
        cd "$repo/$variant/tex"
        pandoc -s "main.tex" \
            --bibliography "../../bibliography/refs.bib" \
            --citeproc \
            -o "$out_dir/main.docx"
        echo "wrote $out_dir/main.docx"
    )
done
