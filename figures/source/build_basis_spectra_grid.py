"""Basis-spectra grid — the K topic-word distributions phi_k plotted
as continuous spectra against wavelength (nm).

Reads `topic_views/<scene>.json` whose `topic_band_profiles` field
holds phi as a K x B matrix and `wavelengths_nm` holds the
band centres in nanometres.

Six panels (one per scene), K lines per panel coloured by topic id.
The water-vapour absorption bands (1350-1430, 1800-1950, 2480-2500 nm)
are shaded grey to mark the regions the no-water mask removes.
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
    ("indian-pines-corrected", "Indian Pines (AVIRIS, K=12)"),
    ("salinas-corrected", "Salinas (AVIRIS, K=12)"),
    ("salinas-a-corrected", "Salinas-A (AVIRIS, K=6)"),
    ("pavia-university", "Pavia University (ROSIS, K=9)"),
    ("kennedy-space-center", "Kennedy Space Center (AVIRIS, K=12)"),
    ("botswana", "Botswana (EO-1, K=12)"),
]

WATER_BANDS_NM = [(1350, 1430), (1800, 1950), (2480, 2500)]


def main() -> int:
    fig, axes = plt.subplots(3, 2, figsize=(11.0, 9.0), dpi=150)
    flat = axes.flatten()
    for ax, (scene_id, label) in zip(flat, SCENES):
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            print(f"WARN: missing {path}", file=sys.stderr)
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        wl = np.array(d["wavelengths_nm"], dtype=float)
        phi = np.array(d["topic_band_profiles"], dtype=float)
        K = phi.shape[0]

        for lo, hi in WATER_BANDS_NM:
            if wl.min() < hi and wl.max() > lo:
                ax.axvspan(lo, hi, color="#dddddd", alpha=0.6, zorder=0)

        cmap = plt.get_cmap("tab20")
        for k in range(K):
            ax.plot(wl, phi[k], color=cmap(k % 20), lw=0.95, alpha=0.9,
                    label=f"t{k}", zorder=2)
        ax.set_xlabel("wavelength (nm)", fontsize=9)
        ax.set_ylabel(r"$\phi_{k,b}$", fontsize=9)
        ax.set_title(label, fontsize=10)
        ax.grid(alpha=0.2)
        ax.tick_params(labelsize=8)

    # Hide unused
    for ax in flat[len(SCENES):]:
        ax.set_visible(False)

    fig.suptitle(r"Canonical-fit topic basis spectra $\phi$ "
                 "(per-scene K topics) — water-vapour bands shaded",
                 fontsize=11, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "basis-spectra-grid.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "basis-spectra-grid.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote basis-spectra-grid.{{svg,pdf}} to {OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
