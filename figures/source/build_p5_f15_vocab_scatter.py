"""P5 contrast figure — F-15 LLM-judge alignment vs *nominal* vocabulary |V|.

Companion to build_p5_dispersion_scatter.py. Same recipes, same F-15
values, but the x-axis is the nominal vocabulary size |V| (log scale)
instead of the token-mass dispersion N_eff.

The point of the pair: the relationship against nominal |V| is visibly
looser than against N_eff (lower Spearman ρ, and obvious counterexamples
— V14 sits at |V|=1024 yet scores F-15 0.95 while V3/V12 at |V|=1600
collapse to 0.12/0.16, and V9 at |V|=536 is a trivial 1.0). So one
cannot reduce F-15 to "small vocabularies win"; the operative variable
is how the token *mass* is spread (N_eff), not how many word *types*
exist (|V|).

Output: figures/p5-f15-vocab.{pdf,png}
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_p5_dispersion_scatter import (  # noqa: E402
    OUT_DIR, ANNOTATE, HIGH_DISP, LOW_DISP, collect, spearman,
)


def main() -> int:
    rows = [r for r in collect() if r["v_nom"] is not None]
    if not rows:
        print("ERROR: no data collected", file=sys.stderr)
        return 1

    neff = np.array([r["n_eff"] for r in rows])
    f15 = np.array([r["f15"] for r in rows])
    vnom = np.array([r["v_nom"] for r in rows], dtype=float)

    rho_vnom = spearman(f15, vnom)
    rho_neff = spearman(f15, neff)

    fig, ax = plt.subplots(figsize=(8.4, 6.0))

    for r in rows:
        rec = r["recipe"]
        x, y = float(r["v_nom"]), r["f15"]
        if rec in HIGH_DISP:
            colour, edge, size = "#9333ea", "#581c87", 150
        elif rec in LOW_DISP:
            colour, edge, size = "#16a34a", "#14532d", 130
        else:
            colour, edge, size = "#64748b", "#334155", 95
        ax.scatter(x, y, s=size, c=colour, edgecolors=edge,
                   linewidths=1.1, zorder=3, alpha=0.92)

    # Same-form linear guide on log10(|V|) to make the looser fit explicit.
    order = np.argsort(vnom)
    ax.plot(vnom[order],
            np.poly1d(np.polyfit(np.log10(vnom), f15, 1))(np.log10(vnom))[order],
            color="#cbd5e1", linewidth=1.6, linestyle="--", zorder=1)

    for r in rows:
        rec = r["recipe"]
        if rec not in ANNOTATE:
            continue
        x, y = float(r["v_nom"]), r["f15"]
        dy = 0.035 if y < 0.9 else -0.05
        ax.annotate(
            rec, (x, y), xytext=(x * 1.04, y + dy),
            fontsize=9.5, fontweight="bold",
            color="#9333ea" if rec in HIGH_DISP else ("#16a34a" if rec in LOW_DISP else "#0f172a"),
            ha="center",
        )

    ax.set_xscale("log")
    ax.set_xlabel("Nominal vocabulary size  |V|  (word types, log scale)", fontsize=10.5)
    ax.set_ylabel("F-15 LLM-judge alignment (mean over 6 scenes)", fontsize=10.5)
    ax.set_ylim(-0.05, 1.18)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)

    ax.set_title(
        "P5 contrast — F-15 vs nominal vocabulary |V| (looser than vs N$_{eff}$)\n"
        f"Spearman ρ(F-15, |V|) = {rho_vnom:.2f}   "
        f"(vs ρ(F-15, N$_{{eff}}$) = {rho_neff:.2f}; companion mechanism figure)",
        fontsize=11.5, pad=12,
    )

    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", linestyle="", markersize=9,
               markerfacecolor="#16a34a", markeredgecolor="#14532d",
               label="low N$_{eff}$ recipes"),
        Line2D([0], [0], marker="o", linestyle="", markersize=9,
               markerfacecolor="#9333ea", markeredgecolor="#581c87",
               label="high N$_{eff}$ recipes"),
        Line2D([0], [0], marker="o", linestyle="", markersize=8,
               markerfacecolor="#64748b", markeredgecolor="#334155",
               label="other recipes"),
        Line2D([0], [0], color="#cbd5e1", linestyle="--", linewidth=1.6,
               label="linear fit on log$_{10}$|V|"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=8.3,
              framealpha=0.92, edgecolor="#cbd5e1")

    fig.text(
        0.01, 0.005,
        "Same F-15 values and recipes as p5-dispersion-scatter; x-axis is nominal |V| (from f15 JSON) instead of N_eff. "
        "Counterexamples to the |V| reading: V14 |V|=1024 → F-15 0.95; V9 |V|=536 → 1.0; V3/V12 |V|=1600 → 0.12/0.16. "
        "The dispersion fit (companion figure) is tighter.",
        fontsize=7.0, color="#475569", ha="left",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = OUT_DIR / f"p5-f15-vocab.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)

    print(f"  rho(F15,|V|)={rho_vnom:.3f}  rho(F15,N_eff)={rho_neff:.3f}  n_recipes={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
