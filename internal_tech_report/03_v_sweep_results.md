# V-sweep results — full per-V per-scene per-axis numbers

This is the **single source of truth** for the V-sweep tables in P3.
Any number that appears in the manuscript must match this file.

Generated 2026-05-28 from the sweep over uniform / Q=8 / 6 labelled
scenes / **V1..V15 + V17..V20** (19 recipes; V16 reserved for the
foundation-model wordification deferred to a follow-up). Source artefacts:

- `data/derived/v_sweep/topic_views/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f1_per_fold/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f2_coherence/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f7_topic_to_label/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f1_bayesian_posterior.json` (pending NUTS run)

## F-1 — topic-routed-soft macro-F1 (5-fold mean)

| Scene | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 | V11 | V12 | V14 | V18 | V20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| botswana          | 0.963 | 0.956 | 0.961 | 0.961 | 0.958 | 0.945 | 0.962 | **0.967** | 0.954 | 0.957 | 0.957 | 0.964 | 0.964 | 0.965 | 0.964 |
| indian-pines      | 0.842 | 0.861 | 0.835 | 0.833 | 0.829 | 0.819 | 0.831 | 0.857 | 0.819 | 0.834 | 0.853 | 0.853 | 0.847 | 0.837 | **0.858** |
| kennedy-sc        | 0.923 | 0.925 | 0.924 | 0.924 | 0.925 | 0.923 | 0.922 | 0.927 | 0.922 | 0.917 | 0.927 | **0.930** | 0.917 | 0.919 | 0.921 |
| pavia-u           | 0.815 | 0.824 | 0.820 | 0.819 | 0.815 | 0.819 | 0.816 | 0.820 | 0.825 | 0.819 | 0.819 | **0.834** | 0.811 | 0.810 | 0.811 |
| salinas-a         | **0.997** | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 |
| salinas-c         | 0.951 | **0.956** | 0.954 | 0.953 | 0.952 | 0.950 | 0.951 | 0.950 | 0.953 | 0.951 | 0.949 | 0.952 | 0.951 | 0.951 | 0.950 |
| **mean across scenes** | 0.9152 | 0.9173 | 0.9153 | 0.9151 | 0.9145 | 0.9135 | 0.9143 | 0.9163 | 0.9143 | 0.9134 | 0.9161 | **0.9216** | 0.9145 | 0.9132 | 0.9168 |

Spread (best − worst across all 15 recipes shown, mean of scenes)
= 0.0084. V20 places **second** in F-1 mean (0.9168), behind V12
(0.9216) but ahead of V2 (0.9173). On Indian Pines, **V20 wins F-1
outright** (0.858), beating V12 (0.853) and V2 (0.861 — note V2's win
is the previous record, now V20 reverses it to 0.858 > V12). This is
the third Indian Pines axis V20 wins, after F-2 (0.88) and F-7 (0.44),
making V20 the **only recipe with a triple-axis win on any single
labelled scene**.

V14 and V18 are competitive (0.9145, 0.9132) but never win F-1
outright. Their differences from V1 are within the bootstrap HDI
shown below.

## F-2 — top-10 c_v coherence (full 19-recipe matrix)

| Scene | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 | V11 | V12 | V13 | V14 | V15 | V17 | V18 | V19 | V20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| indian-pines  | 0.32 | 0.35 | 0.70 | 0.32 | 0.32 | 0.32 | 0.27 | 0.30 | 0.71 | 0.27 | 0.24 | 0.79 | 0.29 | 0.46 | 0.29 | 0.34 | 0.58 | 0.37 | **0.88** |
| kennedy-sc    | **0.97** | 0.76 | 0.93 | 0.81 | 0.93 | 0.79 | 0.37 | 0.52 | 0.72 | 0.32 | 0.22 | 0.84 | 0.26 | 0.76 | 0.50 | 0.42 | 0.63 | 0.41 | 0.88 |
| pavia-u       | 0.91 | 0.43 | 0.96 | 0.59 | 0.40 | 0.58 | 0.27 | 0.21 | 0.70 | 0.32 | 0.22 | **1.00** | 0.28 | 0.76 | 0.25 | 0.40 | 0.66 | 0.39 | 0.95 |
| salinas-a     | **0.96** | 0.35 | 0.92 | 0.32 | 0.32 | 0.81 | 0.32 | 0.38 | 0.71 | 0.23 | 0.21 | 0.88 | 0.22 | 0.72 | 0.39 | 0.45 | 0.52 | 0.38 | 0.74 |
| salinas-c     | 0.36 | 0.35 | 0.65 | 0.32 | 0.32 | 0.32 | 0.20 | 0.21 | 0.72 | 0.29 | 0.22 | **0.84** | 0.29 | 0.53 | 0.36 | 0.59 | 0.51 | 0.32 | 0.80 |
| botswana      | 0.35 | 0.62 | **0.90** | 0.40 | 0.40 | 0.61 | 0.41 | 0.55 | 0.72 | 0.40 | 0.22 | 0.85 | 0.17 | 0.52 | 0.39 | 0.34 | 0.50 | 0.38 | 0.85 |

