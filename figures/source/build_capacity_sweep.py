"""Capacity-K sweep (axis B-4) — perplexity, topic diversity, and
matched-cosine vs K for the six labelled scenes.

Reads `lda_sweep/<scene>.json` whose `grid` field carries per-K
aggregates over 5 seeds.

Three-panel layout (one row per metric), six lines per panel (one per
scene). The recommended_K per scene is marked with a vertical line.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "lda_sweep"

OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENES = [
    ("indian-pines-corrected", "Indian Pines", "#1f77b4"),
    ("salinas-corrected", "Salinas", "#ff7f0e"),
    ("salinas-a-corrected", "Salinas-A", "#2ca02c"),
    ("pavia-university", "Pavia U", "#d62728"),
    ("kennedy-space-center", "KSC", "#9467bd"),
    ("botswana", "Botswana", "#8c564b"),
]


def main() -> int:
    fig, axes = plt.subplots(3, 1, figsize=(7.6, 8.0), dpi=150,
                             sharex=True)
    metrics = [
        ("perplexity_test_mean", "held-out perplexity (mean over 5 seeds)",
         "(a) Held-out perplexity"),
        ("topic_diversity_mean",
         "topic diversity (mean fraction of unique top-15 words)",
         "(b) Topic diversity"),
        ("matched_cosine_mean", "matched-cosine across seeds (mean)",
         "(c) Cross-seed basis cosine"),
    ]

    K_grid_all = None
    for scene_id, scene_label, colour in SCENES:
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            print(f"WARN: missing {path}", file=sys.stderr)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        K_grid = d["K_grid"]
        K_grid_all = K_grid
        rec_K = d["recommended_K"]
        for ax, (field, _, _) in zip(axes, metrics):
            ys = [g[field] for g in d["grid"]]
            ax.plot(K_grid, ys, "-o", color=colour, lw=1.6, ms=5,
                    label=scene_label, alpha=0.95)
            if ax is axes[0]:
                ax.axvline(rec_K, color=colour, ls=":", lw=0.7, alpha=0.5)

    for ax, (_, ylabel, title) in zip(axes, metrics):
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(title, fontsize=9.5)
        ax.grid(alpha=0.25)
    if K_grid_all is not None:
        axes[-1].set_xticks(K_grid_all)
    axes[-1].set_xlabel("topic count K", fontsize=10)
    axes[0].legend(loc="upper right", fontsize=8.5, frameon=False, ncol=2)
    axes[0].text(0.99, 0.02,
                 "dotted verticals = recommended K per scene",
                 transform=axes[0].transAxes, fontsize=7.5,
                 ha="right", va="bottom", color="#666")

    fig.suptitle("LDA capacity sweep (axis B-4) — perplexity, diversity, "
                 "cross-seed basis cosine", fontsize=11, y=0.995)
    fig.tight_layout()

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "capacity-sweep.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "capacity-sweep.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote capacity-sweep.{{svg,pdf}} to {OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
