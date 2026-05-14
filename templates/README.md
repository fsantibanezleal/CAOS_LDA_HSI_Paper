# Template references

This directory documents the LaTeX templates the two manuscripts use.
We do **not** redistribute the template source files here — they
remain under their publishers' licensing. Instead, the
`conference/tex/` and `journal/tex/` directories use the IEEEtran
class (`IEEEtran.cls`) which is on CTAN under the LaTeX Project
Public License (LPPL) and ships with most TeX Live / MiKTeX
installations.

## Conference paper (WHISPERS 2026)

- **Class:** `IEEEtran` with the conference option.
- **Citation:** IEEE Conference Format Author Kit (linked from the
  WHISPERS 2026 submission page once available).
- **Working preamble:**
  ```latex
  \documentclass[conference,a4paper,10pt]{IEEEtran}
  ```
- **Page limit:** 4-5 pages (full paper track, IEEE Xplore inclusion).
- **Column layout:** Two columns.
- **Bibliography style:** `IEEEtran.bst`.

## Journal article (IEEE TGRS)

- **Class:** `IEEEtran` with the journal option.
- **Citation:** IEEE Transactions Template via the GRSS author
  resources page (Overleaf link).
- **Working preamble:**
  ```latex
  \documentclass[journal,a4paper,10pt]{IEEEtran}
  ```
- **Page limit:** No hard limit; **mandatory $230/page Overlength Page
  Charge (OPC) beginning page 11** for submissions after 1 Jan 2026.
  Budget ~$2,300-4,600 OPC for a 20-30 page paper.
- **Column layout:** Two columns.
- **Bibliography style:** `IEEEtran.bst`.

## Required TeX packages

Both manuscripts use the same package set:

```latex
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath, amssymb, amsfonts}
\usepackage{graphicx}
\usepackage{cite}              % IEEEtran-compatible citations
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{hyperref}          % loaded LAST per IEEEtran convention
```

## Locally-built IEEEtran

If a local TeX installation does not bundle `IEEEtran`, download from
CTAN:

```
https://ctan.org/tex-archive/macros/latex/contrib/IEEEtran
```

Place `IEEEtran.cls`, `IEEEtran.bst`, and any required `.sty` files in
the same directory as `main.tex` or in your local TeX tree
(`~/texmf/tex/latex/IEEEtran/`).

## Build

```bash
# Conference
cd conference/tex && latexmk -pdf main.tex

# Journal
cd journal/tex && latexmk -pdf main.tex
```

## License

The IEEEtran class and bibliography style are released under LPPL.
Original IEEE author kits (PDF guides, example .tex skeletons) carry
IEEE's own redistribution terms; we do not vendor them here.
