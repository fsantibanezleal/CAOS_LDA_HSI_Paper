"""Topic pairwise distance heatmap — cosine + JS distance between
phi_k and phi_j per scene.

Quantitatively answers 'are topic spectra different?' for every pair
of topics within a scene. A heatmap of pairwise distances shows
which topic pairs are close (potentially redundant) and which are
far apart (clearly distinct).

Six-panel 3x2 grid, one cosine-distance heatmap per scene.
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
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "topic_views"
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENES = [
    ("indian-pines-corrected", "Indian Pines K=12"),
    ("salinas-corrected", "Salinas K=12"),
    ("salinas-a-corrected", "Salinas-A K=6"),
    ("pavia-university", "Pavia U K=9"),
    ("kennedy-space-center", "KSC K=12"),
    ("botswana", "Botswana K=12"),
]


def main() -> int:
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.5), dpi=150)
    flat = axes.flatten()
    im_last = None
    for ax, (scene_id, label) in zip(flat, SCENES):
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            tv = json.load(fh)
        D = np.array(tv["topic_distance_cosine"], dtype=float)
        K = D.shape[0]

        # Mask diagonal (always 0)
        D_show = D.copy()
        np.fill_diagonal(D_show, np.nan)
        cmap = plt.get_cmap("viridis").copy()
        cmap.set_bad(color="#dddddd")
        masked = np.ma.masked_invalid(D_show)
        im = ax.imshow(masked, cmap=cmap, vmin=0.0, vmax=1.0,
                       aspect="auto")
        im_last = im
        ax.set_xticks(range(K))
        ax.set_yticks(range(K))
        ax.set_xticklabels([f"t{k}" for k in range(K)], fontsize=7)
        ax.set_yticklabels([f"t{k}" for k in range(K)], fontsize=7)
        for i in range(K):
            for j in range(K):
                if i == j:
                    continue
                v = D[i, j]
                colour = "white" if v < 0.5 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6.0, color=colour)
        ax.set_title(label, fontsize=10)

    for ax in flat[len(SCENES):]:
        ax.set_visible(False)

    if im_last is not None:
        cbar = fig.colorbar(im_last, ax=axes, shrink=0.6, pad=0.02,
                            location="right")
        cbar.set_label("cosine distance d(φ_i, φ_j)", fontsize=9)

    fig.suptitle(
        "Pairwise topic-spectrum cosine distance — "
        "high values = visually distinct basis spectra, "
        "low values = similar basis spectra",
        fontsize=10.5, y=1.00,
    )
    fig.tight_layout(rect=[0, 0, 0.92, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "topic-pairwise-distance.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "topic-pairwise-distance.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote topic-pairwise-distance.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
