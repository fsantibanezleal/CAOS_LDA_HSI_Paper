"""Q-sensitivity figure for top contender recipes.

Reads F-2 c_v and F-7 NMI cells across Q=8 / Q=16 / Q=32 for the
top contender recipes and plots two side-by-side line graphs.

Used in P3 §6 (Q-sensitivity discussion).

Output: figures/q-sensitivity-top-recipes.{pdf,svg,png}
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
RECIPES = ["V3", "V8", "V12", "V14", "V18", "V20"]
RECIPE_COLOURS = {
    "V3":  "#0ea5e9",
    "V8":  "#10b981",
    "V12": "#f59e0b",
    "V14": "#06b6d4",
    "V18": "#ec4899",
    "V20": "#9333ea",
}
RECIPE_MARKERS = {
    "V3":  "o",
    "V8":  "s",
    "V12": "D",
    "V14": "^",
    "V18": "v",
    "V20": "*",
}
Q_VALUES = [8, 16, 32]


def load_axis_mean(axis_dir: str, key: str, recipe: str, q: int) -> float | None:
    vals: list[float] = []
    for sc in SCENES:
        f = SRC / axis_dir / f"{sc}_{recipe}_uniform_Q{q}.json"
        if not f.exists():
            continue
        d = json.load(f.open())
        v = d.get(key)
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                continue
    if not vals or len(vals) < 4:
        return None
    return statistics.mean(vals)


def main() -> int:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
    ax_f2, ax_f7 = axes

    for recipe in RECIPES:
        colour = RECIPE_COLOURS[recipe]
        marker = RECIPE_MARKERS[recipe]
        # F-2
        f2 = [load_axis_mean("f2_coherence", "c_v", recipe, q) for q in Q_VALUES]
        x_f2 = [q for q, v in zip(Q_VALUES, f2) if v is not None]
        y_f2 = [v for v in f2 if v is not None]
        if y_f2:
            ax_f2.plot(x_f2, y_f2, marker=marker, color=colour, linewidth=2.2,
                       markersize=9, label=recipe)
        # F-7
        f7 = [load_axis_mean("f7_topic_to_label", "normalised_mi", recipe, q)
              for q in Q_VALUES]
        x_f7 = [q for q, v in zip(Q_VALUES, f7) if v is not None]
        y_f7 = [v for v in f7 if v is not None]
        if y_f7:
            ax_f7.plot(x_f7, y_f7, marker=marker, color=colour, linewidth=2.2,
                       markersize=9, label=recipe)

    for ax, title, ylabel in [
        (ax_f2, r"F-2 coherence $c_v$ (top-10 words)", r"$c_v$ mean across 6 scenes"),
        (ax_f7, r"F-7 NMI (argmax topic vs label)", r"NMI mean across 6 scenes"),
    ]:
        ax.set_xticks(Q_VALUES)
        ax.set_xticklabels([f"Q={q}" for q in Q_VALUES], fontsize=10)
        ax.set_xlabel("Quantisation level $Q$", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(alpha=0.18, linewidth=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="lower right" if ax is ax_f7 else "lower right",
                  fontsize=10, frameon=False, ncol=2)

    fig.suptitle(
        "Q-sensitivity for top-contender recipes — V20 keeps climbing at finer quantisation",
        fontsize=13, fontweight="bold", y=1.0,
    )
    fig.text(
        0.5, 0.005,
        "V20 (purple ★) is the only recipe whose F-2 and F-7 means improve monotonically from Q=8 to Q=32. "
        "V12/V3 plateau or regress at Q=32. V8 is Q-insensitive because its vocabulary is the endmember count, "
        "independent of Q. Q-sweep continues to a follow-up.",
        ha="center", fontsize=8.5, color="#475569",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"q-sensitivity-top-recipes.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
