"""Deep-encoder seed stability at N=30 — complement to the
LDA/ProdLDA/ETM N=5 swarm of axis F-3.

For each scene, plot the per-seed ARI vs ground truth across 30
seeds of four deep encoders (CAE-1D, CAE-2D, CAE-3D, β-VAE) all at
latent dim 8. The N=30 budget is large enough to discriminate
multi-modal posteriors from unimodal ones.
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
       / "deep_seed_stability")
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
METHODS = ["cae_1d_8", "cae_2d_8", "cae_3d_8", "beta_vae_8"]
METHOD_COLOUR = {
    "cae_1d_8": "#1f77b4",
    "cae_2d_8": "#ff7f0e",
    "cae_3d_8": "#2ca02c",
    "beta_vae_8": "#d62728",
}
METHOD_LABEL = {
    "cae_1d_8": "CAE-1D",
    "cae_2d_8": "CAE-2D",
    "cae_3d_8": "CAE-3D",
    "beta_vae_8": "β-VAE",
}


def main() -> int:
    fig, axes = plt.subplots(2, 3, figsize=(11.0, 6.8), dpi=150,
                             sharey=True)
    flat = axes.flatten()
    for ax, (scene_id, label) in zip(flat, SCENES):
        for i, m in enumerate(METHODS):
            path = SRC / f"{scene_id}__{m}__N30.json"
            if not path.exists():
                continue
            with path.open("r", encoding="utf-8") as fh:
                d = json.load(fh)
            aris = d["ari_vs_gt_per_seed"]
            mean = d["ari_vs_gt_summary"]["mean"]
            std = d["ari_vs_gt_summary"]["std"]
            x = i
            # vertical jitter scatter
            jitter = np.random.RandomState(42).normal(0, 0.05, size=len(aris))
            ax.scatter([x + j for j in jitter], aris,
                       color=METHOD_COLOUR[m], s=12, alpha=0.55,
                       edgecolor="black", linewidth=0.2, zorder=3)
            # mean+/-std bar
            ax.plot([x - 0.25, x + 0.25], [mean, mean],
                    color=METHOD_COLOUR[m], lw=2.5, zorder=4)
            ax.errorbar([x], [mean], yerr=[std], color="black",
                        ecolor=METHOD_COLOUR[m], elinewidth=1.4,
                        capsize=4, zorder=4)
        ax.set_xticks(range(len(METHODS)))
        ax.set_xticklabels([METHOD_LABEL[m] for m in METHODS],
                           fontsize=8.5)
        ax.set_title(label, fontsize=10)
        ax.grid(alpha=0.22, axis="y")
    for ax in flat[len(SCENES):]:
        ax.set_visible(False)
    for row in axes:
        row[0].set_ylabel("ARI vs ground-truth label", fontsize=9.5)

    fig.suptitle(
        "Deep-encoder seed stability at N=30 — per-seed dots, "
        "mean bar with std-error bar, 4 methods × 6 scenes",
        fontsize=11, y=1.00,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "deep-seed-stability-n30.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "deep-seed-stability-n30.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote deep-seed-stability-n30.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