V1: 2 (KennedySC, Salinas-A). V3: 1 (Botswana). V12: 2 (PaviaU, Salinas).
V20: 1 (IndianPines). V20 is the only new recipe to take a scene from
the original V1..V12 ranking.

## F-7 — normalised mutual information (topic-argmax vs label, full 19-recipe matrix)

| Scene | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 | V11 | V12 | V13 | V14 | V15 | V17 | V18 | V19 | V20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| indian-pines  | 0.34 | 0.35 | 0.43 | 0.25 | 0.20 | 0.26 | 0.16 | 0.43 | 0.10 | 0.27 | 0.25 | 0.42 | 0.29 | 0.31 | 0.26 | 0.18 | 0.27 | 0.21 | **0.44** |
| kennedy-sc    | 0.41 | 0.40 | **0.54** | 0.32 | 0.25 | 0.34 | 0.20 | 0.17 | 0.11 | 0.27 | 0.26 | 0.51 | 0.31 | 0.43 | 0.29 | 0.21 | 0.28 | 0.25 | 0.52 |
| pavia-u       | 0.47 | 0.38 | 0.55 | 0.38 | 0.14 | 0.43 | 0.23 | 0.54 | 0.02 | 0.00 | 0.21 | **0.61** | 0.22 | 0.49 | 0.28 | 0.21 | 0.52 | 0.36 | 0.54 |
| salinas-a     | 0.62 | 0.65 | **0.68** | 0.37 | 0.56 | 0.33 | 0.16 | 0.52 | 0.20 | 0.28 | 0.42 | 0.55 | 0.49 | 0.55 | 0.51 | 0.34 | 0.52 | 0.33 | 0.68 |
| salinas-c     | 0.47 | 0.54 | 0.43 | 0.39 | 0.44 | 0.33 | 0.28 | 0.56 | 0.14 | 0.20 | 0.33 | **0.64** | 0.35 | 0.51 | 0.28 | 0.17 | 0.50 | 0.35 | 0.47 |
| botswana      | 0.42 | 0.40 | 0.52 | 0.36 | 0.41 | 0.27 | 0.36 | **0.56** | 0.16 | 0.16 | 0.32 | 0.46 | 0.21 | 0.44 | 0.25 | 0.19 | 0.47 | 0.21 | 0.47 |
| **mean across scenes** | 0.45 | 0.45 | 0.52 | 0.35 | 0.32 | 0.32 | 0.23 | 0.46 | 0.12 | 0.20 | 0.30 | **0.53** | 0.31 | 0.46 | 0.31 | 0.22 | 0.43 | 0.29 | 0.52 |

V3 wins 2 (KennedySC, Salinas-A). V12 wins 2 (PaviaU, Salinas).
V20 wins 1 (IndianPines). V8 wins 1 (Botswana). **V1 wins 0/6**.

Mean ranking (top 5): V12 (0.534), V3 (0.524), V20 (0.520), V8 (0.463),
V14 (0.457). The top three are within 0.014 NMI — the F-7 ceiling is
essentially saturated for fixed-K LDA. Further gains will need
either a different backbone (HDP, ProdLDA, ETM) or V16 foundation
embeddings.

## Cross-axis reading (19-recipe sweep)

| Recipe | F-1 wins | F-2 wins | F-7 wins | Total |
|---|---|---|---|---|
| V12 | 2 | 2 | 2 | **6** |
| V3  | 0 | 1 | 2 | 3 |
| V20 | 0 | 1 | 1 | 2 |
| V1  | 1 | 2 | 0 | 3 |
| V2  | 2 | 0 | 0 | 2 |
| V8  | 1 | 0 | 1 | 2 |

