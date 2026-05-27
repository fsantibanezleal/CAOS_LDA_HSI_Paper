# Deferred axes — F-13 through F-18 candidates

Six F-axis extensions identified by the 2026-05-26 literature search
that are not in the current F-1..F-12 framework. Each is independently
publishable as a follow-up and tracked as its own GitHub issue.

## F-13 — SHAP/LIME over wordified pixels

**What**: pixel-level SHAP attributions of topic assignments. The
features are recipe-specific tokens (V1: bands; V7: absorption
features; V9: regions; etc.).

**Why**: there is no published LIME / SHAP for LDA-on-HSI. Directly
defends the "interpretable" claim of P1 against transformer attention
maps.

**Effort**: medium (kernel-SHAP variant adapted to topic-mixture model
output). Existing SHAP library handles the explainer; need a custom
predict-proba wrapper.

**Issue**: [#615](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/615).

## F-14 — repetitiveness (**SHIPPED 2026-05-27 c366**)

**What**: mean off-diagonal jaccard of top-10 word sets across topics.
Low = diverse topics; high = redundant topics (LDA's common failure
mode at large K).

**Result**: per-recipe mean across 6 labelled scenes:
  - V9 0.000, V7 0.009, V12 0.009, V3 0.012, V11 0.053 (most diverse)
  - V1 0.200 (current canonical, mid-pack)
  - V4 0.218, V5 0.221
  - V10 0.472 (moderate)
  - V6 0.738, V8 0.868 (high; vocab too small for K=12)
  - V2 1.000 (Q=8 vocab, K=12 → trivially complete overlap)

**Status**: SHIPPED. `build_v_sweep_f14_repetitiveness.py`. Results
under `data/derived/v_sweep/f14_repetitiveness/`.

**Issue**: [#616](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/616).

## F-15 — topic-document alignment (LLM-judge)

**What**: probability that an LLM, shown a document's top-3 tokens and
the topic-word list, agrees the document belongs to that topic. Forces
the topic semantic to be coherent enough for an LLM to label.

**Why**: same paper as F-14. Closes a reviewer-visible gap on whether
LDA topics are semantically meaningful, not just statistically
identifiable.

**Effort**: medium (LLM cost: 12 V × 6 scenes × 50 docs/scene =
3600 calls per backbone).

**Issue**: [#616](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/616).

## F-16 — model-selection adequacy (HDP)

**What**: drop fixed K; fit HDP per (V, scene); report inferred K vs.
ground-truth class count. Low absolute error means the topic count
emerges naturally from the data.

**Why**: no HDP-on-HSI paper exists. Natural follow-up to the K-policy
discussion in [02_k_policy.md](02_k_policy.md).

**Effort**: medium-high. HDP inference is more expensive than online-VB
LDA; the per-V LDA refit-per-fold protocol may need adjustment.

**Issue**: [#621](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/621).

## F-17 — cross-scene transfer (**SHIPPED 2026-05-27 c366**)

**What**: fit phi on scene S1; transform pixels of scene S2; compute
F-7 NMI on S2. Tests vocabulary reusability across scenes.

**Result**: only vocab-portable recipes (V2, V10, V11) can be evaluated
without resampling to a common band grid. Per-recipe mean transfer NMI
across 30 src→tgt pairs:
  - V2 0.3241 (band-agnostic q-bins generalise best)
  - V11 0.1881
  - V10 0.0972 (3-group too coarse)

V1/V3/V4/V5/V6/V12 deferred until a common-grid resampler is added.

**Status**: SHIPPED. `build_v_sweep_f17_cross_scene.py`. Results
under `data/derived/v_sweep/f17_cross_scene/`.

**Issue**: [#623](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/623).

## F-18 — test-retest reliability beyond seed stability (**SHIPPED 2026-05-27 c366**)

**What**: Maier 2024 reliability protocol — top-N word indicator cosine
similarity > 0.7 proportion across reseed runs. Augments F-3 (which
uses ARI on argmax dominant topic).

**Status**: Builder shipped at `data-pipeline/build_v_sweep_f18_reliability.py`
in CAOS_LDA_HSI. N_SEEDS = 5 (random_state = 42,43,44,45,46), TOP_N = 10,
Hungarian alignment across seed pairs. Output thresholds: 0.5, 0.7.
Running in background as of 2026-05-27. Numbers will populate the
per-V reliability column in P3 supplementary once complete.

**Issue**: [#624](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/624) — implementation done; results pending.

## Cost / benefit

| Axis | Effort | Novelty | Reviewer-shield value |
|---|---|---|---|
| F-13 | medium | very high | very high (interpretability claim) |
| F-14 | low | low | medium (cheap diagnostic) |
| F-15 | medium | medium | high (semantic coherence) |
| F-16 | medium-high | high | medium |
| F-17 | low | medium | high (under-explored) |
| F-18 | low | low | medium (reviewer ask) |

Recommended order:
1. **F-13** (highest interpretability ROI) — earmark for P5.
2. **F-14 + F-18** (cheap; lump into P3's "extension" section).
3. **F-17** (cheap; lump into P3).
4. **F-15** (LLM cost; defer to P5).
5. **F-16** (HDP; defer to P4 / factorial).
