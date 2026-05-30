"""P3 cross-axis correlation figure.

For each (recipe, scene) cell, build a feature vector
[F-1, F-2 c_v, F-7 NMI, F-13 top-SHAP, F-14 jaccard, F-18 frac>=0.7,
F-22 median L1, HDP c_v, ProdLDA c_v, ETM c_v]. Compute Spearman
correlation across the 114 cells. Plot as a heatmap.

The point: show empirically which axes are redundant (highly
correlated) vs orthogonal (near-zero correlation). The F-2 vs F-22
positive correlation, the F-14 vs F-2 negative correlation, and the
F-18 vs F-2 *anti*-correlation are the structural insights.

Output: figures/p3-axis-correlation.{pdf,svg,png}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "v_sweep"
OUT_DIR = REPO_ROOT / "figures"

SCENES = [
    "indian-pines-corrected", "salinas-corrected", "salinas-a-corrected",
    "pavia-university", "kennedy-space-center", "botswana",
]
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]

# (label, axis dir, JSON key)
COLUMNS = [
    ("F-1",    "f1_per_fold",        "topic_routed_soft_mean"),
    ("F-2",    "f2_coherence",       "c_v"),
    ("F-7",    "f7_topic_to_label",  "normalised_mi"),
    ("F-14",   "f14_repetitiveness", "mean_pairwise_jaccard"),
    ("F-18",   "f18_reliability",    "frac_above_0.7"),
    ("F-22",   "f22_counterfactual", "counterfactual_l1_median"),
    ("HDP",    "hdp_backbone",       "f2_c_v"),
    ("ProdLDA","prodlda_backbone",   "f2_c_v"),
    ("ETM",    "etm_backbone",       "f2_c_v"),
]


def cell_value(axis_dir: str, scene: str, recipe: str, key: str) -> float | None:
    f = SRC / axis_dir / f"{scene}_{recipe}_uniform_Q8.json"
    if not f.exists():
        return None
    with f.open() as h:
        d = json.load(h)
    v = d.get(key)
    if v is None:
        # F-1 nested fallback
        if axis_dir == "f1_per_fold":
            per = d.get("per_fold")
            if per:
                vals = [r.get("topic_routed_soft") for r in per]
                vals = [x for x in vals if x is not None]
                if vals:
                    return float(sum(vals) / len(vals))
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def spearman_corr(a: np.ndarray, b: np.ndarray) -> float:
    """Rank-based Pearson on the joint-finite subset."""
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 3:
        return np.nan
    ar = np.argsort(np.argsort(a[mask]))
    br = np.argsort(np.argsort(b[mask]))
    return float(np.corrcoef(ar, br)[0, 1])


def main() -> int:
    n_cells = len(SCENES) * len(RECIPES)
    n_axes = len(COLUMNS)
    M = np.full((n_cells, n_axes), np.nan)
    for r_idx, (label, axis_dir, key) in enumerate(COLUMNS):
        c = 0
        for scene in SCENES:
            for recipe in RECIPES:
                v = cell_value(axis_dir, scene, recipe, key)
                if v is not None:
                    M[c, r_idx] = v
                c += 1

    # F-14 jaccard: lower is better, invert sign to align "higher = better"
    f14_idx = next(i for i, c in enumerate(COLUMNS) if c[0] == "F-14")
    M[:, f14_idx] = -M[:, f14_idx]

    corr = np.full((n_axes, n_axes), np.nan)
    for i in range(n_axes):
        for j in range(n_axes):
            corr[i, j] = spearman_corr(M[:, i], M[:, j])

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(np.arange(n_axes))
    ax.set_xticklabels([c[0] for c in COLUMNS], rotation=45, ha="right", fontsize=10)
    ax.set_yticks(np.arange(n_axes))
    ax.set_yticklabels([c[0] for c in COLUMNS], fontsize=10)
    ax.set_title(
        "Cross-axis Spearman rank correlation across 114 (recipe, scene) cells\n"
        "F-14 jaccard is sign-inverted so all axes are direction-aligned "
        "(higher = better).",
        fontsize=11, pad=14,
    )
    for i in range(n_axes):
        for j in range(n_axes):
            v = corr[i, j]
            if np.isnan(v):
                continue
            colour = "white" if abs(v) > 0.5 else "#0f172a"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=9.5, color=colour, fontweight="bold")

    cb = fig.colorbar(im, ax=ax, shrink=0.78, pad=0.02)
    cb.set_label("Spearman ρ", fontsize=9)

    fig.text(
        0.01, 0.005,
        "Reading: F-2 / F-7 / F-22 / HDP / ProdLDA / ETM form a positively-correlated cluster — "
        "recipes with strong topic-word coherence also produce label-aligned, robust topics under multiple backbones. "
        "F-18 anti-correlates with F-2 (the vocabulary-size confounder Stammbach et al. flagged). "
        "F-14 (inverted) correlates positively with F-1 / F-22 — diverse topics are more robust.",
        fontsize=7.5, color="#475569", ha="left",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"p3-axis-correlation.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
