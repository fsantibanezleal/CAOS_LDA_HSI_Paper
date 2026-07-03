# CAOS_LDA_HSI — Paper Manuscripts

[![License](https://img.shields.io/github/license/fsantibanezleal/CAOS_LDA_HSI_Paper)](LICENSE)

Manuscripts repository for the **CAOS_LDA_HSI** project — topic
modelling on hyperspectral imagery, with strong emphasis on
reproducibility and a multi-axis evaluation framework.

Companion repositories:

- [`CAOS_LDA_HSI`](https://github.com/fsantibanezleal/CAOS_LDA_HSI) —
  code, data pipeline, FastAPI backend and React frontend
  (web app at <https://lda-hsi.fasl-work.com>)
- [`CAOS_LDA_HSI.wiki`](https://github.com/fsantibanezleal/CAOS_LDA_HSI/wiki) —
  technical documentation

## 📄 Compiled PDFs

**All current manuscript PDFs in one place: [`pdfs/`](pdfs/).**
That is the canonical link to share — not the repository root.

## Manuscripts

This repository hosts **five manuscripts** plus an internal technical
report. Target venues are intentionally **redacted** while the work
circulates as preprints.

| # | Manuscript | Form | Source | PDF |
|---|---|---|---|---|
| 1 | Beyond Accuracy: A Multi-Axis Evaluation Framework for Interpretable Topic Models on Hyperspectral Imagery | Journal article (~20-30 pp) | [`journal/`](journal/) | [pdf](pdfs/journal-multi-axis-framework.pdf) |
| 2 | A Band-Mask Robustness Diagnostic for Latent Dirichlet Allocation on Hyperspectral Imagery | Conference paper (4-8 pp) | [`conference/`](conference/) | [pdf](pdfs/conference-band-mask-robustness.pdf) |
| 3 | Which Wordification Matters? A Nineteen-Recipe Sweep of the Interpretable-Topic-Model Framework on Hyperspectral Imagery | Journal article | [`journal_v_sweep/`](journal_v_sweep/) | [pdf](pdfs/journal-wordification-sweep.pdf) |
| 4 | Which Backbone Picks Which Wordification? A Factorial Study of Topic-Model Families on Hyperspectral Imagery | Journal article | [`journal_backbone_factorial/`](journal_backbone_factorial/) | [pdf](pdfs/journal-backbone-factorial.pdf) |
| 5 | Post-hoc Interpretability of LDA on Hyperspectral Imagery: SHAP Attributions, Counterfactual Topic Flips, and LLM-judge Alignment | Journal article | [`journal_interpretability/`](journal_interpretability/) | [pdf](pdfs/journal-interpretability.pdf) |
| — | Internal technical report (design space, K-policy, V-sweep results, reproducibility audit, paper portfolio, HIDSAG results) | Internal notes (Markdown) | [`internal_tech_report/`](internal_tech_report/) | — |

Each LaTeX manuscript ships in two formats:

- **LaTeX source** (`<form>/tex/`) — primary, with IEEEtran class +
  validated bibliography
- **Word** (`<form>/word/`) — Pandoc-converted from LaTeX

## Repository layout

```
CAOS_LDA_HSI_Paper/
├── pdfs/                        ← all compiled manuscript PDFs (share this)
├── journal/                     Multi-axis evaluation framework (flagship)
│   ├── tex/                       LaTeX source (IEEEtran journal)
│   ├── figures/                   SVG/PDF figures
│   ├── word/                      .docx (Pandoc-converted)
│   └── build/                     PDF output (main.pdf tracked)
├── conference/                  Band-mask robustness diagnostic (short paper)
│   └── tex/ figures/ word/ build/
├── journal_v_sweep/             Nineteen-recipe wordification sweep
├── journal_backbone_factorial/  Backbone × wordification factorial study
├── journal_interpretability/    SHAP / counterfactual / LLM-judge interpretability
├── internal_tech_report/        Internal Markdown notes (not for submission)
├── supplementary/               Per-chapter supplementary material
├── bibliography/                Shared .bib file + validation notes
├── venues/                      Venue research (kept internal)
├── templates/                   IEEEtran reference templates
├── equations/                   Shared equation snippets
├── data/                        Manuscript-specific extracted data (CSVs)
└── figures/                     Deterministic figures + Python builders
    └── source/                  Builders driven from CAOS_LDA_HSI/data/derived/
```

## Branch flow

- `main` — release-ready manuscripts
- `develop` — work in progress, integration before main

All other work happens on `task/<5-digit-id>/<descriptor>` branches
PR'd to `develop`.

## Reproducibility commitment

Every numerical claim in any manuscript is backed by a JSON / binary
file in `CAOS_LDA_HSI/data/derived/` and a public endpoint at
<https://lda-hsi.fasl-work.com/api/...>. The manuscripts do **not** add
new experiments; they describe and contextualise results already
produced and validated by the companion code repo's pipeline
(~3,900 derived artefacts).

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
# LaTeX → PDF (run in any manuscript's tex/ directory)
cd journal/tex && latexmk -pdf main.tex
# then copy the output into the shared folder under a descriptive name:
cp main.pdf ../../pdfs/journal-multi-axis-framework.pdf

# LaTeX → Word via Pandoc
pandoc -s journal/tex/main.tex \
       --bibliography=bibliography/refs.bib \
       --citeproc \
       -o journal/word/manuscript.docx
```

## Funding

This work has been partially funded by The Advanced Mining Technology
Center (AMTC) Basal project (ANID/PIA Project AFB220002) and ANID
FONDECYT Postdoctorado 3220094.
