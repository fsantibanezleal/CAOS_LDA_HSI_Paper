# Internal technical report — CAOS LDA HSI

This is **not a manuscript for external submission**. It is the
parking lot for design decisions, deprecated approaches, per-V
diagnostic detail, and reproducibility audit that does not fit in
the P1 / P2 / P3 / P4 / P5 manuscripts but is essential for any
future contributor (or reviewer with deep questions).

## Contents

- [`01_design_space.md`](01_design_space.md) — full V1..V20 design-space
  rationale, including UI/code discrepancies (V3 not trigram, V9 not
  SLIC, V11 seed gap) and how we resolved them.
- [`02_k_policy.md`](02_k_policy.md) — per-V K-policy derivation
  (K = clip(round(mean_doc/2), 3, K_P1)) and the alternatives we
  rejected.
- [`03_v_sweep_results.md`](03_v_sweep_results.md) — full per-V per-scene
  per-axis numbers + Bayesian posterior + spread analysis. Source of
  truth for any table that ends up in P3.
- [`04_reproducibility_audit.md`](04_reproducibility_audit.md) — seed
  pinning status per recipe + Stammbach citation year verification +
  every external claim cross-checked.
- [`05_deferred_axes.md`](05_deferred_axes.md) — F-13..F-18 candidate
  axes from the literature search + cost/benefit per axis.
- [`06_paper_portfolio.md`](06_paper_portfolio.md) — how P3/P4/P5
  divide the surface area and what each depends on. Living doc.

## Status

Scaffold created 2026-05-26. Sections populated as the V-sweep
analysis matures. This is meant to be merged via PR like any other
paper artefact, but is kept in `internal_tech_report/` (not
`journal/`) so it never accidentally gets submitted somewhere.
