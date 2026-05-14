"""Build coherence-vs-ARI scatter exposing the LDA vs ProdLDA vs ETM
tradeoff on HSI.

Six scenes x three methods = 18 points. ARI on the y-axis (cluster
quality vs ground-truth label, KMeans on theta) and c_v on the x-axis
(topic-word coherence). Each scene's three method points are connected
by light lines so the per-scene shape of the tradeoff is visible.

Demonstrates the recommendation in journal Section V: rank by ARI
alone and ProdLDA loses; rank by c_v alone and ProdLDA wins; the
combined view is the only honest summary.
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
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "neural_topic_comparison"

OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENES = [
    ("indian-pines-corrected", "Indian Pines"),
    ("salinas-corrected", "Salinas"),
    ("salinas-a-corrected", "Salinas-A"),
    ("pavia-university", "Pavia U"),
    ("kennedy-space-center", "KSC"),
    ("botswana", "Botswana"),
]
METHODS = ["lda", "prodlda", "etm"]
METHOD_COLOUR = {"lda": "#1f77b4", "prodlda": "#d62728", "etm": "#2ca02c"}
METHOD_LABEL = {"lda": "LDA (online VB)",
                "prodlda": "ProdLDA",
                "etm": "ETM"}


def main() -> int:
    points = {m: {"x": [], "y": [], "scene": []} for m in METHODS}
    per_scene = {}
    for scene_id, scene_label in SCENES:
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            print(f"WARN: missing {path}", file=sys.stderr)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        per_scene[scene_label] = {}
        for m in METHODS:
            r = d["methods"][m]
            ari = r["downstream_kmeans_vs_label"]["ari"]
            cv = r["coherence"]["c_v"]
            points[m]["x"].append(cv)
            points[m]["y"].append(ari)
            points[m]["scene"].append(scene_label)
            per_scene[scene_label][m] = (cv, ari)

    fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=150)

    # Per-scene triangle connectors
    for scene_label, mres in per_scene.items():
        xs = [mres[m][0] for m in METHODS]
        ys = [mres[m][1] for m in METHODS]
        xs_closed = xs + [xs[0]]
        ys_closed = ys + [ys[0]]
        ax.plot(xs_closed, ys_closed, "-", color="#bbbbbb", lw=0.8,
                alpha=0.6, zorder=1)

    # Per-method scatter
    for m in METHODS:
        ax.scatter(points[m]["x"], points[m]["y"],
                   color=METHOD_COLOUR[m], s=90, marker="o",
                   edgecolor="black", linewidth=0.6,
                   label=METHOD_LABEL[m], zorder=3)
        for x, y, sc in zip(points[m]["x"], points[m]["y"],
                            points[m]["scene"]):
            ax.annotate(sc, (x, y), fontsize=7.0,
                        xytext=(4, 4), textcoords="offset points",
                        color="#444", zorder=4)

    ax.axvline(0.5, ls=":", color="#bbbbbb", lw=0.6)
    ax.axhline(0.3, ls=":", color="#bbbbbb", lw=0.6)
    ax.set_xlabel(r"topic-word coherence $c_v$ (top-15 words, Röder 2015)",
                  fontsize=10)
    ax.set_ylabel(r"downstream KMeans-vs-label ARI", fontsize=10)
    ax.set_title("Coherence vs cluster ARI on HSI — "
                 "LDA, ProdLDA, ETM on six scenes",
                 fontsize=10)
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=9, frameon=False)

    # Add annotation about the tradeoff
    ax.text(0.04, 0.96,
            "ProdLDA dominates c_v; LDA tends to dominate ARI.\n"
            "Per-scene triangles (grey) show the local tradeoff shape.",
            transform=ax.transAxes, fontsize=8, va="top", ha="left",
            color="#555",
            bbox=dict(facecolor="#fafafa", edgecolor="#dddddd",
                      boxstyle="round,pad=0.4"))

    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "coherence-vs-ari.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "coherence-vs-ari.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote coherence-vs-ari.{{svg,pdf}} to "
          f"{OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
