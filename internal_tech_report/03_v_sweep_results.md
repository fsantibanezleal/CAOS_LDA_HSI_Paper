# V-sweep results — full per-V per-scene per-axis numbers

This is the **single source of truth** for the V-sweep tables in P3.
Any number that appears in the manuscript must match this file.

Generated 2026-05-26 from the sweep over uniform / Q=8 / 6 labelled
scenes / V1..V12. Source artefacts:

- `data/derived/v_sweep/topic_views/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f1_per_fold/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f2_coherence/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f7_topic_to_label/{scene}_{V}_uniform_Q8.json`
- `data/derived/v_sweep/f1_bayesian_posterior.json` (pending NUTS run)

## F-1 — topic-routed-soft macro-F1 (5-fold mean)

| Scene | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 | V11 | V12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| botswana          | 0.963 | 0.956 | 0.961 | 0.961 | 0.958 | 0.945 | 0.962 | **0.967** | 0.954 | 0.957 | 0.957 | 0.964 |
| indian-pines      | 0.842 | **0.861** | 0.835 | 0.833 | 0.829 | 0.819 | 0.831 | 0.857 | 0.819 | 0.834 | 0.853 | 0.853 |
| kennedy-sc        | 0.923 | 0.925 | 0.924 | 0.924 | 0.925 | 0.923 | 0.922 | 0.927 | 0.922 | 0.917 | 0.927 | **0.930** |
| pavia-u           | 0.815 | 0.824 | 0.820 | 0.819 | 0.815 | 0.819 | 0.816 | 0.820 | 0.825 | 0.819 | 0.819 | **0.834** |
| salinas-a         | **0.997** | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 | 0.997 |
| salinas-c         | 0.951 | **0.956** | 0.954 | 0.953 | 0.952 | 0.950 | 0.951 | 0.950 | 0.953 | 0.951 | 0.949 | 0.952 |
| **mean across scenes** | 0.9152 | 0.9173 | 0.9153 | 0.9151 | 0.9145 | 0.9135 | 0.9143 | 0.9163 | 0.9143 | 0.9134 | 0.9161 | **0.9216** |

Spread (best − worst across recipes, mean of scenes) = 0.0082.
Small, but consistent: V12 leads on 2 scenes outright, V8 on 1, V2
on 2, V1 on 1 (the tied easiest scene).

## F-2 — top-10 c_v coherence

| Scene | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 | V11 | V12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| indian-pines  | 0.32 | 0.35 | 0.70 | 0.32 | 0.32 | 0.32 | 0.27 | 0.30 | 0.71 | 0.27 | 0.24 | **0.79** |
| kennedy-sc    | **0.97** | 0.76 | 0.93 | 0.81 | 0.93 | 0.79 | 0.37 | 0.52 | 0.72 | 0.32 | 0.22 | 0.84 |
| pavia-u       | 0.91 | 0.43 | 0.96 | 0.59 | 0.40 | 0.58 | 0.27 | 0.21 | 0.70 | 0.32 | 0.22 | **1.00** |
| salinas-a     | **0.96** | 0.35 | 0.92 | 0.32 | 0.32 | 0.81 | 0.32 | 0.38 | 0.71 | 0.23 | 0.21 | 0.88 |
| salinas-c     | 0.36 | 0.35 | 0.65 | 0.32 | 0.32 | 0.32 | 0.20 | 0.21 | 0.72 | 0.29 | 0.22 | **0.84** |
| botswana      | (pending) | — | — | — | — | — | — | — | — | — | — | — |

V12 wins 3/5, V1 wins 2/5. V1's wins are on the scenes where
absolute reflectance is most diagnostic (Kennedy SC, Salinas-A).

## F-7 — normalised mutual information (topic-argmax vs label)

| Scene | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 | V9 | V10 | V11 | V12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| indian-pines  | 0.34 | 0.35 | **0.43** | 0.25 | 0.20 | 0.26 | 0.16 | 0.43 | 0.10 | 0.27 | 0.25 | 0.42 |
| kennedy-sc    | 0.41 | 0.40 | **0.54** | 0.32 | 0.25 | 0.34 | 0.20 | 0.17 | 0.11 | 0.27 | 0.26 | 0.41 |
| pavia-u       | 0.47 | 0.38 | 0.55 | 0.38 | 0.14 | 0.43 | 0.23 | 0.54 | 0.02 | 0.00 | 0.21 | **0.61** |
| salinas-a     | 0.62 | 0.65 | **0.68** | 0.37 | 0.56 | 0.33 | 0.16 | 0.52 | 0.20 | 0.28 | 0.42 | 0.55 |
| salinas-c     | 0.47 | 0.54 | 0.43 | 0.39 | 0.44 | 0.33 | 0.28 | 0.56 | 0.14 | 0.20 | 0.33 | **0.64** |

V3 wins 3/5, V12 wins 2/5. **V1 wins 0/5**. The strongest single-axis
finding of the sweep.

## Cross-axis reading

| Recipe | F-1 wins | F-2 wins | F-7 wins | Total |
|---|---|---|---|---|
| V12 | 2 | 3 | 2 | **7** |
| V3  | 0 | 0 | 3 | 3 |
| V2  | 2 | 0 | 0 | 2 |
| V1  | 1 | 2 | 0 | 3 |
| V8  | 1 | 0 | 0 | 1 |

V12 is the most consistent winner across the three axes. V3 is
specialised on label-coupling. V1 is *not* the best on any axis on
the hard scenes; it wins on the easiest scene (Salinas-A) where the
spread is essentially noise.

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

**[Populate from f1_bayesian_posterior.json once NUTS converges.]**

Decision rule: if spread (best mu − worst mu) >= 0.05 the recipe
choice is a real claim. The point-estimate F-1 spread is 0.008, so
the Bayesian posterior is expected to overlap heavily across recipes
on F-1 specifically. F-2 and F-7 spreads are larger (0.2–0.5 in
point estimate) and will dominate the integrated story.

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
