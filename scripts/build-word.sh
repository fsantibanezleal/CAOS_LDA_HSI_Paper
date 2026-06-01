#!/usr/bin/env bash
# Build the .docx versions of every manuscript from the LaTeX sources.
# Uses pandoc + citeproc; pandoc must be on PATH.
# Covers all five: conference (P2), journal (P1), journal_v_sweep (P3),
# journal_backbone_factorial (P4), journal_interpretability (P5).
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"

command -v pandoc >/dev/null 2>&1 || {
    echo "ERROR: pandoc not found; install via your package manager"
    exit 2
}

for variant in conference journal journal_v_sweep journal_backbone_factorial journal_interpretability; do
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
