# Supplementary material

Twelve chapter-aligned supplementary documents, one per main-paper
section, providing the technical, mathematical, theoretical, and
extended-results material that did not fit in the
page-budget-constrained manuscripts.

## Conference paper (5 supplements, A through E)

Companion to `conference/tex/main.tex` (WHISPERS 2026 target,
4-5 pages):

| Suppl | Companion to | Title | PDF |
|---|---|---|---|
| A | §I  Introduction | Extended motivation for the band-mask diagnostic | `build/conference_suppl_A_introduction.pdf` |
| B | §II Method | Full mathematical derivations | `build/conference_suppl_B_method_derivations.pdf` |
| C | §III Experimental setup | Dataset descriptors + tokenisation | `build/conference_suppl_C_datasets.pdf` |
| D | §IV Results | Extended results (full per-tuple tables, Hungarian permutations, HIDSAG) | `build/conference_suppl_D_extended_results.pdf` |
| E | §V Discussion | Extended discussion + four explicit non-claims | `build/conference_suppl_E_discussion.pdf` |

## Journal paper (7 supplements, A through G)

Companion to `journal/tex/main.tex` (IEEE TGRS target, ~20-25 pages):

| Suppl | Companion to | Title | PDF |
|---|---|---|---|
| A | §I  Introduction | The accuracy-only view and why it fails | `build/journal_suppl_A_introduction.pdf` |
| B | §II Related Work | Full related-work taxonomy | `build/journal_suppl_B_related_work.pdf` |
| C | §III Twelve-axis framework | Per-axis motivation + alternatives considered | `build/journal_suppl_C_axis_motivation.pdf` |
| D | §IV Method | Full mathematical derivations (B-1..B-12) | `build/journal_suppl_D_mathematical_derivations.pdf` |
| E | §V Experimental setup | Full dataset descriptors incl. HIDSAG depth | `build/journal_suppl_E_datasets.pdf` |
| F | §VI Results | Extended per-axis results across 6 scenes + 5 HIDSAG subsets | `build/journal_suppl_F_extended_results.pdf` |
| G | §VII Discussion | Limitations + threats to validity + 2nd-paper redesign notes | `build/journal_suppl_G_limitations.pdf` |

## Layout

```
supplementary/
├── README.md          (this index)
├── preamble.tex       (shared LaTeX preamble for every supplement)
├── conference/
│   ├── suppl_A_introduction.tex
│   ├── suppl_B_method_derivations.tex
│   ├── suppl_C_datasets.tex
│   ├── suppl_D_extended_results.tex
│   └── suppl_E_discussion.tex
├── journal/
│   ├── suppl_A_introduction.tex
│   ├── suppl_B_related_work.tex
│   ├── suppl_C_axis_motivation.tex
│   ├── suppl_D_mathematical_derivations.tex
│   ├── suppl_E_datasets.tex
│   ├── suppl_F_extended_results.tex
│   └── suppl_G_limitations.tex
├── build/             (PDFs, gitignored except for the latest set)
└── word/              (DOCX conversions via pandoc, see scripts/build-supplements.{ps1,sh})
```

## Build

```bash
# All PDFs in one pass:
bash scripts/build-supplements.sh

# Or PowerShell equivalent:
scripts/build-supplements.ps1
```

Each supplement compiles standalone (no cross-document references),
so a reader who wants only Suppl D of the journal does not need to
build the other six.

## Word output

Pandoc-generated DOCX versions live under `word/`:

```
supplementary/word/
├── conference/
│   ├── suppl_A_introduction.docx
│   ├── ...
└── journal/
    ├── suppl_A_introduction.docx
    ├── ...
```

## Bibliography

All twelve supplements share `bibliography/refs.bib` with the main
manuscripts. No supplement introduces a new citation that is not
also in the .bib file.

## Status

| Supplement | LaTeX | PDF builds | Word | Status |
|---|---|---|---|---|
| Conf A | ✅ | ✅ | (build) | shipped |
| Conf B | ✅ | ✅ | (build) | shipped |
| Conf C | ✅ | ✅ | (build) | shipped |
| Conf D | ✅ | ✅ | (build) | shipped |
| Conf E | ✅ | ✅ | (build) | shipped |
| Journal A | ✅ | ✅ | (build) | shipped |
| Journal B | ✅ | ✅ | (build) | shipped |
| Journal C | ✅ | ✅ | (build) | shipped |
| Journal D | ✅ | ✅ | (build) | shipped |
| Journal E | ✅ | ✅ | (build) | shipped |
| Journal F | ✅ | ✅ | (build) | shipped |
| Journal G | ✅ | ✅ | (build) | shipped |
