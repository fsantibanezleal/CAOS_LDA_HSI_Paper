# Figures

All figures are generated deterministically from the
`data/derived/` artefacts in the companion code repository
`CAOS_LDA_HSI`. No figure is hand-drawn; every figure is reproducible
from a single Python script under `figures/source/`.

| Figure file | Built by | Source artefact | Used in |
|---|---|---|---|
| `paired-ari-heatmap.{svg,pdf}` | `source/build_paired_ari_heatmap.py` | `data/derived/band_masks/canonical_comparison.json` | Conference §IV, Journal B-5 |
| `hungarian-alignment-example.{svg,pdf}` | `source/build_hungarian_alignment.py` | same | Conference §IV, Journal B-8 |
| `bayesian-method-comparison.{svg,pdf}` | `source/build_bayesian_method_comparison.py` | `data/derived/method_statistics_{labelled,hidsag}/cross_classification_bayesian.json` | Journal B-1 |

## Building

```bash
cd figures/source
python build_paired_ari_heatmap.py
python build_hungarian_alignment.py
python build_bayesian_method_comparison.py
```

Each script writes both an `.svg` (canonical, for the README and the
SVG-archive) and a `.pdf` (for inclusion via `\includegraphics`) into
three locations:

- `figures/` (canonical archive)
- `conference/figures/` (resolved by `conference/tex/main.tex`)
- `journal/figures/` (resolved by `journal/tex/main.tex`)

Re-running is idempotent: the scripts have no RNG, no clock-dependent
inputs, and overwrite their outputs.

## Dependencies

```
python >= 3.10
matplotlib >= 3.7
numpy >= 1.24
```

The scripts use the non-interactive `Agg` backend so they run on
headless CI runners.
