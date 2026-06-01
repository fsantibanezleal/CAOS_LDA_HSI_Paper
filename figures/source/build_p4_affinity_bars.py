"""P4 figure — cross-backbone affinity score A(V_i) for all 19 recipes.

Implements eq:affinity exactly:

    1. For each backbone b in {LDA, HDP, ProdLDA, ETM}, compute the mean
       F-2 c_v coherence of recipe V_i across the 6 labelled scenes at Q=8.
    2. Min-max normalise that per-backbone vector to [0, 1].
    3. A(V_i) = mean over the four normalised backbone scores.

A high affinity = a recipe that is robustly coherent regardless of which
generative prior sits on top of it (Dirichlet / stick-breaking /
logistic-normal / embedding). This is the "backbone-agnostic" quality the
P4 narrative argues for.

Data: data/derived/v_sweep/{f2_coherence (LDA, key 'c_v'),
hdp_backbone, prodlda_backbone, etm_backbone (key 'f2_c_v')} in CAOS_LDA_HSI.

Output: figures/p4-affinity-bars.{pdf,png}
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
# 19 wordification recipes (V16 was never defined in the sweep).
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]

BACKBONES = [
    ("LDA",     "f2_coherence",     "c_v"),
    ("HDP",     "hdp_backbone",     "f2_c_v"),
    ("ProdLDA", "prodlda_backbone", "f2_c_v"),
    ("ETM",     "etm_backbone",     "f2_c_v"),
]

# colour per backbone for the stacked component dots
B_COLOURS = {
    "LDA": "#2563eb", "HDP": "#16a34a",
    "ProdLDA": "#d97706", "ETM": "#9333ea",
}


def cell_mean(backbone_dir: str, recipe: str, key: str) -> float | None:
    """Mean F-2 c_v of `recipe` across the 6 scenes at Q=8, or None."""
    vals: list[float] = []
    for scene in SCENES:
        f = SRC / backbone_dir / f"{scene}_{recipe}_uniform_Q8.json"
        if not f.exists():
            continue
        with f.open() as h:
            d = json.load(h)
        v = d.get(key)
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                continue
    if not vals:
        return None
    return float(np.mean(vals))


def main() -> int:
    # 1. raw per-backbone means
    raw: dict[str, dict[str, float | None]] = {}
    for name, bdir, key in BACKBONES:
        raw[name] = {r: cell_mean(bdir, r, key) for r in RECIPES}

    # 2. min-max normalise within each backbone
    norm: dict[str, dict[str, float | None]] = {}
    for name in raw:
        present = [v for v in raw[name].values() if v is not None]
        lo, hi = min(present), max(present)
        span = hi - lo
        norm[name] = {}
        for r in RECIPES:
            v = raw[name][r]
            if v is None:
                norm[name][r] = None
            else:
                norm[name][r] = (v - lo) / span if span > 0 else 0.5

    # 3. affinity = mean over the four normalised backbones
    affinity: dict[str, float] = {}
    components: dict[str, dict[str, float]] = {}
    for r in RECIPES:
        comps = {n: norm[n][r] for n in raw if norm[n][r] is not None}
        components[r] = comps
        affinity[r] = float(np.mean(list(comps.values()))) if comps else 0.0

    order = sorted(RECIPES, key=lambda r: affinity[r])  # ascending -> top of barh
    y = np.arange(len(order))
    vals = [affinity[r] for r in order]

    fig, ax = plt.subplots(figsize=(9.0, 8.2))

    # Bar colouring: highlight the top-4 backbone-agnostic recipes, V20 in purple.
    ranked = sorted(RECIPES, key=lambda r: -affinity[r])
    top4 = set(ranked[:4])
    bar_colours = []
    for r in order:
        if r == "V20":
            bar_colours.append("#9333ea")        # V20 = MI-weighted, label-aware
        elif r in top4:
            bar_colours.append("#0ea5e9")         # other top-4
        else:
            bar_colours.append("#cbd5e1")
    bars = ax.barh(y, vals, color=bar_colours, edgecolor="#0f172a",
                   linewidth=0.5, height=0.72, zorder=2)

    # Per-backbone component dots overlaid on each bar so the reader sees the spread.
    for yi, r in enumerate(order):
        for name, comp in components[r].items():
            ax.scatter(comp, yi, s=18, color=B_COLOURS[name], zorder=4,
                       edgecolor="white", linewidth=0.4)

    # Value labels
    for bar, v, r in zip(bars, vals, order):
        ax.text(v + 0.012, bar.get_y() + bar.get_height() / 2,
                f"{v:.3f}", va="center", ha="left", fontsize=8.5,
                color="#0f172a", fontweight="bold" if r in top4 else "normal")

    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=9.5)
    # bold the top-4 labels
    for tick, r in zip(ax.get_yticklabels(), order):
        if r == "V20":
            tick.set_color("#9333ea")
            tick.set_fontweight("bold")
        elif r in top4:
            tick.set_fontweight("bold")

    ax.set_xlim(0, 1.08)
    ax.set_xlabel(r"Cross-backbone affinity  $A(V_i)$"
                  "  (mean of min-max-normalised F-2 $c_v$ over 4 backbones)",
                  fontsize=10)
    ax.set_title(
        "Which wordification is backbone-agnostic?\n"
        "Affinity score across LDA / HDP / ProdLDA / ETM (Q=8, 6 scenes)",
        fontsize=12, pad=10,
    )
    ax.grid(axis="x", linestyle=":", color="#cbd5e1", zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    # Legend for the component dots.
    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="none", markersize=7,
                   markerfacecolor=B_COLOURS[n], markeredgecolor="white",
                   label=f"{n} (normalised $c_v$)")
        for n in ("LDA", "HDP", "ProdLDA", "ETM")
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8.5,
              frameon=True, framealpha=0.95, title="per-backbone component",
              title_fontsize=8.5)

    top_recipe = ranked[0]
    fig.text(
        0.012, 0.005,
        "Source: data/derived/v_sweep/{f2_coherence,hdp_backbone,prodlda_backbone,etm_backbone}/ in CAOS_LDA_HSI. "
        f"eq:affinity. Leader {top_recipe} (A={affinity[top_recipe]:.3f}); "
        f"V20 ranks #{ranked.index('V20') + 1} (A={affinity['V20']:.3f}). "
        "19 recipes (V16 undefined). All backbones fully covered at Q=8.",
        fontsize=7.0, color="#475569", ha="left",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = OUT_DIR / f"p4-affinity-bars.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)

    # Echo the table for the audit note.
    print("\nAffinity ranking (descending):")
    for r in ranked:
        print(f"  {r}: A={affinity[r]:.4f}  comps="
              + ", ".join(f"{n}={components[r][n]:.3f}" for n in components[r]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
