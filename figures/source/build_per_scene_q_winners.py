"""Per-scene F-7 winner heatmap across Q=8/16/32.

For each (Q, scene) cell, finds the recipe with highest F-7 NMI and
colours the cell by the recipe's taxonomy family.

Output: figures/per-scene-q-winners.{pdf,svg,png}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "v_sweep" / "f7_topic_to_label"
OUT_DIR = REPO_ROOT / "figures"

SCENES = [
    ("indian-pines-corrected", "Indian Pines"),
    ("salinas-corrected", "Salinas"),
    ("salinas-a-corrected", "Salinas-A"),
    ("pavia-university", "Pavia U"),
    ("kennedy-space-center", "KSC"),
    ("botswana", "Botswana"),
]
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]
Q_VALUES = [8, 16, 32]

FAMILY = {
    "V1": "#0ea5e9", "V2": "#0ea5e9", "V3": "#0ea5e9",
    "V4": "#06b6d4", "V5": "#06b6d4", "V6": "#06b6d4", "V14": "#06b6d4",
    "V7": "#10b981", "V8": "#10b981", "V15": "#10b981",
    "V9": "#f59e0b", "V10": "#f59e0b",
    "V11": "#a855f7", "V12": "#a855f7", "V13": "#a855f7", "V17": "#a855f7",
    "V18": "#ec4899", "V19": "#ec4899",
    "V16": "#9333ea", "V20": "#9333ea",
}


def load_nmi(scene: str, recipe: str, q: int) -> float | None:
    f = SRC / f"{scene}_{recipe}_uniform_Q{q}.json"
    if not f.exists():
        return None
    d = json.load(f.open())
    v = d.get("normalised_mi")
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def main() -> int:
    fig, ax = plt.subplots(figsize=(13, 4.6))
    ax.set_xlim(-0.7, len(SCENES) - 0.3)
    ax.set_ylim(-0.7, len(Q_VALUES) + 0.2)
    ax.invert_yaxis()
    ax.axis("off")

    for qi, q in enumerate(Q_VALUES):
        for si, (scene_id, _) in enumerate(SCENES):
            best_r = None
            best_v = -1.0
            for r in RECIPES:
                v = load_nmi(scene_id, r, q)
                if v is None:
                    continue
                if v > best_v:
                    best_v = v
                    best_r = r
            colour = FAMILY.get(str(best_r), "#94a3b8") if best_r else "#cbd5e1"
            ax.add_patch(mpatches.FancyBboxPatch(
                (si - 0.45, qi - 0.45), 0.9, 0.9,
                boxstyle="round,pad=0.05",
                facecolor=colour, edgecolor="white", linewidth=2, alpha=0.92,
            ))
            ax.text(si, qi - 0.08, best_r or "—",
                    ha="center", va="center",
                    fontsize=15, fontweight="bold", color="white")
            ax.text(si, qi + 0.22, f"NMI = {best_v:.3f}",
                    ha="center", va="center", fontsize=8.5, color="white")

    for si, (_, label) in enumerate(SCENES):
        ax.text(si, -0.55, label, ha="center", va="bottom",
                fontsize=10.5, fontweight="bold")
    for qi, q in enumerate(Q_VALUES):
        ax.text(-0.6, qi, f"Q={q}", ha="right", va="center",
                fontsize=13, fontweight="bold")

    fig.text(
        0.5, 1.02,
        "Per-scene F-7 NMI winner across Q-levels (LDA backbone)",
        ha="center", fontsize=13, fontweight="bold",
    )
    fig.text(
        0.5, 0.98,
        "Colour = recipe family from the wordification taxonomy. V20 (purple) emerges at Q=32 on Indian Pines, Salinas, Salinas-A, Pavia U, Botswana.",
        ha="center", fontsize=9, color="#475569", style="italic",
    )

    families = [
        ("Pure spectral (V1-V3)", "#0ea5e9"),
        ("Differentiated / wavelet (V4-V6, V14)", "#06b6d4"),
        ("Absorption / chemistry (V7, V8, V15)", "#10b981"),
        ("Learnt codebook (V11-V13, V17)", "#a855f7"),
        ("Manifold (V18, V19)", "#ec4899"),
        ("Label-aware (V20)", "#9333ea"),
    ]
    handles = [mpatches.Patch(facecolor=c, edgecolor="white", label=l) for l, c in families]
    ax.legend(handles=handles, loc="lower center",
              bbox_to_anchor=(0.5, -0.32), ncol=3,
              fontsize=8.5, frameon=False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"per-scene-q-winners.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
