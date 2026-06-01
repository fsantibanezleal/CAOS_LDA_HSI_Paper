# Design space — V1..V20 rationale, gaps, and resolutions

Covers the full nineteen-recipe sweep (V1–V15, V17–V20; V16 is a
scaffolded foundation-model slot, weights not vendored). Formal token
and metric definitions live in `equations/canonical.tex`; this file is
the design rationale and the audit trail of schematic-vs-code
discrepancies.

## The four axes of design freedom

Every wordification recipe is a map `Phi: R^B -> N^|V|` from a pixel
spectrum to a doc-term count vector (canonical `eq:quantiser` for the
shared uniform quantiser). The nineteen recipes span:

1. **Token alphabet / semantics** — what a token *means*:
   - *Intensity* — V1 band-frequency (`eq:v1`), V2 intensity-as-word,
     V3 joint (band, bin) (`eq:v3`), V10 band-group.
   - *Differentiated / multi-scale* — V4 first-derivative bin,
     V5 second-derivative bin, V6 Db4 wavelet level-4, V14 CWT-Morlet.
   - *Absorption / chemistry* — V7 absorption triplet, V8 NFINDR
     endmember-fraction (`eq:v8`), V15 spectral indices.
   - *Learnt codebook* — V11 product-quantisation, V12 GMM-token
     responsibilities (`eq:v12`), V13 VQ-VAE codebook, V17 sparse-coding
     dictionary atoms.
   - *Manifold* — V18 graph-Laplacian eigenvectors, V19 UMAP coords.
   - *Label-aware* — V20 MI-weighted bands (`eq:v20`), the only recipe
     that consults the label `y` when building the vocabulary.
2. **Spatial vs spectral** — pure spectral for everything except
   V9 (Felzenszwalb region + SAM), the one spatial-aware recipe.
3. **Local vs global vocabulary** — local per-band (V1, V3, V4, V5,
   V12, V20); global band-agnostic (V2, V11, V13, V17); coarse
   group-level (V8, V10); manifold-coordinate (V18, V19); sparse
   event-level (V7, V9).
4. **Document length** — dense ~`B` tokens/doc (V1–V6, V12, V14, V18,
   V20); coarse 3–10 (V8, V10, V11, V13, V15, V17, V19); sparse `<= 6`
   (V7, V9).

## Recipe families (taxonomy used in P3 figures)

| Family | Recipes | Defining idea |
|---|---|---|
| Pure spectral / intensity | V1, V2, V3 | quantised band intensities |
| Differentiated / wavelet | V4, V5, V6, V14 | derivative / multi-scale response |
| Absorption / chemistry | V7, V8, V15 | physical absorption + unmixing |
| Learnt codebook | V11, V12, V13, V17 | clustered / coded subspace |
| Manifold | V18, V19 | graph / embedding coordinates |
| Spatial | V9, V10 | region / band-group aggregation |
| Label-aware | V20 | per-band mutual information with `y` |
| Foundation (scaffold) | V16 | HyperSIGMA embedding — not vendored |

## Discrepancies between UI/paper schematics and code (RESOLVED)

Three discrepancies caught during the original V1–V12 code audit. The
manuscripts and the web app now state the *actual implementation*; the
app/wiki copy was corrected (2026-05-31) to match.

### V3 — "concat trigram" → joint (band, bin)

- **Original UI label**: "concat trigram" — implied a 3-band context
  window `(bin(x_{b-1}), bin(x_b), bin(x_{b+1}))`.
- **Actual implementation** (`build_wordifications.py`): joint
  `(band, bin)` Cartesian product, vocab `B x Q`, NO context window
  (`eq:v3`).
- **Resolution**: P3 + app + wiki state the actual implementation
  (corrected in `Representations.tsx` 2026-05-31). The trigram variant
  is parked as future work.
- **Why it matters**: V3's F-7 strength comes from the larger `B x Q`
  vocabulary, not from any local-shape semantics.

### V9 — "SLIC-500 superpixel" → Felzenszwalb region + SAM

- **Original UI label**: "Aggregate pixels within a SLIC-500
  superpixel; emit V1 tokens on the region-mean spectrum."
