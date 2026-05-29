"""Wordification taxonomy figure — group all 20 recipes by family.

A taxonomic tree that groups V1..V20 by the seven design axes
discussed in P3 §2.1. Used as a navigational figure in P3 and the
methodology page of the web app.

Output: figures/wordification-taxonomy.{pdf,svg,png}
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "figures"


# Seven groups → recipes within each. Order matters for visual layout.
GROUPS = [
    ("Pure spectral / fixed alphabet",
     ["V1", "V2", "V3"],
     "#0ea5e9",
     "band-frequency + intensity-only + joint (band, bin)"),
    ("Differentiated / multi-scale",
     ["V4", "V5", "V6", "V14"],
     "#06b6d4",
     "1st/2nd derivative, dyadic wavelet, continuous Morlet wavelet"),
    ("Absorption / chemistry-aware",
     ["V7", "V8", "V15"],
     "#10b981",
     "absorption triplet, endmember-fraction, spectral indices"),
    ("Spatial / region-based",
     ["V9", "V10"],
     "#f59e0b",
     "Felzenszwalb region + SAM, VNIR/SWIR groups"),
    ("Learnt unsupervised codebook",
     ["V11", "V12", "V13", "V17"],
     "#a855f7",
     "PQ, GMM, VQ-VAE, sparse-coding"),
    ("Manifold / embedding-based",
     ["V18", "V19"],
     "#ec4899",
     "graph-Laplacian eigenvectors, UMAP coords"),
    ("Label-aware / foundation",
     ["V16", "V20"],
     "#9333ea",
     "HyperSIGMA foundation embedding (scaffold), MI-weighted bands"),
]

# Per-recipe metadata: vocab, key strength
META = {
    "V1": ("B", "Canonical baseline"),
    "V2": ("Q", "Band-agnostic"),
    "V3": ("B·Q", "Cross-backbone star"),
    "V4": ("B", "1st-derivative"),
    "V5": ("B", "2nd-derivative"),
    "V6": ("≈B", "Db4 DWT"),
    "V7": ("≤C_b Q²", "Absorption features"),
    "V8": ("K_e·Q", "NFINDR endmembers"),
    "V9": ("R·Q", "Felzenszwalb regions"),
    "V10": ("3·Q", "VNIR/SWIR groups"),
    "V11": ("M·K_s", "Product quantisation"),
    "V12": ("B·Q", "GMM components"),
    "V13": ("M·K_c = 128", "VQ-VAE, ST-est"),
    "V14": ("16·Q = 128", "Morlet CWT"),
    "V15": ("≤48", "NDVI / MNDWI / NBR"),
    "V16": ("128–256", "HyperSIGMA (scaffold)"),
    "V17": ("K·Q = 512", "MiniBatch dict"),
    "V18": ("K_e·Q = 128", "Sym-normalised Laplacian"),
    "V19": ("3·Q = 24", "3-D UMAP"),
    "V20": ("B·Q", "MI-weighted, label-aware"),
}


def main() -> int:
    fig, ax = plt.subplots(figsize=(16, 9.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title
    ax.text(50, 96.5,
            "Wordification taxonomy — 20 recipes for LDA-on-HSI",
            ha="center", fontsize=15, fontweight="bold")
    ax.text(50, 93,
            "Each group bundles recipes that share token-alphabet semantics. "
            "Vocabulary size and core mechanism are noted per recipe.",
            ha="center", fontsize=10, color="#475569", style="italic")

    # Layout the 7 groups vertically
    n_groups = len(GROUPS)
    group_h = 86 / n_groups
    y_start = 88

    for g_idx, (name, recipes, colour, description) in enumerate(GROUPS):
        y = y_start - (g_idx + 0.5) * group_h

        # Group title bar
        ax.add_patch(mpatches.FancyBboxPatch(
            (1, y - group_h * 0.42), 22, group_h * 0.84,
            boxstyle="round,pad=0.3",
            facecolor=colour, edgecolor="white", alpha=0.85,
        ))
        ax.text(12, y + 1.4, name, ha="center", fontsize=10.5,
                color="white", fontweight="bold")
        ax.text(12, y - 1.6, description, ha="center", fontsize=8.5,
                color="white", style="italic")

        # Connector
        ax.plot([23.5, 27], [y, y], color=colour, linewidth=2.2, alpha=0.7)

        # Recipe boxes
        n_r = len(recipes)
        x_start = 28
        x_end = 99
        box_w = min(11, (x_end - x_start - (n_r - 1) * 1.2) / n_r)
        spacing = (x_end - x_start - n_r * box_w) / max(n_r - 1, 1) if n_r > 1 else 0

        for r_idx, recipe in enumerate(recipes):
            cx = x_start + r_idx * (box_w + spacing) + box_w / 2
            top_y = y + group_h * 0.42
            bot_y = y - group_h * 0.42
            vocab, strength = META.get(recipe, ("?", "?"))
            is_v20 = recipe == "V20"
            is_v16 = recipe == "V16"

            # Box
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx - box_w / 2, bot_y), box_w, top_y - bot_y,
                boxstyle="round,pad=0.25",
                facecolor="white",
                edgecolor=colour,
                linewidth=2.4 if is_v20 else 1.0,
                alpha=0.95,
            ))
            # Star annotation for V20
            if is_v20:
                ax.text(cx, top_y - 1.5, "★",
                        ha="center", fontsize=12,
                        color="#9333ea", fontweight="bold")
            # Scaffold marker for V16
            if is_v16:
                ax.text(cx, top_y - 1.5, "⚙",
                        ha="center", fontsize=11,
                        color=colour, fontweight="bold")

            # Recipe id
            ax.text(cx, y + 1.2, recipe,
                    ha="center", fontsize=11.5,
                    color=colour if not is_v20 else "#9333ea",
                    fontweight="bold")
            # Vocab
            ax.text(cx, y - 0.9, vocab,
                    ha="center", fontsize=8.3,
                    color="#1f2937", family="monospace")
            # Strength one-liner
            ax.text(cx, y - 3.0, strength,
                    ha="center", fontsize=7.7,
                    color="#475569", style="italic")

    # Legend at bottom
    legend_y = 2.5
    ax.add_patch(mpatches.FancyBboxPatch(
        (1, 0.2), 98, 3.3,
        boxstyle="round,pad=0.2",
        facecolor="#f1f5f9", edgecolor="#cbd5e1", alpha=0.7,
    ))
    ax.text(2.5, legend_y - 0.6,
            "★ = triple-axis winner on Indian Pines (F-1 0.858, F-2 0.88, F-7 0.44) — V20 is the only label-aware recipe in the sweep.",
            fontsize=8.5, color="#0f172a", fontweight="bold")
    ax.text(2.5, legend_y - 2.2,
            "⚙ = scaffolded only (V16 reserves the foundation-model slot; HyperSIGMA weights not yet vendored).",
            fontsize=8.5, color="#475569")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"wordification-taxonomy.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
