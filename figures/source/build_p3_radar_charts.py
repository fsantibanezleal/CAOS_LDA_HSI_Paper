"""P3 per-recipe radar charts — top contenders V1/V3/V12/V14/V18/V20.

Each radar shows the same 8 axes normalised to [0, 1] over the
recipe-level means. F-14 jaccard is inverted so all axes are "higher
is better" inside the radar.

Output: figures/p3-radar-top-recipes.{pdf,svg,png}
"""
from __future__ import annotations

import json
import statistics
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
ALL_RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]
FOCUS_RECIPES = ["V1", "V3", "V12", "V14", "V18", "V20"]
RECIPE_COLORS = {
    "V1":  "#94a3b8",
    "V3":  "#0ea5e9",
    "V12": "#f59e0b",
    "V14": "#16a34a",
    "V18": "#0284c7",
    "V20": "#9333ea",
}

AXES = [
    ("F-1",  "f1_per_fold",        "topic_routed_soft_mean", False),
    ("F-2",  "f2_coherence",       "c_v",                    False),
    ("F-7",  "f7_topic_to_label",  "normalised_mi",          False),
    ("F-14", "f14_repetitiveness", "mean_pairwise_jaccard",  True),   # lower is better
    ("F-18", "f18_reliability",    "frac_above_0.7",         False),
    ("F-22", "f22_counterfactual", "counterfactual_l1_median", False),
    ("HDP",  "hdp_backbone",       "f2_c_v",                 False),
    ("ETM",  "etm_backbone",       "f2_c_v",                 False),
]


def axis_value(axis_dir: str, scene: str, recipe: str, key: str) -> float | None:
    f = SRC / axis_dir / f"{scene}_{recipe}_uniform_Q8.json"
    if not f.exists():
        return None
    with f.open() as h:
        d = json.load(h)
    v = d.get(key)
    if v is None and axis_dir == "f1_per_fold":
        per = d.get("per_fold")
        if per:
            vals = [r.get("topic_routed_soft") for r in per]
            vals = [x for x in vals if x is not None]
            if vals:
                return float(sum(vals) / len(vals))
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def recipe_means(recipe: str) -> dict[str, float]:
    means: dict[str, float] = {}
    for label, axis_dir, key, _ in AXES:
        vals = []
        for sc in SCENES:
            v = axis_value(axis_dir, sc, recipe, key)
            if v is not None:
                vals.append(v)
        if vals:
            means[label] = statistics.mean(vals)
    return means


def normalise_axis(recipe_to_value: dict[str, float], lower_is_better: bool) -> dict[str, float]:
    if not recipe_to_value:
        return {}
    lo = min(recipe_to_value.values())
    hi = max(recipe_to_value.values())
    rng = max(hi - lo, 1e-9)
    out = {}
    for r, v in recipe_to_value.items():
        norm = (v - lo) / rng
        if lower_is_better:
            norm = 1.0 - norm
        out[r] = norm
    return out


def main() -> int:
    # Compute per-axis recipe-mean across all 19 recipes for normalisation
    all_means = {r: recipe_means(r) for r in ALL_RECIPES}

    axis_normalised: dict[str, dict[str, float]] = {}
    for label, _, _, lower_better in AXES:
        recipe_to_value = {r: all_means[r].get(label, np.nan) for r in ALL_RECIPES}
        finite = {r: v for r, v in recipe_to_value.items() if not np.isnan(v)}
        axis_normalised[label] = normalise_axis(finite, lower_better)

    # Plot
    n_axes = len(AXES)
    angles = np.linspace(0, 2 * np.pi, n_axes, endpoint=False).tolist()
    angles += angles[:1]
    axis_labels = [a[0] for a in AXES]

    fig, axes = plt.subplots(
        2, 3, figsize=(14, 9.5),
        subplot_kw={"projection": "polar"},
    )
    for ax_idx, recipe in enumerate(FOCUS_RECIPES):
        ax = axes[ax_idx // 3, ax_idx % 3]
        values = [axis_normalised[label].get(recipe, 0.0) for label, *_ in AXES]
        values += values[:1]
        colour = RECIPE_COLORS[recipe]
        ax.plot(angles, values, color=colour, linewidth=2.2)
        ax.fill(angles, values, color=colour, alpha=0.18)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(axis_labels, fontsize=10)
        ax.set_ylim(0, 1.02)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["", "0.5", "", "1.0"], fontsize=8)
        ax.set_title(f"{recipe}", fontsize=13, fontweight="bold",
                     color=colour, pad=12)
        ax.grid(alpha=0.3, linewidth=0.5)

    fig.suptitle(
        "Per-recipe radar — 8 evaluation axes normalised to [0, 1] across 19 recipes\n"
        "(F-14 jaccard inverted so '1' always means 'best on this axis').",
        fontsize=12, fontweight="bold", y=1.005,
    )
    fig.text(
        0.5, 0.005,
        "V20 (purple) and V12 (orange) cover the most surface area — they are top-tier on coherence + counterfactual robustness + ETM backbone. "
        "V18 (cyan) tops the F-18 reliability axis. V1 (grey) is mid-pack on most axes. V14 (green) is a balanced multi-scale alternative.",
        fontsize=8.5, color="#475569", ha="center",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"p3-radar-top-recipes.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
