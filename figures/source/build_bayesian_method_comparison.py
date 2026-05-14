"""Build the hierarchical-Bayesian method-comparison figure for the
journal manuscript.

Four-panel layout:
  (a) Labelled-scene forest plot: posterior mu_m +/- HDI94 per method.
  (b) Labelled-scene pairwise P[A > B] heatmap.
  (c) HIDSAG forest plot: posterior mu_m +/- HDI94 per method.
  (d) HIDSAG pairwise P[A > B] heatmap.

The contrast between (a-b) and (c-d) surfaces the HIDSAG inversion
discussed in Section V of the journal paper: on labelled scenes
topic-routed-soft and raw-logistic are statistically indistinguishable
(P[A>B] = 0.641), on HIDSAG the topic-logistic falls well below
raw-logistic (P[A>B] = 0.0).

Source artefacts:
  - data/derived/method_statistics_labelled/cross_classification_bayesian.json
  - data/derived/method_statistics_hidsag/cross_classification_bayesian.json
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
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
LBL_JSON = SRC / "method_statistics_labelled" / "cross_classification_bayesian.json"
HID_JSON = SRC / "method_statistics_hidsag" / "cross_classification_bayesian.json"

OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SHORT = {
    "pca_K_logistic": "PCA-K + logreg",
    "raw_logistic": "raw + logreg",
    "theta_logistic": "θ + logreg",
    "topic_routed_hard": "topic-routed (hard)",
    "topic_routed_soft": "topic-routed (soft)",
    "cube_topic_logistic_regression": "cube-topic + logreg",
    "pca_logistic_regression": "PCA + logreg",
    "raw_logistic_regression": "raw + logreg",
    "region_topic_logistic_regression": "region-topic + logreg",
    "topic_logistic_regression": "θ + logreg",
}


def forest_panel(ax, payload, title: str) -> list:
    posts = payload["method_posteriors"]
    names = [p["method"] for p in posts]
    mu = np.array([p["posterior_mean"] for p in posts])
    lo = np.array([p["hdi94_lo"] for p in posts])
    hi = np.array([p["hdi94_hi"] for p in posts])

    order = np.argsort(mu)
    names_o = [names[i] for i in order]
    labels = [SHORT.get(n, n) for n in names_o]
    mu_o = mu[order]
    lo_o = lo[order]
    hi_o = hi[order]

    y = np.arange(len(names_o))
    # HDI94 bar
    ax.hlines(y, lo_o, hi_o, color="#999999", lw=2.2)
    # mean dot
    ax.plot(mu_o, y, "o", color="#1f77b4", ms=7,
            markeredgecolor="black", markeredgewidth=0.6)
    # vertical reference at 0
    ax.axvline(0.0, ls="--", color="#aaaaaa", lw=0.8)
    # value annotation
    for yi, m, l, h in zip(y, mu_o, lo_o, hi_o):
        ax.text(h + 0.04, yi, f"μ={m:.3f}", fontsize=7.5, va="center",
                color="#333")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlabel(r"posterior $\mu_m$ (NUTS, 2 chains, 1000 draws)",
                  fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="x", alpha=0.25)
    return names_o


def pairwise_panel(ax, payload, names_in_order: list, title: str) -> None:
    pair = payload["pairwise_p_a_gt_b"]
    n = len(names_in_order)
    M = np.full((n, n), np.nan, dtype=float)
    for i, a in enumerate(names_in_order):
        for j, b in enumerate(names_in_order):
            if a == b:
                continue
            M[i, j] = pair[a][b]
    cmap = plt.get_cmap("RdYlGn").copy()
    cmap.set_bad(color="#dddddd")
    masked = np.ma.masked_invalid(M)
    im = ax.imshow(masked, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    short = [SHORT.get(n, n) for n in names_in_order]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(short, rotation=30, ha="right", fontsize=7.5)
    ax.set_yticklabels(short, fontsize=7.5)
    for i in range(n):
        for j in range(n):
            if np.isnan(M[i, j]):
                ax.text(j, i, "—", ha="center", va="center", fontsize=7.5,
                        color="#777")
                continue
            v = M[i, j]
            colour = "white" if (v < 0.30 or v > 0.70) else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=7.5, color=colour)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("vs method B (col)", fontsize=9)
    ax.set_ylabel("method A (row)", fontsize=9)


def main() -> int:
    for p in (LBL_JSON, HID_JSON):
        if not p.exists():
            print(f"ERROR: missing artefact: {p}", file=sys.stderr)
            return 2

    with LBL_JSON.open("r", encoding="utf-8") as fh:
        labelled = json.load(fh)
    with HID_JSON.open("r", encoding="utf-8") as fh:
        hidsag = json.load(fh)

    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.0), dpi=150,
                             gridspec_kw={"width_ratios": [1.0, 1.05]})
    lbl_order = forest_panel(axes[0, 0], labelled,
                             "(a) Labelled scenes — forest plot (μ ± HDI94)")
    pairwise_panel(axes[0, 1], labelled, lbl_order,
                   "(b) Labelled scenes — P[A > B]")
    hid_order = forest_panel(axes[1, 0], hidsag,
                             "(c) HIDSAG mineral subsets — forest plot (μ ± HDI94)")
    pairwise_panel(axes[1, 1], hidsag, hid_order,
                   "(d) HIDSAG — P[A > B]")

    fig.suptitle(
        "Hierarchical-Bayesian method comparison (axis B-1) — "
        "NUTS, 1000 draws, 2 chains",
        fontsize=11, y=1.00,
    )
    fig.tight_layout()

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "bayesian-method-comparison.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "bayesian-method-comparison.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote bayesian-method-comparison.{{svg,pdf}} "
          f"(forest + pairwise P[A>B] heatmap) to {OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
