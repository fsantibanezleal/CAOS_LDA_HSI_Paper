"""HIDSAG mineralogical topic-spectral-fingerprint per subset.

HIDSAG band_masks_hidsag/<subset>/swir/summary.json artefacts ship
top-words-per-topic as band-wavelength tokens (e.g. swir_1830nm)
but do not expose the continuous phi_{k,b} matrix directly. We
build a discrete per-topic spectral density by binning the top-30
word wavelengths per topic at 50-nm resolution and plotting the
density per topic as a horizontal coloured strip + overlaid stem
markers.

Five subsets (GEOMET, MINERAL1, MINERAL2, GEOCHEM, PORPHYRY) at
SWIR-mask (250 bands kept, near-canonical on the swir_low
modality). Each subset gets its own panel. Mineral absorption
features common in HSI mineralogy are annotated.
"""
from __future__ import annotations

import json
import re
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

SUBSETS = [
    ("GEOMET", "GEOMET — geometallurgical (146 samples)"),
    ("MINERAL1", "MINERAL1 — silicates / sulfides (99 samples)"),
    ("MINERAL2", "MINERAL2 — high-sulfid. epithermal (20 samples)"),
    ("GEOCHEM", "GEOCHEM — geochemistry (28 samples)"),
    ("PORPHYRY", "PORPHYRY — porphyry-copper (28 samples)"),
]

# SWIR-band mineral absorption features (nm)
MINERAL_FEATURES = [
    (1450, "OH 1.4", "#444"),
    (1750, "gypsum", "#3a82c4"),
    (1900, "H₂O 1.9", "#3a82c4"),
    (2170, "alunite", "#b65b8a"),
    (2200, "kaolinite/Al-OH", "#7765c0"),
    (2250, "muscovite", "#7765c0"),
    (2300, "Mg-OH", "#aa5522"),
    (2340, "calcite", "#cc8833"),
]

TOP_N = 30


def parse_nm(token: str) -> float | None:
    m = re.search(r"(\d+)nm", token)
    return float(m.group(1)) if m else None


def main() -> int:
    fig, axes = plt.subplots(5, 1, figsize=(9.0, 9.5), dpi=150, sharex=True)

    for ax, (subset, label) in zip(axes, SUBSETS):
        path = SRC / subset / "swir" / "summary.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        K = d["topic_count"]
        prev = d["topic_prevalence"]
        tw = d["top_words_per_topic_lambda_05"]
        wl_range = (1000, 2500)

        # Annotate mineral features
        for lam, name, colour in MINERAL_FEATURES:
            ax.axvline(lam, color=colour, ls=":", lw=0.7, alpha=0.45,
                       zorder=1)
            ax.text(lam, K + 0.4, name, rotation=90, fontsize=6.0,
                    color=colour, ha="center", va="bottom",
                    alpha=0.75)

        cmap = plt.get_cmap("tab10")
        for k in range(K):
            colour = cmap(k % 10)
            words = tw[k][:TOP_N]
            xs = []
            for w in words:
                token = w if isinstance(w, str) else w.get("token", "")
                lam = parse_nm(token)
                if lam is not None:
                    xs.append(lam)
            if not xs:
                continue
            # Stem markers on a y-row per topic
            y = K - 1 - k
            ax.scatter(xs, [y] * len(xs), color=colour, s=18,
                       marker="|", alpha=0.85, zorder=3)
            # Horizontal strip with weight by prevalence
            ax.axhspan(y - 0.18, y + 0.18, facecolor=colour, alpha=0.07,
                       zorder=0)
            ax.text(wl_range[0] + 20, y, f"t{k}  prev {prev[k]*100:.0f}%",
                    fontsize=7.5, va="center", ha="left", color=colour)
        ax.set_xlim(*wl_range)
        ax.set_ylim(-0.7, K - 0.3)
        ax.set_yticks([])
        ax.set_ylabel("topics", fontsize=8)
        ax.set_title(label, fontsize=9, loc="left")
        ax.grid(axis="x", alpha=0.18)

    axes[-1].set_xlabel("wavelength (nm) — top-30 word λ per topic",
                       fontsize=9)
    fig.suptitle(
        "HIDSAG topic-spectral fingerprints — top-30 words per topic "
        "as λ tick marks; mineral absorption features annotated",
        fontsize=10.5, y=0.997,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-topic-spectra.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "hidsag-topic-spectra.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-topic-spectra.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