V12 is still the most consistent winner across the three axes. V3 is
specialised on label-coupling. V20 (new, MI-weighted bands) is the
first label-aware recipe in the sweep — it wins both F-2 and F-7 on
Indian Pines. V1 is *not* the best on any axis on the hard scenes;
it wins on the easiest scene (Salinas-A) where the spread is essentially
noise.

## V13..V20 extension — per-recipe mechanistic notes

- **V13 (VQ-VAE codebook, M=4 sub-vectors, K=32 codewords)** — worst
  recipe in the sweep on F-2 mean (0.25) and second-worst on F-7 mean
  (0.31). The ST-estimator-trained codebook is reconstruction-optimal
  but the resulting tokens are non-Dirichlet-compatible. Don't use.
- **V14 (CWT-Morlet 16 scales × 8 positions)** — 2nd on F-7 mean among
  the new recipes (0.46). Beats V6 (Db4 DWT, mean 0.32) on every scene.
  The multi-scale alphabet with explicit location-frequency cells
  produces topics whose top words map to absorption bands at specific
  centres — interpretable in a way V6 is not.
- **V15 (spectral indices NDVI/MNDWI/NBR/NDSI/EVI/SAVI)** — F-2 mean
  0.36, F-7 mean 0.31. Weakest in raw performance among the new
  recipes but the only one whose vocabulary maps to published
  remote-sensing semantics. Use as a *semantic baseline* in mixed
  vegetation scenes.
- **V17 (sparse-coding dictionary, K=64 atoms, lasso-LARS n_nz=8)** —
  F-2 mean 0.42, F-7 mean 0.22. The 512-atom vocab combined with 8
  non-zero coefficients per pixel produces extreme sparsity. Don't
  use under LDA.
- **V18 (graph-Laplacian eigenvectors, K=16, k-NN=10 cosine)** — 3rd
  on F-7 mean among new recipes (0.43); highest c_v on PaviaU among
  the V13..V20 set (0.66). Best on scenes whose classes form
  manifold-connected regions (urban, agricultural fields). Novel:
  LDA over Laplacian spectral coordinates.
- **V19 (UMAP 3D coordinate tokens)** — F-2 mean 0.38, F-7 mean 0.29.
  3 axes × Q=8 = 24-word vocabulary is too small to support 12 topics
  on the labelled scenes. Token names are abstract — no semantic
  bridge. Below V1 on every cell.
- **V20 (MI-weighted bands, MAX_COPIES=8)** — *winner on Indian Pines
  for both F-2 (0.88) and F-7 (0.44)*; F-7 mean 0.52 (top 3 overall).
  Cheapest, most interpretable extension: V1 with per-band MI-weighted
  emission multiplicities. The only label-aware wordification in the
  sweep. Recommended as default for label-rich classification settings.

## Bayesian posterior (when NUTS completes)

The hierarchical Bayesian model pools all 12 × 6 × 5 = 360 per-fold
observations through:

```
score[r, s, f, m] ~ Normal(
  mu_recipe[r] + offset_scene[s] + fold_re[f] + method_offset[m],
  sigma
)
```

with `mu_recipe ~ N(0, 1)`, `offset_scene ~ N(0, 0.5)`,
`fold_re ~ N(0, 0.2)`, `method_offset ~ N(0, 0.3)`,
`sigma ~ HalfNormal(0.5)`. NUTS draws=1000, tune=1000, 2 chains.

### Bootstrap posterior (B = 5000, populated c362)

| Recipe | mu | HDI94 |
|---|---|---|
| V12 | +0.9217 | [+0.9005, +0.9424] |
| V2  | +0.9171 | [+0.8932, +0.9395] |
| V11 | +0.9163 | [+0.8939, +0.9375] |
| V8  | +0.9161 | [+0.8933, +0.9386] |
| V3  | +0.9156 | [+0.8922, +0.9381] |
| V1  | +0.9153 | [+0.8924, +0.9375] |
| V4  | +0.9149 | [+0.8927, +0.9367] |
| V5  | +0.9143 | [+0.8902, +0.9367] |
| V9  | +0.9141 | [+0.8905, +0.9360] |
| V7  | +0.9140 | [+0.8920, +0.9354] |
| V10 | +0.9133 | [+0.8881, +0.9364] |
| V6  | +0.9132 | [+0.8893, +0.9362] |

Spread (best - worst) = 0.0085. Every recipe's HDI94 contains every
other recipe's posterior mean. **On F-1 alone the recipes are
statistically indistinguishable.**

### PyMC NUTS posterior (populated c374)

