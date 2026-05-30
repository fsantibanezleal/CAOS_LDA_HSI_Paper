"""P4 — per-scene × backbone F-7 winner grid.

For each (backbone, scene) pair, identify which recipe produces the
highest F-7 NMI. Tile the result as a 4 × 6 grid; each cell labels
the winning recipe + colours the cell by the absolute NMI value.

Output: figures/p4-backbone-scene-winners.{pdf,svg,png}
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
SRC_LDA = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "v_sweep" / "f7_topic_to_label"
SRC_BB = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "v_sweep" / "backbones_f7"
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

BACKBONES = [
    ("LDA", lambda scene, recipe: SRC_LDA / f"{scene}_{recipe}_uniform_Q8.json"),
    ("HDP", lambda scene, recipe: SRC_BB / f"hdp_{scene}_{recipe}_uniform_Q8.json"),
    ("ProdLDA", lambda scene, recipe: SRC_BB / f"prodlda_{scene}_{recipe}_uniform_Q8.json"),
    ("ETM", lambda scene, recipe: SRC_BB / f"etm_{scene}_{recipe}_uniform_Q8.json"),
]

# A discrete colour per recipe-family (matches taxonomy figure)
FAMILY = {
    "V1": "#0ea5e9", "V2": "#0ea5e9", "V3": "#0ea5e9",
    "V4": "#06b6d4", "V5": "#06b6d4", "V6": "#06b6d4", "V14": "#06b6d4",
    "V7": "#10b981", "V8": "#10b981", "V15": "#10b981",
    "V9": "#f59e0b", "V10": "#f59e0b",
    "V11": "#a855f7", "V12": "#a855f7", "V13": "#a855f7", "V17": "#a855f7",
    "V18": "#ec4899", "V19": "#ec4899",
    "V16": "#9333ea", "V20": "#9333ea",
}


def load_nmi(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        d = json.load(path.open())
    except Exception:
        return None
    v = d.get("normalised_mi")
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main() -> int:
    grid_winner = np.empty((len(BACKBONES), len(SCENES)), dtype=object)
    grid_nmi = np.full((len(BACKBONES), len(SCENES)), np.nan)
    for bi, (bname, path_fn) in enumerate(BACKBONES):
        for si, (scene_id, _) in enumerate(SCENES):
            best_v = -1.0
            best_r = "—"
            for r in RECIPES:
                v = load_nmi(path_fn(scene_id, r))
                if v is None:
                    continue
                if v > best_v:
                    best_v = v
                    best_r = r
            grid_winner[bi, si] = best_r
            if best_v >= 0:
                grid_nmi[bi, si] = best_v

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_xlim(-0.7, len(SCENES) - 0.3)
    ax.set_ylim(-0.7, len(BACKBONES) + 0.2)
    ax.invert_yaxis()
    ax.axis("off")

    # Cells
    for bi in range(len(BACKBONES)):
        for si in range(len(SCENES)):
            winner = grid_winner[bi, si]
            nmi = grid_nmi[bi, si]
            colour = FAMILY.get(str(winner), "#94a3b8")
            ax.add_patch(mpatches.FancyBboxPatch(
                (si - 0.45, bi - 0.45), 0.9, 0.9,
                boxstyle="round,pad=0.05",
                facecolor=colour, edgecolor="white", linewidth=2, alpha=0.9,
            ))
            ax.text(si, bi - 0.05, str(winner), ha="center", va="center",
                    fontsize=14.5, fontweight="bold", color="white")
            ax.text(si, bi + 0.22,
                    f"NMI = {nmi:.3f}" if not np.isnan(nmi) else "—",
                    ha="center", va="center", fontsize=8.5, color="white")

    # Scene labels above the grid (closer to cells)
    for si, (_, label) in enumerate(SCENES):
        ax.text(si, -0.55, label, ha="center", va="bottom",
                fontsize=10.5, fontweight="bold")
    for bi, (bname, _) in enumerate(BACKBONES):
        ax.text(-0.62, bi, bname, ha="right", va="center",
                fontsize=12, fontweight="bold")

    # Title above the scene labels
    fig.text(
        0.5, 1.02,
        "Per-scene F-7 NMI winner under each backbone — 6 labelled scenes × 4 backbones",
        ha="center", fontsize=13, fontweight="bold",
    )
    fig.text(
        0.5, 0.98,
        "Colour = recipe family from the wordification taxonomy (cf. wordification-taxonomy.pdf)",
        ha="center", fontsize=9.5, color="#475569", style="italic",
    )

    # Legend at the bottom
    families_seen = sorted({FAMILY.get(str(grid_winner[bi, si]), "#94a3b8")
                            for bi in range(len(BACKBONES))
                            for si in range(len(SCENES))})
    legend_items = []
    for code, colour in [
        ("Pure spectral (V1-V3)", "#0ea5e9"),
        ("Differentiated / wavelet (V4-V6, V14)", "#06b6d4"),
        ("Absorption / chemistry (V7, V8, V15)", "#10b981"),
        ("Spatial / region (V9, V10)", "#f59e0b"),
        ("Learnt unsupervised (V11-V13, V17)", "#a855f7"),
        ("Manifold (V18, V19)", "#ec4899"),
        ("Label-aware (V20)", "#9333ea"),
    ]:
        if colour in families_seen:
            legend_items.append(mpatches.Patch(facecolor=colour, edgecolor="white", label=code))
    if legend_items:
        ax.legend(
            handles=legend_items,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.36),
            ncol=4,
            fontsize=8,
            frameon=False,
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"p4-backbone-scene-winners.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
