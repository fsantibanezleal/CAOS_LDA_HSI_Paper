# Paper portfolio — what each paper claims, depends on, and ships

Decision recorded 2026-05-26 after the literature search and full
F-2 + F-7 + F-1 sweep results. The literature search confirmed that:

- The V1..V12 head-to-head sweep is genuinely novel (no published
  wordification comparison for HSI).
- LDVAE-T (arxiv:2511.17757, Nov 2025) is the most recent direct
  competitor and must be benchmarked.
- HDP-on-HSI, ProdLDA-on-HSI, ETM-on-HSI, VQ-learned-wordification:
  all unfilled niches.

## Portfolio overview

| # | Working title | Target | Status | Depends on | Lead claim |
|---|---|---|---|---|---|
| P1 | Beyond accuracy: 12-axis framework (V1 only) | journal #1 | written | -- | Framework introduces 12 axes; V1 baseline. |
| P2 | Band-mask robustness diagnostic | conference companion to P1 | written | -- | F-5 deep-dive on V1; complements P1. |
| P3 | Which wordification matters? V-sweep on F-1, F-2, F-7 | journal #2 | scaffold + numbers | sweep done | V12 wins coherence + NMI most often; V1 is canonical not universal. |
| P4 | Backbone factorial: V × {LDA, HDP, ProdLDA, ETM, LDVAE} on F-1..F-12 | journal #3 | not started | #617, #621, #618 | Wordification matters as much as backbone choice. |
| P5 | Post-hoc interpretability of LDA-on-HSI (SHAP + counterfactual + F-13/F-14/F-15) | journal #4 | not started | #615, #616, #622 | LDA topics are SHAP-defensible against transformer attention. |
| P6 (internal) | V-sweep technical report | internal-only | this directory | -- | Single source of truth for design decisions + reproducibility audit. |

## P1 — status

Compiles (12 pages). Author block + ORCID + email fixed in c361
(2026-05-26). The "canonical" V1 framing is preserved; P3 extends
it rather than replacing it.

Open items before submission:
- Verify Stammbach citation year (see `04_reproducibility_audit.md`).
- Confirm AMTC + FONDECYT grant numbers.

## P2 — status

Same as P1 (compiles, author block fixed). Reports F-5 band-mask
diagnostic on V1 only. Stays narrow; do not retrofit V-sweep.

## P3 — status

Scaffold at `journal_v_sweep/tex/main.tex` (PR #35 on paper repo).
Full F-2 + F-7 tables populated. F-1 section pending Bayesian
posterior completion. Headline claim: V1 is not the best on F-7 on
any scene; V12 dominates F-2 and is competitive on F-7; V3 dominates
F-7 on landcover scenes.

Open items:
- Populate F-1 section once `f1_bayesian_posterior.json` lands.
- Verify v3-not-trigram and v9-not-SLIC framing in §II.
- LDVAE-T comparison (issue #618) optional but recommended.
- Target journal not conference (Procemin discoverability lesson).

## P4 — proposal

Scope: take the V-sweep cross-product and substitute the LDA backbone
for each of {LDA, HDP, ProdLDA, ETM, LDVAE}. 12 × 5 = 60 cells per
F-axis. Two F-axes minimum (F-1, F-7) = 120 cells. Each cell needs
its own per-V K-policy depending on backbone prior.

Decision: do **not** start P4 until P3 ships. P3 closes the question
"does the wordification choice matter?" and P4 then asks "does the
backbone choice matter more, less, or about the same?".

Dependencies: issues #617 (factorial), #621 (HDP), #618 (LDVAE-T).

## P5 — proposal

Scope: bring post-hoc interpretability tools (SHAP, counterfactual,
LLM-judge F-14/F-15) to the V-sweep canonical fits. Argues that the
"interpretable" claim of LDA-on-HSI is defensible beyond topic-word
lists.

Decision: P5 lives downstream of P4 (needs F-13..F-15 from #615,
#616, #622). Speculative until P3 is out.

## P6 (internal) — purpose

This directory. Living source of truth for design decisions,
reproducibility audits, deferred axes, and portfolio thinking.
Merged via PR like every other artefact but never submitted
externally. Path is `internal_tech_report/` (not `journal/`) to
make this explicit.

## What changes if P3's Bayesian posterior shows tight overlap

If the per-recipe Bayesian posterior on F-1 has overlap > 80% (HDI94
spanning >50% of the spread), the F-1 claim weakens to "no statistical
difference at the 5-fold pooling level". P3 is still publishable
because F-2 and F-7 spreads are large; the framing pivots to
"F-1 macro-F1 is recipe-insensitive but coherence and label-coupling
are not". This is documented in
[03_v_sweep_results.md](03_v_sweep_results.md) Bayesian section.

## What changes if a major competitor lands during P3 prep

If a 2026 H1 paper publishes a head-to-head wordification comparison
before P3 ships, the narrative shifts from "first such study" to
"first such study with N axes / N backbones". P3 should still ship;
the contribution is the framework integration, not just the
comparison.

If LDVAE-T or a successor publishes per-V evaluations, P3 cites it
and shows the V-sweep adds the orthogonal axis (multiple recipes
under one backbone vs one recipe under multiple backbones).