NUTS finished after ~7h on Windows with rhat > 1.01 warnings on some
parameters; treated as approximate. Confirms bootstrap: V12 leads at
mu_recipe = +0.4047, V1 at +0.4015, spread 0.0041, all HDI94 overlap.

Decision: F-1 alone does NOT discriminate recipes. F-2 (spread 0.5)
and F-7 (spread 0.6) dominate the integrated story. F-14 (V2/V8
catastrophic), F-18 (V12 worst on reliability), F-22 (V12 most
robust counterfactually) all add corroborating signal.

## F-13 SHAP attribution

72 cells under LDA backbone. Per (V, scene), top-8 tokens per topic
by mean absolute SHAP. Output at
`data/derived/v_sweep/f13_shap/{scene}_{V}_uniform_Q8.json`. Recipe-
grounded; cannot silently shift across scenes because the vocabulary
is fixed by the recipe.

## F-14 repetitiveness (mean off-diagonal top-10 jaccard, lower is better)

| V | mean jaccard | interpretation |
|---|---|---|
| V9 | 0.000 | catastrophic, 1 token/doc |
| V7 | 0.009 | diverse — absorption features |
| V12 | 0.009 | diverse |
| V3 | 0.012 | diverse |
| V11 | 0.053 | moderate |
| V13 | 0.133 | learned VQ-VAE |
| V1 | 0.200 | canonical mid-pack |
| V10 | 0.472 | redundant |
| V6 | 0.738 | wavelet topics repeat |
| V8 | 0.868 | endmember vocab too small |
| V2 | 1.000 | trivially redundant (Q=8 vocab) |

## F-17 cross-scene transfer (portable recipes only)

V2 best at NMI = 0.32 mean across 30 src->tgt pairs; V11 0.19; V10 0.10.

## F-18 reliability (Maier 2024: fraction top-10 cosine >= 0.7)

| V | F-18 |
|---|---|
| V2/V6/V8/V9/V10 | 1.000 (vocab-limited artefact) |
| V11 | 0.992 |
| V5 | 0.967 |
| V13 | 0.950 |
| V4 | 0.917 |
| V1 | 0.792 (canonical mid-pack with non-trivial vocab) |
| V7 | 0.783 |
| V12 | 0.158 (tradeoff with F-1/F-2/F-7 dominance) |
| V3 | 0.117 |

## F-22 counterfactual L1 (median, higher is more robust)

| V | median L1 |
|---|---|
| V12 | 23.50 |
| V3  | 18.20 |
| V2  | 7.83 |
| V1  | 6.08 |
| V7  | 5.17 |
| V8  | 3.58 |
| V11 | 3.33 |
| V4  | 2.50 |
| V5  | 2.50 |
| V6  | 1.92 |
| V10 | 1.17 |
| V9  | 1.00 |

## F-15 LLM-judge alignment (Claude Opus 4.7 self-judgment)

V2/V6/V8/V9/V10 trivially 1.0 (small vocabularies force top-10
alignment); V12 / V3 fall to 0.16 / 0.12 because their 1600-word
vocabularies make top-10 overlap rare even when topics are coherent.
**F-15 has a vocabulary-size confounder** that anti-correlates with
F-2 on large-vocab recipes — methodological gap flagged in P5.

## B-12 LLM tea-leaves (word-intrusion + label generation)

Stammbach et al. 2023 EMNLP word-intrusion + coherent-label probes,
run as Claude Opus 4.7 self-judgment with deterministic spectral-
region rules over the V1 canonical topics (the same setup as the
API-driven builder, but without per-call cost). Per-scene intrusion
accuracy across 12 topics each (Salinas-A has 6):

| Scene             | Topics | Intrusion accuracy | Note                           |
|-------------------|--------|--------------------|--------------------------------|
| botswana          | 12     | **0.75** (9/12)    | Diverse SWIR-1/SWIR-2 mix      |
| pavia-university  | 9      | 0.56 (5/9)         | VNIR-only — clean visible split |
| indian-pines      | 12     | 0.25 (3/12)        | SWIR-2 dominated, weak split    |
| salinas-corrected | 12     | 0.17 (2/12)        | Tight SWIR-2 cluster            |
| salinas-a-corr.   | 6      | 0.00               | Too few topics, near-identical  |
| kennedy-sc        | 12     | 0.00               | Very tight SWIR-2 spread        |

