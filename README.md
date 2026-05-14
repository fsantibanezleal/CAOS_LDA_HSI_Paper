# CAOS_LDA_HSI — Paper Manuscripts

Manuscripts repository for the **CAOS_LDA_HSI** project — topic
modelling on hyperspectral imagery, with strong emphasis on
reproducibility and a multi-axis evaluation framework.

Companion repositories:

- [`CAOS_LDA_HSI`](https://github.com/fsantibanezleal/CAOS_LDA_HSI) —
  code, data pipeline, FastAPI backend and React frontend
  (web app at <https://lda-hsi.fasl-work.com>)
- [`CAOS_LDA_HSI.wiki`](https://github.com/fsantibanezleal/CAOS_LDA_HSI/wiki) —
  technical documentation

This repository contains **two manuscripts** in parallel:

| Form | Target | Scope | Location |
|---|---|---|---|
| Conference paper (4-8 pp) | [WHISPERS 2026](https://www.ieee-whispers.com/) (IEEE GRSS hyperspectral workshop) | Band-mask robustness diagnostic for LDA on hyperspectral imagery | [`conference/`](conference/) |
| Journal article (~20-30 pp) | [IEEE TGRS](https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=36) (Trans. Geoscience and Remote Sensing) | Topic models as interpretable spectral mixtures — full multi-axis framework + reproducibility discipline + band-mask robustness | [`journal/`](journal/) |

Each manuscript ships in two formats:

- **LaTeX source** (`<form>/tex/`) — primary, with IEEEtran class +
  validated bibliography
- **Word** (`<form>/word/`) — Pandoc-converted from LaTeX

## Repository layout

```
CAOS_LDA_HSI_Paper/
├── conference/                  WHISPERS 4-8 pp paper
│   ├── tex/                       LaTeX source (IEEEtran conf)
│   ├── figures/                   SVG/PDF figures
│   ├── word/                      .docx (Pandoc-converted)
│   └── build/                     PDF output (gitignored)
├── journal/                     IEEE TGRS 20-30 pp article
│   ├── tex/                       LaTeX source (IEEEtran journal)
│   ├── figures/                   SVG/PDF figures
│   ├── word/                      .docx (Pandoc-converted)
│   └── build/                     PDF output (gitignored)
├── supplementary/               Per-chapter supplementary material
│   ├── conference/                5 supplements A..E (one per
│   │                              conference §)
│   ├── journal/                   7 supplements A..G (one per
│   │                              journal §)
│   ├── build/                     supplement PDFs (gitignored)
│   └── word/                      supplement DOCX (gitignored)
├── bibliography/                Shared .bib file + validation notes
├── venues/                      Venue research (conferences + journals)
├── templates/                   IEEEtran reference templates
├── docs/                        Project-level docs (this is the repo
│                                README; per-manuscript guidance lives
│                                in each form's tex/ folder)
├── data/                        Manuscript-specific extracted data
│                                (small enough to commit; e.g. CSVs
│                                of paired ARI numbers, etc.)
└── figures/                     9 deterministic figures + builders
    └── source/                  Python builders driven from
                                  CAOS_LDA_HSI/data/derived/
```

## Branch flow

- `main` — release-ready manuscripts; CI builds PDFs from `tex/`
  sources
- `develop` — work in progress, integration before main

All other work happens on `task/<5-digit-id>/<descriptor>` branches
PR'd to `develop`.

## Reproducibility commitment

Every numerical claim in either manuscript is backed by a
JSON / binary file in `CAOS_LDA_HSI/data/derived/` and a public
endpoint at <https://lda-hsi.fasl-work.com/api/...>. The manuscripts
do **not** add new experiments; they describe and contextualise
results already produced and validated by the companion code repo's
pipeline (1726+ artefacts as of cycle 138).

## Bibliography discipline

The shared `.bib` file in [`bibliography/`](bibliography/) follows
two strict rules:

1. Every entry is **independently verified** against the publisher's
   record (DOI, ISBN, or arXiv ID resolves to the cited title and
   authors). Fabricated references are not acceptable.
2. Every cited claim is supported by the **right kind** of source
   (a textbook for foundational definitions; a peer-reviewed paper
   for a specific method; a dataset descriptor for an HSI scene).

## Build commands

```bash
# LaTeX → PDF
cd conference/tex && latexmk -pdf main.tex     # WHISPERS conf
cd journal/tex && latexmk -pdf main.tex        # IEEE TGRS

# LaTeX → Word via Pandoc
pandoc -s conference/tex/main.tex \
       --bibliography=bibliography/refs.bib \
       --citeproc \
       -o conference/word/manuscript.docx

pandoc -s journal/tex/main.tex \
       --bibliography=bibliography/refs.bib \
       --citeproc \
       -o journal/word/manuscript.docx
```

## Status

| Cycle | Section | Form | Status |
|---|---|---|---|
| 140 | Repo bootstrap + dir structure | — | done |
| 141 | Venue research | — | done |
| 142 | LaTeX templates | both | done |
| 143 | Validated bibliography | both | done |
| 144 | Conference paper draft | conference | done |
| 145 | Journal article draft | journal | done |
| 146 | Pandoc → Word | both | done |
| 147 | Web app cross-link | (other repo) | done |
| 148 | Final review + push | — | done |
