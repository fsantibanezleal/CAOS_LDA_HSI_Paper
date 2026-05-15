"""HIDSAG mosaic / fluctuation heatmap: P(quartile-bin | topic) for
the most discriminative continuous variable per subset.

Bins each continuous variable into quartiles (Q1..Q4) over the full
subset distribution, then computes the conditional matrix
P(quartile-bin | dominant topic). Rendered as a heatmap with cells
annotated by probability. Companion to the ridge plot (c208): the
ridge shows the continuous distribution; the mosaic discretises and
makes the conditional-ordering claim directly readable.

Reference: Hofmann 2008 mosaic-plot family (Springer Handbook of
Data Visualisation pp. 617-642); Friendly 1994 mosaic displays
(JASA 89:190-200).

Three subsets selected (PORPHYRY, GEOMET, MINERAL1) for the
strongest discrimination signal.
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
SRC = (REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
       / "hidsag_topic_measurements")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SUBSETS = [
    ("PORPHYRY", "Bt (%)"),
    ("GEOMET", "Cu rec"),
    ("MINERAL1", "Albite"),
]


def panel(ax, payload: dict, var: str) -> None:
    K = payload["topic_count"]
    records = payload["records"]
    values = []
    topic_of = []
    for r in records:
        v = r["vars"].get(var)
        if v is None:
            continue
        values.append(v)
        topic_of.append(r["dominant_topic"])
    if not values:
        ax.set_visible(False); return
    values = np.array(values, dtype=float)
    topic_of = np.array(topic_of)
    edges = np.quantile(values, [0, 0.25, 0.5, 0.75, 1.0])
    # ensure uniqueness; fall back to linspace if degenerate
    if len(np.unique(edges)) < 5:
        edges = np.linspace(values.min(), values.max(), 5)
    bin_idx = np.clip(np.digitize(values, edges[1:-1]), 0, 3)
    Q = 4
    M = np.zeros((K, Q), dtype=float)
    counts_per_topic = np.zeros(K, dtype=int)
    for t, b in zip(topic_of, bin_idx):
        M[t, b] += 1
        counts_per_topic[t] += 1
    row_sum = M.sum(axis=1, keepdims=True)
    row_sum[row_sum == 0] = 1
    M = M / row_sum
    cmap = plt.get_cmap("YlOrRd")
    im = ax.imshow(M, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(range(Q))
    ax.set_yticks(range(K))
    ax.set_xticklabels([f"Q{q + 1}\n[{edges[q]:.1f},\n{edges[q + 1]:.1f}]"
                        for q in range(Q)], fontsize=7)
    ax.set_yticklabels([f"t{k}  n={counts_per_topic[k]}"
                        for k in range(K)], fontsize=8)
    for i in range(K):
        for j in range(Q):
            v = M[i, j]
            if v < 0.05:
                continue
            colour = "white" if v > 0.55 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=7.5, color=colour)
    ax.set_title(f"{payload['subset_code']}: P(bin | topic) on {var}",
                 fontsize=9.5)


def main() -> int:
    fig, axes = plt.subplots(1, len(SUBSETS), figsize=(13.5, 4.4),
                             dpi=150)
    for ax, (subset, var) in zip(axes, SUBSETS):
        path = SRC / f"{subset}.json"
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        panel(ax, payload, var)
    fig.suptitle(
        "HIDSAG mosaic: P(quartile-bin | dominant topic) on a "
        "selected continuous variable per subset. Bins are scene-wide "
        "quartiles; rows are normalised so each topic sums to 1.",
        fontsize=10.5, y=1.04,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-measurement-mosaic.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "hidsag-measurement-mosaic.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-measurement-mosaic.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
