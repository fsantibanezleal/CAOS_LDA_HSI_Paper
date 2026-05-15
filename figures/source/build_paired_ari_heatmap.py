"""Build paired-ARI heatmap SVG + PDF for the conference + journal paper.

Reads canonical_comparison.json from the CAOS_LDA_HSI repo and renders a
heatmap of paired ARI per (scene, mask) tuple. Outputs both .svg
(for the GitHub README and the SVG-archive) and .pdf (for LaTeX).

Deterministic: no RNG, no clock-dependent input. Re-run yields byte-equal
SVG and visually-equal PDF (small font-rendering deltas are unavoidable
across matplotlib versions but the numerical content is fixed).
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
SRC_JSON = (
    REPO_ROOT.parent
    / "CAOS_LDA_HSI"
    / "data"
    / "derived"
    / "band_masks"
    / "canonical_comparison.json"
)
OUT_DIR = REPO_ROOT / "figures"
CONF_FIG_DIR = REPO_ROOT / "conference" / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENE_ORDER = [
    "indian-pines-corrected",
    "salinas-corrected",
    "salinas-a-corrected",
    "pavia-university",
    "kennedy-space-center",
    "botswana",
]
SCENE_LABELS = [
    "Indian Pines",
    "Salinas",
    "Salinas-A",
    "Pavia U",
    "KSC",
    "Botswana",
]
MASK_ORDER = ["vnir", "swir", "no_water", "top_50_fisher"]
MASK_LABELS = ["VNIR", "SWIR", "no-water", "top-50 Fisher"]


def main() -> int:
    if not SRC_JSON.exists():
        print(f"ERROR: source artefact not found: {SRC_JSON}", file=sys.stderr)
        return 2

    with SRC_JSON.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    entries = {(e["scene_id"], e["mask_id"]): e for e in payload["entries"]}

    M = np.full((len(SCENE_ORDER), len(MASK_ORDER)), np.nan, dtype=float)
    annot = np.full(M.shape, "", dtype=object)
    for i, scene in enumerate(SCENE_ORDER):
        for j, mask in enumerate(MASK_ORDER):
            entry = entries.get((scene, mask))
            if entry is None or entry.get("skipped"):
                annot[i, j] = "---"
                continue
            ari = entry["paired_ari_dominant_topics"]
            M[i, j] = ari
            annot[i, j] = f"{ari:.3f}"

    fig, ax = plt.subplots(figsize=(5.0, 4.0), dpi=150)
    masked = np.ma.masked_invalid(M)
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad(color="#dddddd")
    im = ax.imshow(masked, cmap=cmap, vmin=0.0, vmax=0.8, aspect="auto")

    ax.set_xticks(range(len(MASK_LABELS)))
    ax.set_xticklabels(MASK_LABELS, rotation=20, ha="right", fontsize=9)
    ax.set_yticks(range(len(SCENE_LABELS)))
    ax.set_yticklabels(SCENE_LABELS, fontsize=9)
    ax.set_xlabel("band mask", fontsize=10)
    ax.set_ylabel("scene", fontsize=10)
    ax.set_title("Paired ARI (canonical vs band-masked dominant-topic maps)",
                 fontsize=10)

    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            value = M[i, j]
            txt = annot[i, j]
            if np.isnan(value):
                colour = "#222222"
            else:
                colour = "white" if value < 0.45 else "black"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8.5,
                    color=colour)

    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("paired ARI", fontsize=9)

    fig.tight_layout()

    for outdir in (OUT_DIR, CONF_FIG_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "paired-ari-heatmap.svg", format="svg")
        fig.savefig(outdir / "paired-ari-heatmap.pdf", format="pdf")

    plt.close(fig)
    print(f"wrote paired-ari-heatmap.{{svg,pdf}} to "
          f"{OUT_DIR}, {CONF_FIG_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
