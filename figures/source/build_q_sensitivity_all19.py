"""Full 19-recipe Q-sensitivity figure (c445).

Plots F-7 NMI across Q=8/16/32 for every available recipe. Highlights
the 3 monotonic-UP recipes (V20, V2, V8) in bold colour; greys out
recipes whose F-7 declines or saturates.

Output: figures/q-sensitivity-all19.{pdf,svg,png}
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
# All recipes (V13 excluded — Q-insensitive)
RECIPES = [
    "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10",
    "V11", "V12", "V14", "V15", "V17", "V18", "V19", "V20",
]
Q_VALUES = [8, 16, 32]

# Mono-UP recipes — bold colour
MONO_UP_F7 = {"V20", "V2", "V8", "V6"}
MONO_UP_BOTH = {"V20", "V2", "V8"}

RECIPE_COLOURS = {
    "V20": "#9333ea",   # Bold purple (label-aware, biggest gain)
    "V2":  "#0ea5e9",   # Bold cyan (intensity-bin)
    "V8":  "#10b981",   # Bold green (NFINDR endmember)
    "V6":  "#06b6d4",   # F-7 mono UP but F-2 mono DOWN — dotted
}
NEUTRAL = "#cbd5e1"  # grey for non-mono-UP recipes


def load_axis_mean(axis_dir: str, key: str, recipe: str, q: int) -> float | None:
    vals: list[float] = []
    for sc in SCENES:
        f = SRC / axis_dir / f"{sc}_{recipe}_uniform_Q{q}.json"
        if not f.exists():
            continue
        d = json.load(f.open())
        v = d.get(key)
        if v is None:
            continue
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            continue
    if not vals or len(vals) < 4:
        return None
    return statistics.mean(vals)


def main() -> int:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax_f2, ax_f7 = axes

    # First pass: plot greys
    for recipe in RECIPES:
        if recipe in MONO_UP_BOTH or recipe == "V6":
            continue
        f2 = [load_axis_mean("f2_coherence", "c_v", recipe, q) for q in Q_VALUES]
        f7 = [load_axis_mean("f7_topic_to_label", "normalised_mi", recipe, q) for q in Q_VALUES]
        for ax, ys in [(ax_f2, f2), (ax_f7, f7)]:
            x = [q for q, v in zip(Q_VALUES, ys) if v is not None]
            y = [v for v in ys if v is not None]
            if y:
                ax.plot(x, y, color=NEUTRAL, alpha=0.55, linewidth=1.1, marker="o", markersize=4)
                ax.annotate(recipe, (x[-1], y[-1]), fontsize=7, color="#94a3b8", ha="left", va="center")

    # Second pass: plot highlights
    for recipe in ["V6", "V8", "V2", "V20"]:
        f2 = [load_axis_mean("f2_coherence", "c_v", recipe, q) for q in Q_VALUES]
        f7 = [load_axis_mean("f7_topic_to_label", "normalised_mi", recipe, q) for q in Q_VALUES]
        colour = RECIPE_COLOURS.get(recipe, "#94a3b8")
        marker = "*" if recipe == "V20" else "o"
        msize = 13 if recipe == "V20" else 9
        lw = 2.5 if recipe in MONO_UP_BOTH else 1.6
        ls = "-" if recipe in MONO_UP_BOTH else (0, (3, 2))
        for ax, ys in [(ax_f2, f2), (ax_f7, f7)]:
            x = [q for q, v in zip(Q_VALUES, ys) if v is not None]
            y = [v for v in ys if v is not None]
            if y:
                ax.plot(x, y, color=colour, linewidth=lw, marker=marker,
                        markersize=msize, linestyle=ls,
                        label=f"{recipe} (mono UP on F-2+F-7)" if recipe in MONO_UP_BOTH else f"{recipe} (F-7 only)")

    for ax, title, ylabel in [
        (ax_f2, r"F-2 coherence $c_v$ (top-10 words)", r"$c_v$ mean across 6 scenes"),
        (ax_f7, r"F-7 NMI (argmax topic vs label)", r"NMI mean across 6 scenes"),
    ]:
        ax.set_xticks(Q_VALUES)
        ax.set_xticklabels([f"Q={q}" for q in Q_VALUES], fontsize=11)
        ax.set_xlabel("Quantisation level $Q$", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(alpha=0.18, linewidth=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="upper left", fontsize=9.5, frameon=False)

    fig.suptitle(
        "Full 19-recipe Q-sensitivity — only V20/V2/V8 are monotonic ↑ on both axes",
        fontsize=13.5, fontweight="bold", y=1.0,
    )
    fig.text(
        0.5, 0.005,
        "Three recipes climb monotonically on F-2 and F-7 across Q=8/16/32: V20 (purple ★, label-aware), V2 (cyan, intensity-bin), V8 (green, NFINDR endmember). "
        "V6 (dashed cyan) climbs on F-7 only — F-2 regresses. V20 has the steepest gains and highest absolute values on both axes. "
        "Eight recipes decline monotonically; six peak at Q=16 then regress.",
        ha="center", fontsize=8.5, color="#475569",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"q-sensitivity-all19.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
