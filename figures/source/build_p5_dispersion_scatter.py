"""P5 mechanism figure — F-15 LLM-judge alignment vs token-mass dispersion.

The P5 narrative: the F-15 alignment metric does NOT track nominal
vocabulary size |V|; it tracks *token-mass dispersion* — how spread the
corpus token mass is across the vocabulary that is actually exercised.

Dispersion is measured as the effective vocabulary size

    N_eff = exp(H(p))      with   p = corpus marginal token distribution,
                                   H in nats  (== 2**H_bits)

computed per (scene, recipe) from the wordification doc-term matrix and
averaged across the 6 labelled scenes. N_eff answers "how many tokens
carry the bulk of the corpus mass?" — V2/V8/V10 collapse to ~4-7
effective tokens; V3/V12/V20 spread mass over ~460-475.

The self-judgment F-15 rule (top-10 doc/topic overlap) is trivially
satisfied when N_eff is small (every topic and every doc draws from the
same handful of tokens) and rarely satisfied when N_eff is large. So
F-15 is a *dispersion meter*, not a coherence meter — the key
methodological caveat for P5.

The contrast figure (build_p5_f15_vocab_scatter.py) plots the same F-15
values against nominal |V| on a log axis, where the relationship is
markedly weaker. Together they refute "F-15 just measures vocab size".

Ground-truth anchors (internal_tech_report/03_v_sweep_results.md):
  V12 F-15 0.158, V3 0.117  (large N_eff -> low alignment)
  V20 F-15 0.642            (large N_eff, mid alignment)
  V14 F-15 0.950            (nominal |V|=1024 but N_eff only ~67 -> high)

Output: figures/p5-dispersion-scatter.{pdf,png}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import sparse  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
HSI_ROOT = REPO_ROOT.parent / "CAOS_LDA_HSI"
SRC = HSI_ROOT / "data" / "derived" / "v_sweep"
DOC_TERM_ROOT = HSI_ROOT / "data" / "local" / "wordifications"
OUT_DIR = REPO_ROOT / "figures"

SCENES = [
    "indian-pines-corrected", "salinas-corrected", "salinas-a-corrected",
    "pavia-university", "kennedy-space-center", "botswana",
]
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]

# Recipes to annotate with text labels: low-dispersion-trivial winners and
# the high-dispersion recipes that the P5 narrative cares about.
ANNOTATE = {"V2", "V3", "V8", "V10", "V12", "V14", "V15", "V17", "V20"}
# Recipes highlighted as the headline contrast (P5 leaders / losers).
HIGH_DISP = {"V3", "V12", "V20", "V17"}   # large N_eff
LOW_DISP = {"V2", "V8", "V10", "V14"}     # small N_eff


def neff_corpus(scene: str, recipe: str) -> float | None:
    """Effective vocabulary N_eff = 2**H(corpus marginal token dist).

    Computed directly from the doc-term matrix so the metric is identical
    for every recipe (the derived wordification JSONs only cover V1-V12).
    """
    p = DOC_TERM_ROOT / recipe / "uniform_Q8" / scene / "doc_term.npz"
    if not p.exists():
        return None
    m = sparse.load_npz(p).tocsc().astype(np.float64)
    col = np.asarray(m.sum(axis=0)).ravel()
    tot = col.sum()
    if tot <= 0:
        return None
    pp = col[col > 0] / tot
    h_bits = float(-np.sum(pp * np.log2(pp)))
    return float(2.0 ** h_bits)


def f15_value(scene: str, recipe: str) -> tuple[float | None, int | None]:
    f = SRC / "f15_llm_alignment" / f"{scene}_{recipe}_uniform_Q8.json"
    if not f.exists():
        return None, None
    with f.open(encoding="utf-8") as h:
        d = json.load(h)
    return d.get("f15_alignment"), d.get("V")


def collect() -> list[dict]:
    rows: list[dict] = []
    for recipe in RECIPES:
        neffs, f15s, vnoms = [], [], []
        for scene in SCENES:
            n = neff_corpus(scene, recipe)
            f, v = f15_value(scene, recipe)
            if n is not None:
                neffs.append(n)
            if f is not None:
                f15s.append(float(f))
                if v is not None:
                    vnoms.append(int(v))
        if not neffs or not f15s:
            continue
        rows.append({
            "recipe": recipe,
            "n_eff": float(np.mean(neffs)),
            "f15": float(np.mean(f15s)),
            "v_nom": int(vnoms[0]) if vnoms else None,
            "n_scenes": len(f15s),
        })
    return rows


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = np.argsort(np.argsort(a))
    br = np.argsort(np.argsort(b))
    return float(np.corrcoef(ar, br)[0, 1])


def main() -> int:
    rows = collect()
    if not rows:
        print("ERROR: no data collected", file=sys.stderr)
        return 1

    neff = np.array([r["n_eff"] for r in rows])
    f15 = np.array([r["f15"] for r in rows])
    vnom = np.array([r["v_nom"] for r in rows], dtype=float)

    rho_neff = spearman(f15, neff)
    rho_vnom = spearman(f15, vnom)

    fig, ax = plt.subplots(figsize=(8.4, 6.0))

    for r in rows:
        rec = r["recipe"]
        x, y = r["n_eff"], r["f15"]
        if rec in HIGH_DISP:
            colour, edge, size = "#9333ea", "#581c87", 150
        elif rec in LOW_DISP:
            colour, edge, size = "#16a34a", "#14532d", 130
        else:
            colour, edge, size = "#64748b", "#334155", 95
        ax.scatter(x, y, s=size, c=colour, edgecolors=edge,
                   linewidths=1.1, zorder=3, alpha=0.92)

    # Trend (rank-monotone): LOWESS-free simple ordered guide on log x.
    order = np.argsort(neff)
    ax.plot(neff[order], np.poly1d(np.polyfit(np.log10(neff), f15, 1))(np.log10(neff))[order],
            color="#cbd5e1", linewidth=1.6, linestyle="--", zorder=1,
            label="linear fit on log$_{10}$ N$_{eff}$")

    # Annotations
    for r in rows:
        rec = r["recipe"]
        if rec not in ANNOTATE:
            continue
        x, y = r["n_eff"], r["f15"]
        dy = 0.035 if y < 0.9 else -0.05
        dx = 1.04
        ax.annotate(
            rec, (x, y), xytext=(x * dx, y + dy),
            fontsize=9.5, fontweight="bold",
            color="#9333ea" if rec in HIGH_DISP else ("#16a34a" if rec in LOW_DISP else "#0f172a"),
            ha="center",
        )

    ax.set_xscale("log")
    ax.set_xlabel(
        "Token-mass dispersion  N$_{eff}$ = exp $H(p)$  "
        "(effective vocabulary, mean over 6 scenes, log scale)",
        fontsize=10.5,
    )
    ax.set_ylabel("F-15 LLM-judge alignment (mean over 6 scenes)", fontsize=10.5)
    ax.set_ylim(-0.05, 1.18)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)

    ax.set_title(
        "P5 mechanism — F-15 alignment tracks token-mass dispersion, not coherence\n"
        f"Spearman ρ(F-15, N$_{{eff}}$) = {rho_neff:.2f}   "
        f"(vs ρ(F-15, |V|) = {rho_vnom:.2f}; see companion figure)",
        fontsize=11.5, pad=14,
    )

    # Legend proxies
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="o", linestyle="", markersize=9,
               markerfacecolor="#16a34a", markeredgecolor="#14532d",
               label="low N$_{eff}$ (mass collapses → F-15 trivially high)"),
        Line2D([0], [0], marker="o", linestyle="", markersize=9,
               markerfacecolor="#9333ea", markeredgecolor="#581c87",
               label="high N$_{eff}$ (mass spreads → top-10 overlap rare)"),
        Line2D([0], [0], marker="o", linestyle="", markersize=8,
               markerfacecolor="#64748b", markeredgecolor="#334155",
               label="other recipes"),
        Line2D([0], [0], color="#cbd5e1", linestyle="--", linewidth=1.6,
               label="linear fit on log$_{10}$ N$_{eff}$"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=8.3,
              framealpha=0.92, edgecolor="#cbd5e1")

    fig.text(
        0.01, 0.005,
        "N$_{eff}$ = 2$^{H(p)}$ with p the corpus marginal token distribution, computed from "
        "data/local/wordifications/<recipe>/uniform_Q8/<scene>/doc_term.npz (matches derived corpus_marginal_entropy_bits). "
        "F-15 from data/derived/v_sweep/f15_llm_alignment/. "
        "V14 has nominal |V|=1024 yet N_eff≈67 → F-15 0.95, while V3/V12 (|V|=1600, N_eff≈465) collapse to 0.12/0.16: "
        "F-15 is a dispersion meter, refuting the pure |V| reading.",
        fontsize=7.0, color="#475569", ha="left",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = OUT_DIR / f"p5-dispersion-scatter.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)

    print(f"  rho(F15,N_eff)={rho_neff:.3f}  rho(F15,|V|)={rho_vnom:.3f}  n_recipes={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
