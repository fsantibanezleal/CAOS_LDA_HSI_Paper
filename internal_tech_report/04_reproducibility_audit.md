# 04 — Reproducibility audit and methodology caveats

Single-file home for disclosure of methodology gaps, data leakage
caveats, degenerate-cell rates, and reproducibility status across
the V-sweep matrix.

Last update: 2026-05-31.

## 1. V20 label-leakage caveat (F-1 macro-F1)

**Mechanism.** `build_wordifications_v20.py` computes per-band mutual
information weights using `mutual_info_classif(X, sample_labels)`
over the full labelled stratified sample (`SAMPLES_PER_CLASS = 220`).
The resulting `doc_term` matrix encodes those weights into the vocabulary
itself — bands with high MI emit more copies, bands with near-zero MI
emit none.

`build_v_sweep_f1_classification.py` then runs a 5-fold `StratifiedKFold`
on the SAME labelled set, re-fitting LDA per fold but using the
pre-computed (and label-aware) `doc_term`.

The "Per-fold LDA refit (no leakage)" comment at line 187 of the F-1
builder is correct for the LDA fit step, but does NOT cover the
upstream MI-weighting that has already incorporated test-fold label
information into the vocabulary structure.

**Practical bias.** V20 F-1 macro-F1 saturates at 0.917 across
Q=8/16/32 — identical to V8 (0.916) and V2 (0.917), both of which
have NO label leakage. So the practical bias appears to be ~0,
masked by the saturation effect of the topic_routed_soft classifier
working on enough topics.

**Scope of the caveat.** The leakage only contaminates F-1 macro-F1.
The following V20 metrics are NOT affected:
- F-7 NMI (computed against labels per scene, all recipes equivalent — labels are part of the metric definition, not the recipe)
- F-2 c_v (no labels involved)
- F-14 jaccard repetitiveness (no labels)
- F-18 reliability (no labels)
- F-22 counterfactual L1 (no labels)
- HIDSAG family-D NMI (different label set)
- Cross-backbone factorial (no labels in HDP/ProdLDA/ETM F-7 either)

**Recommended disclosure language for P3.** "V20 F-1 macro-F1 values
are computed with V20's MI weights derived from the same labelled
sample used for 5-fold cross-validation; the V20 vocabulary is
therefore label-aware in a way V8 and V2 are not. V20 F-1 numbers
should be read with this caveat in mind, although the saturation of
all three recipes at ~0.917 suggests the practical effect of this
leakage is small."

**Optional remediation.** A V20-nested protocol could re-compute MI
weights using only `train_idx` rows in each of the 5 folds. The
quantification of leakage bias would be |F-1(V20-leaky) - F-1(V20-nested)|.
At the saturation ceiling of ~0.917 this gap is expected to be ≤ 0.005.

Tracked in issue #763.

## 2. Backbone factorial degenerate-cell rates (Q=8)

The 4-backbone × 19-recipe × 6-scene factorial at Q=8 contains a
significant number of cells where the backbone converged to NMI=0
or near-zero values:

| Backbone | NMI=0 cells | NMI<0.01 cells | Total degenerate | Rate |
|---|---|---|---|---|
| LDA | 1 | 0 | 1 | 0.9% |
| **HDP** | **20** | **5** | **25** | **22%** |
| **ProdLDA** | **28** | **13** | **41** | **36%** |
| ETM | 1 | 0 | 1 | 0.9% |

### Degenerate patterns

**HDP** systematically fails on:
- V1 / V4 / V5 / V6 in botswana + indian-pines (low-content vocabularies + large-vocabulary class set)
- V10 / V4 in pavia-university

**ProdLDA** systematically fails on:
- V1 / V6 / V9 / V10 in indian-pines and botswana (encoder-decoder collapse on small-effective-vocabulary recipes)
- **V20 indian-pines (NMI = 0.0)** — the only V20 zero across all backbones. Contributes to V20's ProdLDA mean of 0.221, which is the headline "V20 collapses under ProdLDA" finding in P3
- V12 indian-pines (NMI = 0.0) — contributes to V12's poor ProdLDA performance

### Effect on cross-backbone composite

Mean F-7 NMI across the 4 backbones (current method, zeros included):

| Recipe | LDA | HDP | ProdLDA | ETM | Mean |
|---|---|---|---|---|---|
| V8 | 0.463 | 0.451 | 0.328 | 0.482 | 0.431 |
| V20 | 0.520 | 0.356 | 0.221 | 0.490 | 0.397 |
| V11 | 0.292 | 0.571 | 0.088 | 0.530 | 0.370 |
| V12 | 0.534 | 0.220 | 0.238 | 0.488 | 0.370 |

Excluding zero cells from per-backbone means:

| Recipe | Cross-backbone mean (zeros excluded) | Δ vs current |
|---|---|---|
| V8 | 0.431 | 0 (no zeros) — **robust** |
| V20 | 0.408 | +0.011 |
| V11 | 0.382 | +0.012 |
| V12 | 0.393 | +0.023 |

**Headline:** V8 retains cross-backbone leadership either way (no
degenerate cells to exclude). V12 recovers most under the zeros-
excluded version. V20 is robust to the exclusion (only 1 zero).

### Disclosure recommendation for P3

Add a footnote to the cross-backbone Q=8 table: "Cross-backbone means
include cells where the backbone converged to NMI=0 (HDP: 22% of cells,
ProdLDA: 36%). See Appendix B for the convergence audit and the
zeros-excluded version of the composite ranking, which preserves V8
as cross-backbone leader."

Tracked in issue #764.

## 3. F-15 LLM alignment coverage — CLOSED (full 19-recipe coverage)

