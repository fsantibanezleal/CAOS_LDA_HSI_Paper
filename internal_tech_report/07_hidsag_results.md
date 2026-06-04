# 07 — HIDSAG cross-domain results (mineral region-document corpus)

Internal technical report section covering the wordification-recipe sweep
on the HIDSAG mineral corpus — the cross-domain counterpart to the
labelled-scene V-sweep in `03_v_sweep_results.md`. Numbers are produced by
`build_v_sweep_hidsag.py` / `build_v_sweep_hidsag_f7.py` (repo
`CAOS_LDA_HSI`) into the derived JSON cells under
`data/derived/v_sweep/hidsag/`.

## Corpus

HIDSAG documents are region-aggregated reflectance spectra
(`data/derived/core/hidsag_region_documents.npz`), one row per document,
split into five mineral subsets: GEOCHEM, GEOMET, MINERAL1, MINERAL2,
PORPHYRY. There is no per-document mineral class label, so the
labelled-scene F-1/F-7 do not apply directly; instead we report:

- **F-2 coherence** (`f2_c_v`, `f2_c_npmi`, `f2_u_mass`) on the top-10
  words per topic — `build_v_sweep_hidsag.py` →
  `data/derived/v_sweep/hidsag/topic_views/`.
- **F-7 owner-NMI** — NMI of topic-argmax against the per-document
  `sample_owner` id — `build_v_sweep_hidsag_f7.py` →
  `data/derived/v_sweep/hidsag/f7_topic_to_owner/`.

Each cell carries a `source_id` field equal to its subset code (e.g.
`"GEOCHEM"`), mirroring the labelled-scene `scene_id` convention (added
under issue #765; all 150 cells backfilled).

## Recipe coverage

HIDSAG covers **15 recipes**: **V1-V7, V10-V14, V17-V19**. All are
unsupervised and run directly on the `[D, B]` region-document spectra
matrix.

Not covered, with reasons:

| Recipe | Status | Reason |
|---|---|---|
| V8 (endmember NFINDR) | precompute-blocked | needs scene-level endmember precompute that does not exist for HIDSAG |
| V9 (region-SAM Felzenszwalb) | precompute-blocked | needs scene-level segmentation precompute that does not exist for HIDSAG |
| V15 (spectral indices) | out of scope | named-band indices need wavelength-specific bands; HIDSAG documents are region aggregates over a synthetic wavelength grid |
| V16 (foundation-model scaffold) | out of scope | needs external pretrained weights |
| V20 (MI-weighted, label-aware) | out of scope | requires a per-document mineral class label HIDSAG region documents do not carry (only a `sample_owner` provenance id) |

V13/V14/V17/V18/V19 were added to the HIDSAG sweep under issue #765;
prior to that the HIDSAG corpus covered only V1-V7, V10-V12 (10 recipes —
not "12", since V8/V9 are skipped).

V13 (VQ-VAE codebook, M=4, K=32), V14 (CWT-Morlet, S=16 scales,
P=8 position buckets), V17 (sparse-coding dictionary, 64 atoms),
V18 (graph-Laplacian eigenvectors, 16 eigenvectors over a k-NN graph)
and V19 (UMAP, 3D coordinates) are re-implemented inline in
`build_v_sweep_hidsag.py` on the region-document spectra (the standalone
`build_wordifications_v*.py` builders operate on labelled scene cubes).

**V18 small-subset guard:** the k-NN graph degree and the eigenvector
count are both capped to `k = min(16, D - 2)`, so the small MINERAL2
subset (D = 180) and any future smaller subset stay within bounds.

## F-7 owner-NMI leaders (per subset)

Owner-NMI is the strongest signal HIDSAG offers without class labels:
how much each recipe's topics recover sample membership. Computed from
`data/derived/v_sweep/hidsag/f7_topic_to_owner/` over all 15 recipes ×
5 subsets (75 cells).

Per-subset owner-NMI leader (across all 15 recipes):

| Subset | n_owners | Leader | owner-NMI |
|---|---|---|---|
| GEOCHEM | 28 | V2 | 0.051 |
| GEOMET | 146 | V12 | 0.239 |
| MINERAL1 | 99 | **V18** | 0.270 |
| MINERAL2 | 20 | V1 | 0.338 |
| PORPHYRY | 28 | V12 | 0.379 |

Mean owner-NMI per recipe (n=5 subsets each), highest first:

| Recipe | mean owner-NMI |
|---|---|
| V18 (graph-Laplacian) | 0.204 |
| V12 (GMM) | 0.200 |
| V2 (magnitude phrase) | 0.198 |
| V1 (band frequency) | 0.177 |
| V11 | 0.157 |
| V19 (UMAP) | 0.156 |
| V5 | 0.124 |
| V3 | 0.113 |
| V4 | 0.111 |
| V7 (absorption triplet) | 0.109 |
| V17 (sparse coding) | 0.106 |
| V10 | 0.092 |
| V14 (CWT-Morlet) | 0.060 |
| V13 (VQ-VAE) | 0.021 |
| V6 (wavelet) | 0.019 |

Notes on the newly-ported recipes (#765): **V18 (graph-Laplacian) is the
strongest of the five and the best recipe overall on MINERAL1**; V19
(UMAP) is mid-pack; V17 (sparse coding) is near V7; V14 (CWT) and V13
(VQ-VAE) sit at the bottom — V13's single dominant codebook column tends
to collapse topics (mean owner-NMI ≈ 0.02), so it underperforms the
hand-crafted quantisers on this corpus. All 25 new cells passed the
finite-metric gate (finite c_v and finite owner-NMI), independently
re-verified (0 parse / 0 missing-source_id / 0 non-finite across 150
cells).

## Cross-domain note vs the labelled scenes

On the labelled HSI scenes (03), V8 (NFINDR endmember) is the
cross-backbone leader and V20 (MI-weighted, label-aware) the LDA peak —
but neither is available here (V8 precompute-blocked, V20 needs a class
label HIDSAG lacks). Among the recipes that DO transfer to the unlabelled
mineral corpus, the manifold recipe **V18** and the soft-cluster recipe
**V12** lead owner-recovery — a different winner profile from the
labelled-scene F-7, which is itself the cross-domain finding: recipe
optimality is corpus-dependent, not universal.
