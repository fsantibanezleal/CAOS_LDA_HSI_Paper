"""HIDSAG cross-preprocessing stability (axis F-9) figure.

For each HIDSAG subset, refit the canonical LDA under four
preprocessing policies (baseline_raw, bad_band_mask, bad_band_mask
+ SNV, bad_band_mask + SavGol + SNV) and report the pairwise matched
Jaccard@top-15 between every pair of refits. A subset whose canonical
topics survive preprocessing changes will have off-diagonal mean
close to 1; a subset whose topics depend strongly on preprocessing
will collapse near 0.

Five-panel layout, one 4x4 Jaccard heatmap per subset.
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
       / "hidsag_cross_preprocessing_stability")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SUBSETS = [
    ("GEOMET", "GEOMET"),
    ("MINERAL1", "MINERAL1"),
    ("MINERAL2", "MINERAL2"),
    ("GEOCHEM", "GEOCHEM"),
    ("PORPHYRY", "PORPHYRY"),
]

POLICY_LABELS = {
    "baseline_raw": "raw",
    "heuristic_bad_band_mask": "bad-band",
    "heuristic_bad_band_mask_snv": "bb + SNV",
    "heuristic_bad_band_mask_savgol_snv": "bb + SG + SNV",
}


def short_policy(p: str) -> str:
    return POLICY_LABELS.get(p, p)


def main() -> int:
    fig, axes = plt.subplots(2, 3, figsize=(11.0, 7.0), dpi=150)
    flat = axes.flatten()
    im_last = None
    for ax, (subset_id, label) in zip(flat, SUBSETS):
        path = SRC / f"{subset_id}.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        policies = d["policies"]
        M = np.array(d["pairwise_matched_jaccard_top15_mean_matrix"],
                     dtype=float)
        off_mean = d["off_diagonal_summary"]["off_diagonal_mean"]
        K = d["topic_count"]

        cmap = plt.get_cmap("viridis").copy()
        im = ax.imshow(M, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
        im_last = im
        n = len(policies)
        labels = [short_policy(p) for p in policies]
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        for i in range(n):
            for j in range(n):
                v = M[i, j]
                colour = "white" if v < 0.5 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=7.5, color=colour)
        ax.set_title(
            f"{label}  ·  K={K}  ·  off-diag mean = {off_mean:.3f}",
            fontsize=9.5,
        )

    for ax in flat[len(SUBSETS):]:
        ax.set_visible(False)

    if im_last is not None:
        cbar = fig.colorbar(im_last, ax=axes, shrink=0.6, pad=0.02,
                            location="right")
        cbar.set_label("matched Jaccard@top-15", fontsize=9)

    fig.suptitle(
        "F-9 cross-preprocessing stability on HIDSAG — "
        "pairwise matched Jaccard@top-15 between LDA refits",
        fontsize=11, y=1.00,
    )
    fig.tight_layout(rect=[0, 0, 0.92, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-preprocessing-stability.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "hidsag-preprocessing-stability.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-preprocessing-stability.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