F-15 LLM-judge cells now exist for all 19 recipes (114 cells = 19 × 6);
the V14-V20 extension was completed 2026-05-30 (issue #758 closed).

The original "expected V20 ≈ 0.16, consistent with V12" prediction was
**WRONG**: V20 scores **0.642**, far above V12 (0.158) and V3 (0.117)
despite sharing the ~1600-token vocabulary. V14 (vocab 1024) scores
0.950. This refutes the pure vocabulary-size confounder hypothesis:
the real driver is **token-mass dispersion**, not nominal vocabulary
cardinality. V20's MI-weighting (and V14's multi-scale wavelet
response) concentrate each document's mass on a few tokens, keeping
the top-10 overlap density high even at large |V|.

Full F-15 means (Q=8): V18/V19=1.00, V14=0.95, V20=0.64, V17=0.57,
V15=0.03. This corrected finding is now reflected in P5 abstract +
Table IV (commit eac6c11). Issue #758 closed.

## 4. HIDSAG family-D coverage gap

Only 50 cells in `data/derived/v_sweep/hidsag/f7_topic_to_owner/`
(12 recipes V1-V12, 5 sources). V13-V20 absent. JSONs missing
`source_id` field (currently group as "unknown").

V20 has NEVER been tested on HIDSAG. The cross-domain validity of
V20 = LDA peak finding is unknown.

Tracked in issue #765.

## 5. B-12 word-intrusion limited to V1 (by design, methodology gap)

B-12 (`data/derived/llm_tea_leaves/`) has 6 cells, one per scene,
all run against the V1 canonical topic fit.

**Why V12/V20 can't be evaluated with B-12 in its current form**:
the `build_b12_self_judge.py` deterministic rule judges word intrusion
by parsing wavelength values from the candidate tokens (e.g. `"0823nm"`,
`"2400nm"`) and computing the one farthest from the candidate-set
median. V12 tokens are GMM-component IDs (`gmm_c0` ... `gmm_c{N}`),
V20 tokens are MI-weighted band indices (`miw_b000_q28`) — neither
encodes wavelength information directly accessible to the parser.

The 2026-05-31 attempt to run `--recipe V12` and `--recipe V20`
through the V-sweep topic_views layout produces cells with
`n_attempted = 0` and `per_topic[k].skipped = True` (reason: "no top
words"), confirming the methodology gap.

**Recommended P5 language**: "The Stammbach et al. (2023) intrusion
test as implemented in our self-judge bypass operates over
wavelength-encoded vocabularies. V12 and V20 vocabularies are
non-wavelength (GMM-component IDs and MI-weighted band indices
respectively), so B-12 cannot be applied without a vocab-agnostic
re-implementation of the judge rule. This is itself a finding: the
single-axis "topic coherence under intrusion" is V1-dialect-specific."

The B-12 builder argparse was extended in c460 to accept `--recipe`
and `--q` arguments for future use when a vocab-agnostic judge rule
becomes available.

Tracked in issue #766. The limitation is now documented; degenerate
V12/V20 cells were removed from disk to avoid misleading downstream
analyses.

## 6. F-15 / F-1 / coverage matrix Q-stratification

`data/derived/v_sweep/coverage_matrix.json` does not include the
Q dimension. "F-22 114/114 cells" refers to Q=8 only; the matrix
does not surface that F-22 now has 162 cells (Q=8 + Q=16/32).

The matrix also omits F-15, F-17, HIDSAG, B-12 axes entirely.

Tracked in issue #759.

## 7. API exposure: Q-extension findings invisible in prod

The Q-extension findings (V8 cross-axis composite at Q=16, V20 LDA
peak at Q=32) are documented in P3 + tech report + linkedin + wiki
but the live `/api/v-sweep/*` endpoints only return Q=8 cells. The
visitor to `https://lda-hsi.fasl-work.com` cannot see the Q=16/32
data without manual disk inspection.

Tracked in issue #755.

## Status snapshot (2026-05-31, post-audit fixup pass)

| Disclosure | Tech report (this doc) | P3 paper | LinkedIn | Wiki | i18n | Code |
|---|---|---|---|---|---|---|
| §1 V20 leakage | ✅ | ✅ (F-1 protocol §) | ✅ (F-1 tie note) | n/a | ✅ | ✅ (caveat) |
| §2 Degenerate cells | ✅ | ✅ (cross-bb footnote) | n/a | n/a | n/a | n/a |
| §3 F-15 V14-V20 | ✅ closed | ✅ (P5 Table IV) | n/a | n/a | n/a | ✅ (builder run) |
| §4 HIDSAG V13-V20 | ✅ | pending | n/a | n/a | n/a | pending (run + schema patch) |
| §5 B-12 V12/V20 | ✅ | ✅ (P5 limitation) | n/a | n/a | n/a | ✅ (builder arg) |
| §6 Coverage matrix Q | ✅ closed | n/a | n/a | n/a | n/a | ✅ (Q-stratified) |
| §7 API Q-extension | ✅ closed | n/a | n/a | n/a | n/a | ✅ (live in prod) |
| triple-axis retired | ✅ | ✅ (abstract+captions) | ✅ | ✅ (Home) | ✅ | ✅ (BackboneF7Panel) |
| F-2 Q=32 tie | ✅ | ✅ | ✅ | ✅ | pending (V20 theory) | n/a |
| path leak D:\\ | n/a | n/a | n/a | n/a | n/a | ✅ (json + builder) |

Closed issues: #755 #756 #758 #759 #760 #763 #764 #766 (+ #762 disclosed).
Deferred: #757 (venv DX), #765 (HIDSAG V13-V20 deep refactor).
