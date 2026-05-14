"""Cross-method ARI agreement matrix grid (axis B-6) — one panel per
scene, full 8x8 ARI matrix.

Reads `cross_method_agreement/<scene>.json` whose `ari_matrix` field
holds the all-pairs ARI between {label, topic-dominant, Felzenszwalb,
SLIC-500, SLIC-2000, patch-15, patch-7, pixel}.
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
       / "cross_method_agreement")

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

ABBREV = {
    "label": "lbl",
    "topic_dominant": "topic",
    "felzenszwalb": "felz",
    "slic_500": "slic500",
    "slic_2000": "slic2k",
    "patch_15": "p15",
    "patch_7": "p7",
    "pixel": "px",
}


def short(names: list) -> list:
    return [ABBREV.get(n, n) for n in names]


def main() -> int:
    fig, axes = plt.subplots(2, 3, figsize=(11.0, 7.5), dpi=150)
    flat = axes.flatten()
    im_last = None
    for ax, (scene_id, label) in zip(flat, SCENES):
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        names = d["method_names"]
        M = np.array(d["ari_matrix"], dtype=float)
        # Mask diagonal
        M_masked = M.copy()
        np.fill_diagonal(M_masked, np.nan)
        masked = np.ma.masked_invalid(M_masked)
        cmap = plt.get_cmap("viridis").copy()
        cmap.set_bad(color="#dddddd")
        im = ax.imshow(masked, cmap=cmap, vmin=0.0, vmax=0.6, aspect="auto")
        im_last = im
        sn = short(names)
        ax.set_xticks(range(len(sn)))
        ax.set_yticks(range(len(sn)))
        ax.set_xticklabels(sn, rotation=45, ha="right", fontsize=7.5)
        ax.set_yticklabels(sn, fontsize=7.5)
        for i in range(len(sn)):
            for j in range(len(sn)):
                if i == j:
                    ax.text(j, i, "—", ha="center", va="center",
                            fontsize=6.5, color="#aaaaaa")
                    continue
                v = M[i, j]
                colour = "white" if v < 0.30 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6.5, color=colour)
        ax.set_title(label, fontsize=10)

    # Hide unused axes
    for ax in flat[len(SCENES):]:
        ax.set_visible(False)

    if im_last is not None:
        cbar = fig.colorbar(im_last, ax=axes, shrink=0.6, pad=0.02,
                            location="right")
        cbar.set_label("ARI", fontsize=9)

    fig.suptitle("Cross-method ARI agreement (axis B-6) — "
                 "8 methods × 6 scenes",
                 fontsize=11, y=1.00)
    fig.tight_layout(rect=[0, 0, 0.92, 0.97])

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "cross-method-ari-grid.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "cross-method-ari-grid.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote cross-method-ari-grid.{{svg,pdf}} to "
          f"{OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
