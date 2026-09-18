# Compiled manuscript PDFs

All current manuscript PDFs for the **CAOS_LDA_HSI** project in one place.
These are the rendered outputs; the LaTeX sources live in each manuscript's
`<form>/tex/` directory. Each preprint is archived on Zenodo; the concept DOI
always resolves to its latest version.

| PDF | Manuscript | Form | Concept DOI |
|---|---|---|---|
| [`journal-multi-axis-framework.pdf`](journal-multi-axis-framework.pdf) | Beyond Accuracy: A Multi-Axis Evaluation Framework for Interpretable Topic Models on Hyperspectral Imagery | Journal article | [10.5281/zenodo.21504115](https://doi.org/10.5281/zenodo.21504115) |
| [`conference-band-mask-robustness.pdf`](conference-band-mask-robustness.pdf) | A Band-Mask Robustness Diagnostic for Latent Dirichlet Allocation on Hyperspectral Imagery | Conference paper | [10.5281/zenodo.21504109](https://doi.org/10.5281/zenodo.21504109) |
| [`journal-wordification-sweep.pdf`](journal-wordification-sweep.pdf) | Which Wordification Matters? A Nineteen-Recipe Sweep of the Interpretable-Topic-Model Framework on Hyperspectral Imagery | Journal article | [10.5281/zenodo.21504117](https://doi.org/10.5281/zenodo.21504117) |
| [`journal-backbone-factorial.pdf`](journal-backbone-factorial.pdf) | Which Backbone Picks Which Wordification? A Factorial Study of Topic-Model Families on Hyperspectral Imagery | Journal article | [10.5281/zenodo.21504111](https://doi.org/10.5281/zenodo.21504111) |
| [`journal-interpretability.pdf`](journal-interpretability.pdf) | Post-hoc Interpretability of LDA on Hyperspectral Imagery: SHAP Attributions, Counterfactual Topic Flips, and LLM-judge Alignment under Token-Mass-Dispersion Asymmetry | Journal article | [10.5281/zenodo.21504113](https://doi.org/10.5281/zenodo.21504113) |

The preprints are published on Zenodo under CC BY 4.0, the licence printed in
each PDF's header. The repository, including the LaTeX sources, is released
under MIT; see the repository root `LICENSE`.

> Regenerate after editing a source: `latexmk -pdf` in the manuscript's
> `tex/` directory, then copy `main.pdf` here under its descriptive name.
