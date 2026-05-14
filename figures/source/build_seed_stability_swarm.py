"""Seed-stability swarm: per-seed ARI and c_v for ProdLDA + ETM across
the six labelled scenes (N = 5 seeds).

Two panels:
  (a) ARI per seed per (scene, method).
  (b) c_v per seed per (scene, method).

Each (scene, method) column shows the 5 individual seed values as
dots plus a horizontal line at the mean; method colour matches the
coherence-vs-ari scatter.
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
       / "neural_topic_seed_stability")

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
METHODS = ["prodlda", "etm"]
METHOD_COLOUR = {"prodlda": "#d62728", "etm": "#2ca02c"}
METHOD_LABEL = {"prodlda": "ProdLDA", "etm": "ETM"}


def main() -> int:
    aris = {m: [] for m in METHODS}
    cvs = {m: [] for m in METHODS}
    scene_labels = []
    for scene_id, label in SCENES:
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            print(f"WARN: missing {path}", file=sys.stderr)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        scene_labels.append(label)
        for m in METHODS:
            per = d["methods"][m]["per_seed"]
            aris[m].append([p["ari"] for p in per])
            cvs[m].append([p["c_v"] for p in per])

    n_scenes = len(scene_labels)
    x = np.arange(n_scenes)
    width = 0.18  # half-width of jitter

    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.4), dpi=150,
                             sharex=True)
    for ax, panel_data, ylabel, title in (
        (axes[0], aris,
         "KMeans-on-θ vs label ARI (5 seeds)",
         "(a) Cluster ARI per seed"),
        (axes[1], cvs,
         r"topic-word coherence $c_v$ (5 seeds)",
         "(b) Coherence c_v per seed"),
    ):
        for i, m in enumerate(METHODS):
            offsets = (i - 0.5) * 0.42
            for sx, vals in zip(x + offsets, panel_data[m]):
                if not vals:
                    continue
                jitter = np.linspace(-width / 2, width / 2, len(vals))
                ax.scatter(sx + jitter, vals,
                           color=METHOD_COLOUR[m], s=42,
                           alpha=0.85, edgecolor="black", linewidth=0.4,
                           zorder=3,
                           label=METHOD_LABEL[m] if sx == x[0] + offsets
                                 else None)
                mu = float(np.mean(vals))
                ax.plot([sx - width, sx + width], [mu, mu],
                        color=METHOD_COLOUR[m], lw=2.2, zorder=4)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.25, axis="y")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(scene_labels, rotation=15, ha="right",
                            fontsize=9)
    axes[0].legend(loc="upper right", fontsize=9, frameon=False)

    fig.suptitle("Seed-stability swarm (axis B-3): 5 seeds per (scene, method)",
                 fontsize=11, y=0.995)
    fig.tight_layout()

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "seed-stability-swarm.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "seed-stability-swarm.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote seed-stability-swarm.{{svg,pdf}} to {OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
