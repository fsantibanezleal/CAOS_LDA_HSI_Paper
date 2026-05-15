# Figures

All figures are generated deterministically from the
`data/derived/` artefacts in the companion code repository
`CAOS_LDA_HSI`. No figure is hand-drawn; every figure is reproducible
from a single Python script under `figures/source/`.

## Figure inventory

| Figure file | Built by | Primary source artefact(s) | Used in |
|---|---|---|---|
| `paired-ari-heatmap.{svg,pdf}` | `source/build_paired_ari_heatmap.py` | `band_masks/canonical_comparison.json` | Conf §IV, Journal F-5 |
| `hungarian-alignment-example.{svg,pdf}` | `source/build_hungarian_alignment.py` | `topic_to_data/salinas-a-corrected_dominant_topic_map.bin` + `band_masks/salinas-a-corrected/swir/dominant_topic_map.bin` + canonical_comparison.json (for σ\*) | Conf §IV, Journal F-8 |
| `bayesian-method-comparison.{svg,pdf}` | `source/build_bayesian_method_comparison.py` | `method_statistics_{labelled,hidsag}/cross_classification_bayesian.json` | Journal F-1 |
| `coherence-vs-ari.{svg,pdf}` | `source/build_coherence_vs_ari.py` | `neural_topic_comparison/<scene>.json` × 6 | Journal V.C, Suppl F |
| `seed-stability-swarm.{svg,pdf}` | `source/build_seed_stability_swarm.py` | `neural_topic_seed_stability/<scene>.json` × 6 | Journal F-3, Suppl F |
| `capacity-sweep.{svg,pdf}` | `source/build_capacity_sweep.py` | `lda_sweep/<scene>.json` × 6 | Journal F-4, Suppl F |
| `cross-method-ari-grid.{svg,pdf}` | `source/build_cross_method_grid.py` | `cross_method_agreement/<scene>.json` × 6 | Journal F-6, Suppl F |
| `basis-spectra-grid.{svg,pdf}` | `source/build_basis_spectra_grid.py` | `topic_views/<scene>.json` × 6 (`topic_band_profiles`, `wavelengths_nm`) | Journal III, Suppl D |
| `hidsag-band-mask.{svg,pdf}` | `source/build_hidsag_band_mask.py` | `band_masks_hidsag/index.json` | Journal F-5 (HIDSAG side), Suppl F |
| `topic-profile-cards-salinas-a.{svg,pdf}` | `source/build_topic_profile_cards.py` | `topic_views/salinas-a-corrected.json` + `topic_to_data/salinas-a-corrected.json` | Suppl H |
| `topic-profile-cards-indian-pines.{svg,pdf}` | same | `topic_views/indian-pines-corrected.json` + `topic_to_data/indian-pines-corrected.json` | Suppl H |
| `topic-spectra-contrast.{svg,pdf}` | `source/build_topic_spectra_contrast.py` | `topic_views/{salinas-a-corrected,kennedy-space-center}.json` | Suppl H |
| `topic-pairwise-distance.{svg,pdf}` | `source/build_topic_pairwise_distance.py` | `topic_views/<scene>.json` × 6 (`topic_distance_cosine`) | Suppl H |
| `hidsag-topic-spectra.{svg,pdf}` | `source/build_hidsag_topic_spectra.py` | `band_masks_hidsag/<subset>/swir/summary.json` × 5 | Suppl H |
| `hidsag-preprocessing-stability.{svg,pdf}` | `source/build_hidsag_preprocessing_stability.py` | `hidsag_cross_preprocessing_stability/<subset>.json` × 5 | Journal F-9, Suppl F |
| `cross-scene-transfer.{svg,pdf}` | `source/build_cross_scene_transfer.py` | `cross_scene_transfer/transfer_matrix.json` | Journal F-10, Suppl F |
| `rate-distortion.{svg,pdf}` | `source/build_rate_distortion.py` | `rate_distortion_curve/<scene>.json` × 6 | Journal F-11, Suppl F |
| `deep-seed-stability-n30.{svg,pdf}` | `source/build_deep_seed_stability_n30.py` | `deep_seed_stability/<scene>__<method>__N30.json` × 24 | Suppl F (companion to F-3) |
| `topic-class-heatmap.{svg,pdf}` | `source/build_topic_class_heatmap.py` | `topic_to_data/<scene>.json` × 6 (`p_label_given_topic_dominant`) | Suppl I |
| `per-topic-class-bars.{svg,pdf}` | `source/build_per_topic_class_bars.py` | same as above | Suppl I |
| `topic-class-sankey.{svg,pdf}` | `source/build_topic_class_sankey.py` | same as above | Suppl I |
| `theta-embedding-scatter.{svg,pdf}` | `source/build_theta_embedding_scatter.py` | `topic_to_data/<scene>.json` (`theta_embedding_pca_2d`) | Suppl I |
| `confidence-ridge.{svg,pdf}` | `source/build_confidence_ridge.py` | same as above (`confidence` field) | Suppl I |
| `hidsag-topic-covariate.{svg,pdf}` | `source/build_hidsag_topic_covariate.py` | `band_masks_hidsag/<subset>/swir/summary.json` (`p_covariate_given_topic_dominant`) | Suppl I |
| `hidsag-measurement-ridges.{svg,pdf}` | `source/build_hidsag_measurement_ridges.py` | `hidsag_topic_measurements/<subset>.json` × 5 | Suppl I |
| `hidsag-corner-geomet.{svg,pdf}` | `source/build_hidsag_corner_geomet.py` | `hidsag_topic_measurements/GEOMET.json` | Suppl I |
| `hidsag-measurement-mosaic.{svg,pdf}` | `source/build_hidsag_mosaic.py` | `hidsag_topic_measurements/{PORPHYRY,GEOMET,MINERAL1}.json` | Suppl I |
| `hidsag-corner-mineral2.{svg,pdf}` | `source/build_hidsag_corner_mineral2_porphyry.py` | `hidsag_topic_measurements/MINERAL2.json` | Suppl I |
| `hidsag-corner-porphyry.{svg,pdf}` | same | `hidsag_topic_measurements/PORPHYRY.json` | Suppl I |
| `porphyry-hammock.{svg,pdf}` | `source/build_porphyry_hammock.py` | `hidsag_topic_measurements/PORPHYRY.json` | Suppl I |
| `neural-topic-word-compare.{svg,pdf}` | `source/build_neural_topic_word_compare.py` | `topic_views/<scene>.json` + `topic_variants/{prodlda,etm}/<scene>.json` | Suppl I |

## Honest gaps

With the c190-c193 figure-batch, every F-axis B-1..B-12 now has at
least one figure (most have multiple). The figure set deliberately
omits a few candidates whose source data is partial or whose
value-add over an existing figure is marginal:

- **Per-pixel dominant-topic rasters.** Each scene has a
  `dominant_topic_map.bin` (uint8 H×W) and rendering them as a 6-panel
  raster would be informative — but the spatial sizes are very
  heterogeneous (Salinas-A 83×86 vs Botswana 1476×256) and faithful
  rendering across the grid would crowd the page. The web app at
  `lda-hsi.fasl-work.com/workspace > raster` is the appropriate
  interactive surface for these.

Note: `rate-distortion.{svg,pdf}` is now shipped (`build_rate_distortion.py`),
with the tokenisation-loss caveat preserved in journal §VII /
Suppl G §Reporting choices rather than as a missing-figure pointer.

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
python build_topic_profile_cards.py
python build_topic_spectra_contrast.py
python build_topic_pairwise_distance.py
python build_hidsag_topic_spectra.py
python build_hidsag_preprocessing_stability.py
python build_cross_scene_transfer.py
python build_rate_distortion.py
python build_deep_seed_stability_n30.py
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
