"""HIDSAG topic × covariate-tag heatmap.

For each HIDSAG subset that exposes non-degenerate covariate tags
(MINERAL1 with P1/P2/P3; GEOCHEM and PORPHYRY with coarse/fine), a
small heatmap of P(covariate-tag | dominant topic) read from
band_masks_hidsag/<subset>/swir/summary.json field
p_covariate_given_topic_dominant. Subsets with a single degenerate
'unknown' covariate (GEOMET, MINERAL2) are omitted from the figure
but flagged in the caption.

Demonstrates whether the canonical topics on HIDSAG carry information
about the available categorical tags - the closest analogue we have
on HIDSAG to the labelled-scene topic-x-class heatmap, given the
continuous mineralogical measurements live in the raw HDF5 source
rather than the derived JSON.
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
       / "band_masks_hidsag")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SUBSETS_TO_SHOW = ["MINERAL1", "GEOCHEM", "PORPHYRY"]


def main() -> int:
    fig, axes = plt.subplots(1, len(SUBSETS_TO_SHOW),
                             figsize=(12.5, 4.0), dpi=150)
    im_last = None
    for ax, subset in zip(axes, SUBSETS_TO_SHOW):
        path = SRC / subset / "swir" / "summary.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        p_cov = d["p_covariate_given_topic_dominant"]
        K = d["topic_count"]
        # collect unique covariate values in order of first appearance
        cov_order = []
        for topic_entry in p_cov:
            for c in topic_entry:
                if c["covariate"] not in cov_order:
                    cov_order.append(c["covariate"])
        C = len(cov_order)
        M = np.zeros((K, C), dtype=float)
        for k in range(K):
            for c in p_cov[k]:
                if c["covariate"] in cov_order:
                    M[k, cov_order.index(c["covariate"])] = c["p"]
        cmap = plt.get_cmap("YlOrRd").copy()
        im = ax.imshow(M, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
        im_last = im
        ax.set_xticks(range(C))
        ax.set_yticks(range(K))
        ax.set_xticklabels(cov_order, fontsize=9)
        ax.set_yticklabels([f"t{k}" for k in range(K)], fontsize=9)
        for i in range(K):
            for j in range(C):
                v = M[i, j]
                if v < 0.03:
                    continue
                colour = "white" if v > 0.55 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=8, color=colour)
        ax.set_title(f"{subset} (K={K}, C={C})", fontsize=10)
        ax.set_xlabel("covariate tag", fontsize=9)
    if im_last is not None:
        cbar = fig.colorbar(im_last, ax=axes, shrink=0.7, pad=0.02,
                            location="right")
        cbar.set_label("P(covariate | dominant topic)", fontsize=9)
    fig.suptitle(
        "HIDSAG topic × covariate-tag heatmaps — three subsets with "
        "non-degenerate tags. GEOMET and MINERAL2 omitted (single "
        "'unknown' covariate, fall-back behaviour from the band-mask "
        "builder).",
        fontsize=10.5, y=1.05,
    )
    fig.tight_layout(rect=[0, 0, 0.92, 0.95])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-topic-covariate.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "hidsag-topic-covariate.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-topic-covariate.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
