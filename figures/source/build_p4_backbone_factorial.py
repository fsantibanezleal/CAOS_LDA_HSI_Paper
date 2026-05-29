"""P4 / wiki figure — backbone × wordification factorial heatmap.

Reads F-2 c_v means from each of the four backbone directories under
``data/derived/v_sweep/`` and produces a publication-grade heatmap
that shows which (backbone, recipe) cells dominate.

Cells highlighted:
- best per-backbone row (green border + star)
- V20 always annotated (purple text) to keep the narrative
- HDP missing cells (V13/V15/V17/V19) shown as hatched

Output: figures/p4-backbone-factorial.{pdf,svg,png}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "v_sweep"
OUT_DIR = REPO_ROOT / "figures"

SCENES = [
    "indian-pines-corrected", "salinas-corrected", "salinas-a-corrected",
    "pavia-university", "kennedy-space-center", "botswana",
]
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]

BACKBONES = [
    ("LDA",     "f2_coherence",       "c_v"),
    ("HDP",     "hdp_backbone",       "f2_c_v"),
    ("ProdLDA", "prodlda_backbone",   "f2_c_v"),
    ("ETM",     "etm_backbone",       "f2_c_v"),
]


def cell_mean(backbone_dir: str, recipe: str, key: str) -> float | None:
    vals: list[float] = []
    for scene in SCENES:
        f = SRC / backbone_dir / f"{scene}_{recipe}_uniform_Q8.json"
        if not f.exists():
            continue
        with f.open() as h:
            d = json.load(h)
        v = d.get(key) or d.get("score") or d.get("c_v_mean")
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                continue
    if not vals:
        return None
    return float(np.mean(vals))


def main() -> int:
    data = np.full((len(BACKBONES), len(RECIPES)), np.nan)
    for r_idx, (_, bdir, key) in enumerate(BACKBONES):
        for c_idx, recipe in enumerate(RECIPES):
            v = cell_mean(bdir, recipe, key)
            if v is not None:
                data[r_idx, c_idx] = v

    fig, ax = plt.subplots(figsize=(15, 4.6))
    cmap = plt.cm.viridis.copy()
    cmap.set_bad("#fee2e2")  # missing cells in light red

    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0.0, vmax=1.0)

    # Cell annotations
    v20_idx = RECIPES.index("V20")
    for r in range(data.shape[0]):
        row = data[r]
        # winner per backbone row
        valid_mask = ~np.isnan(row)
        if valid_mask.any():
            winner_col = int(np.nanargmax(row))
        else:
            winner_col = -1
        for c in range(data.shape[1]):
            v = data[r, c]
            if np.isnan(v):
                # hatched marker
                ax.add_patch(
                    Rectangle((c - 0.5, r - 0.5), 1, 1,
                              fill=False, hatch="////",
                              edgecolor="#94a3b8", linewidth=0.4),
                )
                ax.text(c, r, "—", ha="center", va="center",
                        fontsize=8.5, color="#64748b")
                continue
            colour_text = "white" if v < 0.55 else "#0f172a"
            label = f"{v:.2f}"
            weight = "normal"
            if c == winner_col:
                weight = "bold"
                ax.add_patch(
                    Rectangle((c - 0.5, r - 0.5), 1, 1,
                              fill=False, edgecolor="#16a34a", linewidth=2.2),
                )
                label = f"★ {v:.2f}"
            elif c == v20_idx:
                colour_text = "#facc15" if v < 0.55 else "#9333ea"
                weight = "bold"
            ax.text(c, r, label, ha="center", va="center",
                    fontsize=9, color=colour_text, fontweight=weight)

    ax.set_xticks(np.arange(len(RECIPES)))
    ax.set_xticklabels(RECIPES, fontsize=9, rotation=0)
    ax.set_yticks(np.arange(len(BACKBONES)))
    ax.set_yticklabels([b[0] for b in BACKBONES], fontsize=10)
    ax.set_title(
        "Backbone × wordification factorial — F-2 $c_v$ coherence "
        "(mean across 6 labelled scenes)\n"
        "Green ★ = winner per row; purple = V20 (MI-weighted, label-aware); "
        "hatched = not yet run",
        fontsize=11.5, pad=12,
    )
    ax.set_xlabel("Wordification recipe", fontsize=10)
    ax.set_ylabel("Topic-model backbone", fontsize=10)

    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cb.set_label("F-2 $c_v$ mean", fontsize=9)
    cb.ax.tick_params(labelsize=8)

    fig.text(
        0.01, 0.005,
        "Source: data/derived/v_sweep/{f2_coherence,hdp_backbone,prodlda_backbone,etm_backbone}/ in CAOS_LDA_HSI. "
        "V20 places top-3 in LDA, ProdLDA, ETM; tied with V12/V3 on LDA. "
        "HDP V13/V15/V17/V19 cells deferred to a future cycle.",
        fontsize=7.5, color="#475569", ha="left",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"p4-backbone-factorial.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
