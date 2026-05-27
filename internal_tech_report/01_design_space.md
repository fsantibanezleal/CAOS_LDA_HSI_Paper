# Design space — V1..V12 rationale, gaps, and resolutions

## The four axes of design freedom

The 12 recipes span:

1. **Token alphabet**: intensity (V1, V2, V10, V12), local derivative
   (V4, V5), multi-scale (V6 wavelet), absorption (V7), mixing
   fractions (V8), spatial (V9), encoded subspaces (V11).
2. **Spatial vs spectral**: pure spectral V1..V8, V10..V12;
   spatial-aware V9.
3. **Local vs global vocabulary**: local per-band (V1, V3, V4, V5, V12);
   global band-agnostic (V2, V11); coarse group-level (V10, V8); sparse
   event-level (V7, V9).
4. **Document length**: dense $B$ tokens/doc (V1, V2, V4, V5, V6, V12);
   coarse 3–10 (V8, V10, V11); sparse $\le 6$ (V7, V9).

## Discrepancies between UI/paper schematics and code (RESOLVED IN P3)

Three discrepancies were caught during the V-sweep code audit. They
are documented here for transparency; the P3 manuscript states the
*actual implementation*, not the original schematic.

### V3 — "concat trigram" → joint (band, bin)

- **Original UI label** (`frontend/src/pages/methodology/Representations.tsx:262`):
  "concat trigram" — implied a 3-band context window
  `(bin(x_{b-1}), bin(x_b), bin(x_{b+1}))`.
- **Actual implementation** (`data-pipeline/build_wordifications.py:173`):
  joint `(band, bin)` Cartesian product. Vocab size `B × Q`. NO
  context window.
- **Resolution**: P3 states the actual implementation. The trigram
  variant is parked as a future V13b for the factorial study (issue
  [#617](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/617)).
- **Why this matters**: V3 wins F-7 on 3 of 5 scenes precisely because
  of the larger vocab; if it were a trigram its vocabulary would be
  `B × Q^3` and the topic-label coupling would likely be different.
  The semantic claim "trigram captures local shape" does not apply.

### V9 — "SLIC-500 superpixel" → Felzenszwalb region + SAM

- **Original UI label** (`Representations.tsx:309`): "Aggregate pixels
  within a SLIC-500 superpixel; emit V1 tokens on the region-mean
  spectrum."
- **Actual implementation** (`build_wordifications_v6plus.py:219`):
  loads a precomputed Felzenszwalb segmentation, computes per-pixel
  spectral-angle distance to the region mean, emits one token
  `(region_id, SAM_bin)`. No SLIC. No aggregation.
- **Resolution**: P3 states Felzenszwalb + SAM. SLIC variant deferred
  to the factorial study.
- **Why this matters**: V9 has 1 token per document by construction;
  K-policy forced K=4 across scenes; the F-1 result is lower bound,
  not realistic ceiling for spatial-aware wordifications.

### V11 — nanopq seed unfixed

- **Symptom** (`build_wordifications_v7v11.py:260`): `nanopq.PQ(M=4,
  Ks=Q)` is invoked without an explicit `random_state`. nanopq's
  codebook fit uses k-means with a default seed; results may drift
  across nanopq versions.
- **Resolution**: V11 results in P3 are tagged "approximate" until the
  seed is pinned. Issue tracked in [#606](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/606)
  cycle backlog.
- **Why this matters**: V11 results should not be used as basis for
  reviewer rebuttal until the seed is pinned and the cell re-evaluated.

## Recipes NOT included in V1..V12 (and why)

These were considered during the design-space audit and explicitly
rejected for the *initial* sweep. They reappear in the factorial
study (issue #617) and the learned-wordification proposal
(issue #620).

| Candidate | Rationale for exclusion |
|---|---|
| V13a — trigram (true 3-band context) | High vocab cost; #617 covers. |
| V13b — VQ-VAE learned codebook | Requires training; not deterministic from raw spectra; #620 covers. |
| V14 — convolutional spectral tokens | Sliding 1D conv → tokens. Adjacent to V6 wavelet; deferred. |
| V15 — pixel-pair contrastive tokens | Two-pixel difference tokens. Outside the single-pixel-document framing of P1; future. |
| V16 — Mahalanobis-bin tokens | Bins along PCA principal axes. Useful comparator to V11. Future. |
| V17 — RBF-kernel-feature tokens | Random Fourier features quantized. Adjacent to V12 GMM but parametric. Future. |

## Decision: V1 remains the *reproducibility canonical* in P1 ↔ V12 is the
*best on coherence + label-alignment* per P3

The decision in P1 to use V1 was made on three grounds:
1. Deterministic — band-frequency tokens have no learned components.
2. Dense — supports K up to `n_classes` without document-length
   degeneration.
3. Identifiable — every token has a clear physical interpretation
   (band b at intensity bin q).

The V-sweep result does *not* invalidate this choice. V1 remains the
right reproducibility canonical. The P3 finding is narrower: across
F-2 coherence and F-7 topic-label NMI, V12 (GMM-token) and V3 (joint
band-bin) produce more coherent and more label-aligned topics. P3
recommends V1 as default for *new* reproducibility studies, V12 for
*coherence-driven* studies, V3 for *label-alignment-driven* studies.
