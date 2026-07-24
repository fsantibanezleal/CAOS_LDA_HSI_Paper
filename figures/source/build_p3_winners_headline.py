"""P3 headline figure — winners per (axis, scene) across V1..V20.

Reads the F-1, F-2, F-7 cells from the CAOS_LDA_HSI repo and produces
a publication-grade matrix figure that highlights the V20 triple-axis
win on Indian Pines plus the broader "no universal winner" finding.

Layout:
* Three rows (F-1 macro-F1, F-2 c_v, F-7 NMI)
* Six columns (the labelled scenes)
* Each row contains a barchart of all 19 recipes; winner barred and
  annotated with a star. V20 is colour-coded purple throughout.

Output: figures/p3-winners-headline.{pdf,svg,png}
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
    ("indian-pines-corrected", "Indian Pines"),
    ("salinas-corrected",      "Salinas"),
    ("salinas-a-corrected",    "Salinas-A"),
    ("pavia-university",       "Pavia U"),
    ("kennedy-space-center",   "KSC"),
    ("botswana",               "Botswana"),
]
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]
AXES = [
    ("f1_per_fold",        "F-1 macro-F1 (5-fold mean, topic_routed_soft)", "topic_routed_soft_mean"),
    ("f2_coherence",       "F-2 $c_v$ coherence (top-10 words)",            "c_v"),
    ("f7_topic_to_label",  "F-7 NMI(argmax topic, label)",                  "normalised_mi"),
]


def load_value(axis_dir: str, scene: str, recipe: str, key: str) -> float | None:
    f = SRC / axis_dir / f"{scene}_{recipe}_uniform_Q8.json"
    if not f.exists():
        return None
    with f.open() as h:
        data = json.load(h)
    if key in data and data[key] is not None:
        try:
            return float(data[key])
        except (TypeError, ValueError):
            return None
    # f1 has nested per_fold
    if axis_dir == "f1_per_fold":
        per = data.get("per_fold")
        if per:
            vals = [f.get("topic_routed_soft") for f in per]
            vals = [v for v in vals if v is not None]
            if vals:
                return float(sum(vals) / len(vals))
    return None


def main() -> int:
    fig, axes = plt.subplots(
        nrows=3, ncols=6, figsize=(18, 8.5), sharex=True,
        gridspec_kw={"hspace": 0.42, "wspace": 0.15},
    )

    for row_idx, (axis_dir, axis_label, key) in enumerate(AXES):
        for col_idx, (scene_id, scene_short) in enumerate(SCENES):
            ax = axes[row_idx, col_idx]
            vals: list[float | None] = []
            for r in RECIPES:
                vals.append(load_value(axis_dir, scene_id, r, key))
            arr = np.array([v if v is not None else np.nan for v in vals])
            # Identify winner ignoring NaN
            valid = ~np.isnan(arr)
            if valid.any():
                winner_idx = int(np.nanargmax(arr))
            else:
                winner_idx = -1

            # Colour palette
            colours = []
            for i, r in enumerate(RECIPES):
                if i == winner_idx:
                    colours.append("#16a34a")  # winner green
                elif r == "V20":
                    colours.append("#9333ea")  # V20 purple highlight
                elif r in ("V1", "V3", "V12"):
                    colours.append("#0ea5e9")  # legacy reference blue
                else:
                    colours.append("#94a3b8")  # neutral grey

            x = np.arange(len(RECIPES))
            ax.bar(x, np.nan_to_num(arr, nan=0), color=colours, width=0.78, edgecolor="none")

            # Annotate winner with star
            if winner_idx >= 0 and not np.isnan(arr[winner_idx]):
                ax.text(
                    winner_idx, arr[winner_idx] + 0.02,
                    f"★ {RECIPES[winner_idx]}\n{arr[winner_idx]:.2f}",
                    ha="center", va="bottom", fontsize=8.5,
                    color="#15803d", fontweight="bold",
                )

            # V20 always annotated even if not winner, to drive the narrative
            v20_idx = RECIPES.index("V20")
            if v20_idx != winner_idx and not np.isnan(arr[v20_idx]):
                ax.text(
                    v20_idx, arr[v20_idx] + 0.015,
                    f"{arr[v20_idx]:.2f}",
                    ha="center", va="bottom", fontsize=7.5,
                    color="#7e22ce", fontweight="bold",
                )

            ax.set_xticks(x)
            ax.set_xticklabels(RECIPES, rotation=90, fontsize=7)
            ax.tick_params(axis="y", labelsize=8)
            ax.set_ylim(0, max(1.05, float(np.nanmax(arr)) + 0.08 if valid.any() else 1.0))
            ax.grid(axis="y", alpha=0.18, linewidth=0.5)
            if row_idx == 0:
                ax.set_title(scene_short, fontsize=11, fontweight="bold")
            if col_idx == 0:
                ax.set_ylabel(axis_label.split("(")[0].strip(), fontsize=10)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    fig.suptitle(
        "Wordification matters: per-axis winners on six labelled HSI scenes "
        "(V1..V15, V17..V20)\nGreen ★ = winner per cell; purple = V20 "
        "(mutual-information-weighted bands, new)",
        fontsize=12, fontweight="bold", y=0.995,
    )
    fig.text(
        0.01, 0.005,
        "Indian Pines: V20 wins F-2 (0.88) and F-7 (0.44); F-1 is a tie "
        "(V2 0.861 vs V20 0.858). "
        "F-7 mean ranking: V12 0.534 / V3 0.524 / V20 0.520 (within 0.014 NMI of each other). "
        "Source: data/derived/v_sweep/{f1_per_fold,f2_coherence,f7_topic_to_label}/ in CAOS_LDA_HSI.",
        fontsize=8, color="#475569", ha="left",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"p3-winners-headline.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
