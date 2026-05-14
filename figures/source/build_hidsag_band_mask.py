"""HIDSAG band-mask sweep figure (axis F-5 complement on the
mineralogical side).

HIDSAG has no per-pixel ground-truth label, so the paired-ARI metric
used on the labelled scenes does not apply directly. Instead this
figure surfaces three reportable per-(subset, mask) quantities:
  (a) train perplexity of the masked LDA refit,
  (b) mean per-document max-theta (confidence proxy),
  (c) number of bands kept after the mask (sensor floor: 268).

Reads `band_masks_hidsag/index.json`.
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
       / "band_masks_hidsag" / "index.json")

OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SUBSETS = ["GEOMET", "MINERAL1", "MINERAL2", "GEOCHEM", "PORPHYRY"]
MASKS = ["vnir", "swir", "no_water", "top_50_fisher"]
MASK_LABELS = ["VNIR\n(18 bands)", "SWIR\n(250)", "no-water\n(222)",
               "top-50\nvariance"]


def build_matrix(entries, field):
    M = np.full((len(SUBSETS), len(MASKS)), np.nan, dtype=float)
    for e in entries:
        sub = e["subset_code"]
        msk = e["mask_id"]
        if sub in SUBSETS and msk in MASKS:
            M[SUBSETS.index(sub), MASKS.index(msk)] = e[field]
    return M


def heatmap(ax, M, title, cmap, fmt, vmin=None, vmax=None) -> None:
    cm = plt.get_cmap(cmap).copy()
    cm.set_bad(color="#dddddd")
    masked = np.ma.masked_invalid(M)
    im = ax.imshow(masked, cmap=cm, aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(MASK_LABELS)))
    ax.set_yticks(range(len(SUBSETS)))
    ax.set_xticklabels(MASK_LABELS, fontsize=8.5)
    ax.set_yticklabels(SUBSETS, fontsize=9)
    ax.set_title(title, fontsize=10)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center",
                        fontsize=8, color="#777")
                continue
            ref = (vmax if vmax is not None else np.nanmax(M))
            colour = "white" if v < ref * 0.5 else "black"
            ax.text(j, i, fmt.format(v), ha="center", va="center",
                    fontsize=8, color=colour)
    return im


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: missing {SRC}", file=sys.stderr)
        return 2
    with SRC.open("r", encoding="utf-8") as fh:
        idx = json.load(fh)

    perp = build_matrix(idx["entries"], "perplexity_train")
    conf = build_matrix(idx["entries"], "mean_confidence")
    nkept = build_matrix(idx["entries"], "n_bands_kept")

    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.0), dpi=150)
    im1 = heatmap(axes[0], perp,
                  "(a) train perplexity (lower = better fit)",
                  "viridis_r", "{:.0f}")
    im2 = heatmap(axes[1], conf,
                  "(b) mean per-doc max-θ (confidence proxy)",
                  "viridis", "{:.2f}", vmin=0.2, vmax=1.0)
    im3 = heatmap(axes[2], nkept,
                  "(c) bands kept (sensor B = 268)",
                  "Blues", "{:.0f}", vmin=0, vmax=270)
    for ax, im in zip(axes, (im1, im2, im3)):
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)

    fig.suptitle("HIDSAG mineral subsets — band-mask sweep "
                 "(axis F-5 complement, no per-pixel ground truth)",
                 fontsize=11, y=1.02)
    fig.tight_layout()

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-band-mask.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "hidsag-band-mask.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-band-mask.{{svg,pdf}} to {OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