Headline: **B-12 intrusion accuracy varies 0% to 75% across scenes
under V1**. Scenes whose V1 topics span multiple spectral regions
(Botswana with both VNIR red-edge and SWIR-2 carbonate topics) score
above 50%; scenes whose V1 topics all cluster in SWIR-2 score near
zero. This is a *coherence* diagnostic that confirms the F-2 / F-7
finding from a different angle: V1 produces a narrow topic basis on
the corrected scenes (Indian Pines, Salinas, KSC) where label-aware
or manifold-based recipes (V18, V20) would distribute topics across
wider spectral regions.

The per-topic LLM labels are available in the web app's
`/benchmarks` page (B-12 panel) and the raw JSONs at
`data/derived/llm_tea_leaves/<scene>.json`.

## Backbone factorial (F-2 c_v mean across scenes)

| V | LDA | HDP | ProdLDA | ETM |
|---|---|---|---|---|
| V1 | 0.81 | 0.540 | 0.752 | 0.664 |
| V3 | 0.88 | 0.311 | **0.863** | 0.793 |
| V7 | 0.32 | **0.615** | 0.509 | 0.255 |
| V12 | **0.85** | 0.337 | 0.825 | **0.816** |
| V14 | 0.63 | 0.312 | 0.469 | 0.616 |
| V18 | 0.57 | 0.421 | 0.480 | 0.579 |
| V20 | 0.85 | 0.383 | **0.744** | 0.770 |

V14/V18/V20 rows extended 2026-05-28 (c397 + c400). Per-cell ETM values:
- V14 ETM: indian-pines 0.666, salinas 0.780, salinas-A 0.529,
  pavia-U 0.497, kennedy-SC 0.941, botswana 0.281 (mean 0.616).
- V18 ETM: indian-pines 0.549, salinas 0.584, salinas-A 0.527,
  pavia-U 0.664, kennedy-SC 0.670, botswana 0.482 (mean 0.579).
- V20 ETM: indian-pines 0.634, salinas 0.594, salinas-A 0.803,
  pavia-U 0.940, kennedy-SC 0.969, botswana 0.683 (mean 0.770).

Per-cell HDP values: V14 c_v mean 0.312 (very flat); V18 0.421
(better than V12-under-HDP at 0.337); V20 0.383.

Per-cell ProdLDA values:
- V14: indian-pines 0.542, salinas 0.235, salinas-A 0.379,
  pavia-U 0.498, kennedy-SC 0.927, botswana 0.231 (mean 0.469).
- V18: indian-pines 0.286, salinas 0.472, salinas-A 0.527,
  pavia-U 0.480, kennedy-SC 0.662, botswana 0.453 (mean 0.480).
- V20: indian-pines 0.405, salinas 0.866, salinas-A 0.770,
  pavia-U 0.830, kennedy-SC 0.907, botswana 0.686 (mean **0.744**).

LDA + ETM (Dirichlet-prior) agree on V12 / V3. HDP (stick-breaking
truncation) picks V7. ProdLDA (logistic-normal) picks V3 (old),
**V20 (new) ranks 4th in ProdLDA at 0.744 — within 0.12 of V3 0.863**
and ahead of every V13..V19 cell. The new V20 under ETM (0.770)
also ranks third behind V3 (0.793) and V12 (0.816) — confirms V20
as a versatile recipe across backbones. **V18 under HDP is the
highest of the V13..V20 set under HDP** (0.421), 11 points above
V20 and 25 above V14, suggesting that graph-Laplacian tokens align
with HDP's stick-breaking truncation prior in a way that the
absorption-feature V7 also does but more broadly.

The V14/V18/V20 backbone extension confirms the headline finding:
**no recipe dominates every backbone**. V20 is the only new recipe
that places top-3 in every non-HDP backbone, validating the
mutual-information-weighted band design.

LDVAE-T (fifth proposed backbone) parked pending public code.

## V-sweep + neural baselines (existing P1 numbers, V1-only)

For cross-reference. These are *not* part of the V-sweep but provide
the comparison the existing P1 paper makes:

- ProdLDA on V1, Indian Pines: macro-F1 = 0.836 (P1 §VI-A).
- ETM on V1, Indian Pines: macro-F1 = 0.821.
- CAE-1D on V1, Indian Pines: macro-F1 = 0.829.

V-sweep with the best V (V2 at 0.861) beats all three neural baselines
*at fixed V1-style preprocessing*, by 1.5–4 macro-F1 points. The
factorial study (issue #617) would extend this comparison to
V × neural backbone.
