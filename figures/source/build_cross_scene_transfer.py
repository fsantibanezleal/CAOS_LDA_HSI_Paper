"""Cross-scene topic-transfer matrix (axis F-10).

5x5 heatmap of macro-F1 on the target scene's labels when the LDA
topic basis is trained on the source scene and only the linear head
is refit on the target. Diagonals are the in-distribution baseline
(same scene). Pavia U is missing because the common-wavelength grid
spans only the VNIR range that AVIRIS scenes plus EO-1 Hyperion
cover (ROSIS 430-860 nm does not intersect cleanly with the SWIR
scenes' canonical grid).
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
       / "cross_scene_transfer" / "transfer_matrix.json")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENE_LABELS = {
    "indian-pines-corrected": "Indian Pines",
    "salinas-corrected": "Salinas",
    "salinas-a-corrected": "Salinas-A",
    "kennedy-space-center": "KSC",
    "botswana": "Botswana",
}


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: missing {SRC}", file=sys.stderr)
        return 2
    with SRC.open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    order = d["scene_order"]
    labels = [SCENE_LABELS.get(s, s) for s in order]
    M = np.array(d["transfer_matrix_macro_f1"], dtype=float)
    n = len(order)

    fig, ax = plt.subplots(figsize=(7.0, 5.6), dpi=150)
    cmap = plt.get_cmap("viridis").copy()
    im = ax.imshow(M, cmap=cmap, vmin=0.0, vmax=0.8, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("target scene (linear head refit)", fontsize=10)
    ax.set_ylabel("source scene (topic basis trained)", fontsize=10)
    for i in range(n):
        for j in range(n):
            v = M[i, j]
            colour = "white" if v < 0.45 else "black"
            on_diag = (i == j)
            weight = "bold" if on_diag else "normal"
            ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                    fontsize=8.5, color=colour, fontweight=weight)
            if on_diag:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           fill=False,
                                           edgecolor="white", lw=1.5))
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("macro-F1 on target", fontsize=9)

    fig.suptitle(
        "F-10 cross-scene topic-transfer macro-F1 "
        "(5×5 matrix; diagonal = in-distribution baseline)",
        fontsize=11, y=0.995,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "cross-scene-transfer.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "cross-scene-transfer.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote cross-scene-transfer.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
