# Figures

All figures are generated deterministically from the
`data/derived/` artefacts in the companion code repository
`CAOS_LDA_HSI`. No figure is hand-drawn; every figure is reproducible
from a single Python script under `figures/source/`.

## Figure inventory

| Figure file | Built by | Primary source artefact(s) | Used in |
|---|---|---|---|
| `paired-ari-heatmap.{svg,pdf}` | `source/build_paired_ari_heatmap.py` | `band_masks/canonical_comparison.json` | Conf §IV, Journal B-5 |
| `hungarian-alignment-example.{svg,pdf}` | `source/build_hungarian_alignment.py` | `topic_to_data/salinas-a-corrected_dominant_topic_map.bin` + `band_masks/salinas-a-corrected/swir/dominant_topic_map.bin` + canonical_comparison.json (for σ\*) | Conf §IV, Journal B-8 |
| `bayesian-method-comparison.{svg,pdf}` | `source/build_bayesian_method_comparison.py` | `method_statistics_{labelled,hidsag}/cross_classification_bayesian.json` | Journal B-1 |
| `coherence-vs-ari.{svg,pdf}` | `source/build_coherence_vs_ari.py` | `neural_topic_comparison/<scene>.json` × 6 | Journal V.C, Suppl F |
| `seed-stability-swarm.{svg,pdf}` | `source/build_seed_stability_swarm.py` | `neural_topic_seed_stability/<scene>.json` × 6 | Journal B-3, Suppl F |
| `capacity-sweep.{svg,pdf}` | `source/build_capacity_sweep.py` | `lda_sweep/<scene>.json` × 6 | Journal B-4, Suppl F |
| `cross-method-ari-grid.{svg,pdf}` | `source/build_cross_method_grid.py` | `cross_method_agreement/<scene>.json` × 6 | Journal B-6, Suppl F |
| `basis-spectra-grid.{svg,pdf}` | `source/build_basis_spectra_grid.py` | `topic_views/<scene>.json` × 6 (`topic_band_profiles`, `wavelengths_nm`) | Journal III, Suppl D |
| `hidsag-band-mask.{svg,pdf}` | `source/build_hidsag_band_mask.py` | `band_masks_hidsag/index.json` | Journal B-5 (HIDSAG side), Suppl F |
| `topic-profile-cards-salinas-a.{svg,pdf}` | `source/build_topic_profile_cards.py` | `topic_views/salinas-a-corrected.json` + `topic_to_data/salinas-a-corrected.json` | Suppl H |
| `topic-profile-cards-indian-pines.{svg,pdf}` | same | `topic_views/indian-pines-corrected.json` + `topic_to_data/indian-pines-corrected.json` | Suppl H |
| `topic-spectra-contrast.{svg,pdf}` | `source/build_topic_spectra_contrast.py` | `topic_views/{salinas-a-corrected,kennedy-space-center}.json` | Suppl H |
| `topic-pairwise-distance.{svg,pdf}` | `source/build_topic_pairwise_distance.py` | `topic_views/<scene>.json` × 6 (`topic_distance_cosine`) | Suppl H |
| `hidsag-topic-spectra.{svg,pdf}` | `source/build_hidsag_topic_spectra.py` | `band_masks_hidsag/<subset>/swir/summary.json` × 5 | Suppl H |

## Honest gaps

The figure set deliberately omits a few candidates whose source data
is partial or whose value-add over an existing figure is marginal:

- **Per-pixel dominant-topic rasters.** Each scene has a
  `dominant_topic_map.bin` (uint8 H×W) and rendering them as a 6-panel
  raster would be informative — but the spatial sizes are very
  heterogeneous (Salinas-A 83×86 vs Botswana 1476×256) and faithful
  rendering across the grid would crowd the page. The web app at
  `lda-hsi.fasl-work.com/workspace > raster` is the appropriate
  interactive surface for these.
- **Rate–distortion curve.** The relevant artefact
  (`rate_distortion_curve/*.json`) exists but reconstructs the spectrum
  from quantised tokens, which mixes a tokenisation-loss confound into
  the curve. Discussed as a limitation in journal §VII.

## Building

```bash
cd figures/source
python build_paired_ari_heatmap.py
python build_hungarian_alignment.py
python build_bayesian_method_comparison.py
python build_coherence_vs_ari.py
python build_seed_stability_swarm.py
python build_capacity_sweep.py
python build_cross_method_grid.py
python build_basis_spectra_grid.py
python build_hidsag_band_mask.py
```

Each script writes both an `.svg` (canonical, for the README and the
SVG archive) and a `.pdf` (for inclusion via `\includegraphics`) into
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