- **Actual implementation** (`build_wordifications_v6plus.py`):
  precomputed Felzenszwalb segmentation; per-pixel spectral-angle
  distance to the region mean; one token `(region_id, SAM_bin)`. No
  SLIC, no aggregation.
- **Resolution**: P3 + app + wiki state Felzenszwalb + SAM (corrected
  in `Representations.tsx` 2026-05-31).
- **Why it matters**: V9 has one token per document by construction;
  the K-policy forced K=4; its F-1 is a lower bound, not a ceiling for
  spatial-aware wordifications.

### V11 — nanopq seed unfixed

- **Symptom**: `nanopq.PQ(M=4, Ks=Q)` invoked without an explicit
  `random_state`; the k-means codebook fit can drift across versions.
- **Resolution**: V11 results are tagged "approximate" until the seed
  is pinned. (V11 is nonetheless the HDP/ETM backbone-specialist; see
  P4.)
- **Why it matters**: do not use V11 numbers for reviewer rebuttal
  until the seed is pinned and the cell re-evaluated.

## The V13–V20 extension (no longer "future")

The original design-space audit listed V13–V17 as deferred. They were
subsequently implemented and are full members of the nineteen-recipe
sweep. What each added:

| Recipe | What it added | Sweep verdict |
|---|---|---|
| V13 | VQ-VAE learnt codebook (deterministic given the trained quantiser) | underperforms on F-7; moderate reliability |
| V14 | CWT-Morlet multi-scale tokens | mid-pack; F-7 peaks at Q=16 |
| V15 | spectral indices (NDVI-style ratios) | low F-15 (0.03); narrow vocabulary |
| V17 | sparse-coding dictionary atoms | mid-pack on F-7 / F-15 |
| V18 | k-NN graph-Laplacian eigenvectors | strongest reseed reliability among non-trivial vocabularies; F-7 ~0.43 |
| V19 | UMAP 3-coordinate bins | abstract tokens; F-7 0.21–0.36, very low F-2 (decouples F-2 from F-7) |
| V20 | per-band MI-weighting of the V3 alphabet (`eq:v20`) | LDA + ETM Q-scaling peak; only label-aware recipe |
| V16 | HyperSIGMA foundation-model embedding | scaffolded only; weights not vendored |

Genuinely still-future variants: V3-trigram (true 3-band context),
V9-SLIC, pixel-pair contrastive tokens, Mahalanobis-bin tokens.

## Decision: which recipe is "canonical" depends on the goal

The P1 choice of **V1** as the reproducibility canonical stands, on
three grounds: deterministic (no learned components), dense (supports
K up to `n_classes` without document-length degeneration), and
identifiable (every token is band `b` at intensity bin `q`).

The V-sweep refines, not invalidates, that choice. The corrected
findings (single source of truth: `03_v_sweep_results.md`):

- **V1** — reproducibility canonical. Never the *most* label-aligned
  recipe, but the most reliable with an informative vocabulary.
- **V12** (GMM-token) — leads LDA at Q=8 on F-2 and F-7; informative
  but seed-sensitive (low F-18). F-1 is a non-discriminating tie.
- **V20** (MI-weighted) — LDA + ETM Q-scaling peak: wins F-2 + F-7 on
  Indian Pines, F-7 ranking inverts to a robust lead over V12 at Q=32,
  most counterfactually robust basis at Q=8 (F-22), lowest F-14 among
  informative-vocabulary recipes. Pays in F-18 reliability (~0.45).
- **V8** (NFINDR endmember) — the cross-axis composite leader: top of
  the cross-backbone F-7 mean (0.431) AND F-18 reliability ~0.96 stable
  across Q. Recommended when the backbone is uncertain or
  reproducibility matters; its reliability is geometric (convex hull),
  not a vocabulary-size artefact.
- **V11** (product quantisation) — backbone-specialist: wins HDP and
  ETM outright but collapses under LDA / ProdLDA.

Recommendation matrix: V1 for new reproducibility studies; V20 when LDA
is fixed and `Q >= 16` is affordable; V8 when the topic-model backbone
is uncertain or reseed reliability is required; V12 for coherence-driven
LDA-only work at Q=8.
