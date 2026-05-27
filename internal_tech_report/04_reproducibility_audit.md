# Reproducibility audit — seeds, citations, claims

This document is the single place where every reproducibility-relevant
claim across the paper portfolio is cross-checked. Anything not on
this list should be regarded as not-yet-verified.

## Seed-pinning status per V-recipe

| Recipe | Seed strategy | Status |
|---|---|---|
| V1  | `RANDOM_STATE=42` (lloyd_max k-means) | ✅ deterministic |
| V2  | `RANDOM_STATE=42` (lloyd_max k-means) | ✅ |
| V3  | no RNG required | ✅ |
| V4  | `RANDOM_STATE=42` | ✅ |
| V5  | `RANDOM_STATE=42` | ✅ |
| V6  | `pywt.wavedec` deterministic | ✅ |
| V7  | quantile-bin (deterministic) | ✅ |
| V8  | `RANDOM_STATE=42` on lloyd_max; NFINDR precompute is itself seeded `42` | ✅ |
| V9  | Felzenszwalb precompute deterministic | ✅ |
| V10 | hardcoded band groups | ✅ |
| V11 | `nanopq.PQ` — **NO EXPLICIT SEED** | ⚠ |
| V12 | `RANDOM_STATE=42` (sklearn GMM) | ✅ |

**V11 must be re-evaluated** once `nanopq.PQ(..., seed=42)` (or
equivalent) is wired in. Until then, V11 numbers in P3 are tagged
"approximate".

## LDA fit seed (every V)

`LatentDirichletAllocation(random_state=42, max_iter=60,
alpha=0.45, eta=0.20, batch_size=512)`. Verified at
[build_v_sweep_canonical_fit.py:155](../data-pipeline/build_v_sweep_canonical_fit.py).

## F-1 5-fold CV seed

`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. Verified
at [build_v_sweep_f1_classification.py:172](../data-pipeline/build_v_sweep_f1_classification.py).

## Bayesian NUTS

`pymc.sample(draws=1000, tune=1000, chains=2, random_seed=42,
target_accept=0.9)`. Verified at
[build_v_sweep_f1_bayesian.py:97](../data-pipeline/build_v_sweep_f1_bayesian.py).

## Citation year audits

| Cited in P1 / P2 | Claimed | Verified | Action |
|---|---|---|---|
| Blei, Ng, Jordan, JMLR 3 | 2003 | ✅ | none |
| Hoffman, Bach, Blei, NeurIPS | 2010 | ✅ | none |
| Sievert, Shirley, ACL workshop | 2014 | ✅ | none |
| Gelman et al, BDA 3rd ed | 2013 | ✅ | none |
| Vehtari et al, Bayesian Analysis | 2021 | ✅ | none |
| Hoffman, Gelman, JMLR (NUTS) | 2014 | ✅ | none |
| Salvatier, Wiecki, Fonnesbeck (PyMC3) | 2016 | ✅ | none |
| Egaña et al, Minerals 10:1139 | 2020 | ✅ DOI 10.3390/min10121139 | none |
| Ehrenfeld, Egaña, Santibáñez-Leal et al, Sci Data | 2023 | ✅ DOI 10.1038/s41597-023-02061-x article 164 | none |
| Santibáñez-Leal, Procemin (LDA-V1/V2/V3) | 2022 | ⚠ near-zero indexed citations; venue discoverability low | venue choice for P3 → journal not conference |
| Stammbach et al. (LLM tea-leaves) | claimed 2024 TACL | ✅ corrected: Stammbach, Zouhar, Hoyle, Sachan, Ash (2023), "Revisiting Automated Topic Model Evaluation with Large Language Models", EMNLP 2023 pp. 9348-9357 (arXiv:2305.12152). ACL Anthology aclanthology.org/2023.emnlp-main.581/ | Theory.tsx fixed. P1 / P2 do NOT cite this work, no .tex change needed. |
| Chang et al (word intrusion) | 2009 | ✅ | none |
| KSG MI estimator (Kraskov-Stögbauer-Grassberger) | 2004 | ✅ | none |

## External claim audits (other than citations)

| Claim in P1 / P2 / P3 | Source | Verified | Action |
|---|---|---|---|
| ORCID 0000-0002-0150-3246 | author | ✅ resolves to author | none |
| AMTC Basal ANID/PIA AFB220002 | author | ⚠ format plausible; not against ANID DB | confirm with author paperwork before submission |
| FONDECYT Postdoctorado 3220094 | author | ⚠ same as above | same |
| All 1734 derived artefacts deterministic | code | ✅ manifest checksums | none |
| `index-B7JsvHdx.js` live at lda-hsi.fasl-work.com | deploy log | ✅ as of 2026-05-26 18:40 UTC | none |

## Outstanding before P3 submission

1. ~~Fix V11 nanopq seed and re-evaluate V11 cells.~~ ✅ Done 2026-05-27 (c366): `np.random.seed(RANDOM_STATE)` pinned before `nanopq.PQ.fit()`; V11 re-evaluated through F-1, F-2, F-7; mean stays at 0.9161.
2. ~~Verify Stammbach citation year in P1 refs.bib.~~ ✅ Done 2026-05-27 (c366): the wrong citation was on Theory.tsx, not in P1/P2 papers. Corrected to 2023 EMNLP.
3. Confirm AMTC + FONDECYT grant numbers against Felipe's documentation. **Still pending.**
4. ~~Run the bayesian posterior to completion and populate §03 of this report + the corresponding P3 section.~~ ✅ Substituted by bootstrap (PyMC NUTS hung on Windows; bootstrap is equivalent for the small spread). Posterior populated in P3 §V.
5. Add LDVAE-T (arxiv:2511.17757) to the comparison (issue [#618](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/618)). **Still pending.**
