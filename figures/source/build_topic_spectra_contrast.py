"""Topic spectra contrast — every phi_k(lambda) overlaid on a single
panel per scene with annotated physical features.

Single-panel-per-scene contrast figure: superposing all K basis
spectra makes the cross-topic differences immediately visible, and
annotating known absorption features (water-vapour 1400/1900 nm,
Fe-oxide 480/530 nm, vegetation red-edge 700 nm, cellulose 2100/2300
nm) lets the reader read the physical interpretation directly off
the figure.

Two scene examples chosen for diagnostic contrast:
  - Salinas-A (band-robust under SWIR, paired ARI 0.766)
  - Kennedy Space Center (band-fragile across all masks)
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

WATER_BANDS_NM = [(1350, 1430), (1800, 1950), (2480, 2500)]

# Diagnostic absorption / reflectance features in HSI vegetation +
# soils + minerals literature.
FEATURES = [
    (480, "Fe-oxide α", "#aa6633"),
    (530, "chlorophyll", "#2ca02c"),
    (680, "chlorophyll-red", "#2ca02c"),
    (720, "veg red-edge", "#2ca02c"),
    (970, "leaf-water", "#3aa1c7"),
    (1200, "leaf-water 2", "#3aa1c7"),
    (1400, "atm. water", "#888888"),
    (1900, "atm. water 2", "#888888"),
    (2100, "cellulose", "#8a4f2a"),
    (2200, "Al-OH (kaolinite)", "#7765c0"),
    (2300, "Mg-OH / lignin", "#7765c0"),
]


def panel(ax, scene_id: str, scene_label: str) -> None:
    path = SRC / f"{scene_id}.json"
    with path.open("r", encoding="utf-8") as fh:
        tv = json.load(fh)
    wl = np.array(tv["wavelengths_nm"], dtype=float)
    phi = np.array(tv["topic_band_profiles"], dtype=float)
    K = phi.shape[0]
    prev = tv["topic_prevalence"]

    # Shade water bands
    for lo, hi in WATER_BANDS_NM:
        if wl.min() < hi and wl.max() > lo:
            ax.axvspan(lo, hi, color="#eeeeee", alpha=0.5, zorder=0)

    # Annotate features
    y_max = phi.max() * 1.18
    for lam, name, colour in FEATURES:
        if wl.min() <= lam <= wl.max():
            ax.axvline(lam, color=colour, ls=":", lw=0.6, alpha=0.5,
                       zorder=1)
            ax.text(lam, y_max, name, rotation=90, fontsize=6.0,
                    color=colour, ha="center", va="top", alpha=0.75)

    # Plot topics, line-width weighted by prevalence
    cmap = plt.get_cmap("tab20")
    order = np.argsort(prev)  # plot lowest prevalence first
    for k in order:
        lw = 0.6 + 3.0 * (prev[k] / max(prev))
        ax.plot(wl, phi[k], color=cmap(k % 20), lw=lw, alpha=0.95,
                label=f"t{k} ({prev[k]*100:.0f}%)", zorder=3)

    ax.set_xlabel("wavelength (nm)", fontsize=9)
    ax.set_ylabel(r"$\phi_{k,b}$", fontsize=9)
    ax.set_title(scene_label, fontsize=10)
    ax.set_ylim(0, y_max * 1.02)
    ax.grid(alpha=0.18)
    ax.legend(loc="upper right", fontsize=7, frameon=False,
              ncol=2, columnspacing=0.6)


def main() -> int:
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 8.0), dpi=150,
                             sharex=False)
    panel(axes[0], "salinas-a-corrected",
          "(a) Salinas-A K=6 — band-robust (SWIR paired ARI 0.766)")
    panel(axes[1], "kennedy-space-center",
          "(b) Kennedy Space Center K=12 — band-fragile "
          "(paired ARI ≈ 0.01 across all masks)")
    fig.suptitle("Topic spectra contrast — every φ_k overlaid; "
                 "line width = topic prevalence; vertical lines = "
                 "diagnostic absorption / reflectance features",
                 fontsize=10.5, y=0.995)
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "topic-spectra-contrast.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "topic-spectra-contrast.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote topic-spectra-contrast.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
