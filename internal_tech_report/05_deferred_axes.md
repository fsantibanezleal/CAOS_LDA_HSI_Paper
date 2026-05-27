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

## F-14 — repetitiveness (LLM-judge)

**What**: fraction of top-N words shared across topics (jaccard on
top-10 sets). Already partially in F-2's top-word jaccard matrix,
but presented as a coherence diagnostic rather than a quality metric.

**Why**: free axis from arxiv:2502.07352. Cheap to compute. Common
reviewer ask.

**Effort**: low (reuse f7's top-word lists).

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

## F-17 — cross-scene transfer of label-coupling

**What**: fit phi on scene S1; transform pixels of scene S2; compute
F-7 NMI on S2. Tests vocabulary reusability across scenes.

**Why**: every prior topic-models-on-HSI paper fits and evaluates on
the same scene. Cross-scene transfer is unanswered.

**Effort**: low (uses existing fits; just adds a transform pass).

**Issue**: [#623](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/623).

## F-18 — test-retest reliability beyond seed stability

**What**: Maier 2024 reliability protocol — top-word cosine-similarity
> 0.7 proportion across reseed runs, beyond the simple ARI of F-3.

**Why**: free axis from arxiv:2410.23186. Digital-humanities reviewers
expect it.

**Effort**: low (extends F-3's existing seed-sweep).

**Issue**: [#624](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/624).

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
