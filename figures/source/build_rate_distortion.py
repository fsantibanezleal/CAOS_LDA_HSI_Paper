"""Rate-distortion curve (axis F-11) across LDA, NMF, PCA.

Six-panel layout, one per labelled scene. X axis: dictionary size K
(number of basis spectra), on a log2 scale. Y axis: normalised held-out
RMSE of the reconstruction
  hat_x = sum_k theta_dk * phi_k^T
in the quantised band-frequency space. NOTE: this is a
distortion-vs-complexity curve, NOT a strict rate-distortion curve --
the reconstruction is a SOFT convex combination over all K topics
(theta_d in the simplex), whose description cost is not the log2(K) bits
of a hard one-of-K codeword, so we plot K rather than a bit-rate.

LDA / NMF / PCA on the same K grid; lower curves dominate. The
tokenisation-loss caveat (the recipe quantises to Q+1=13 levels
before reconstruction) is flagged in journal §VII and Suppl G.
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
       / "rate_distortion_curve")
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

METHOD_STYLE = {
    "lda": ("#1f77b4", "-", "LDA (online VB)"),
    "nmf": ("#d62728", "--", "NMF"),
    "pca": ("#2ca02c", ":", "PCA"),
}


def main() -> int:
    fig, axes = plt.subplots(2, 3, figsize=(11.0, 6.8), dpi=150,
                             sharex=True, sharey=True)
    flat = axes.flatten()
    for ax, (scene_id, label) in zip(flat, SCENES):
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        K_grid = d["K_grid"]
        for method, (colour, style, mlabel) in METHOD_STYLE.items():
            entries = d["method_curves"].get(method, [])
            if not entries:
                continue
            ys = [e["rmse_test_normalised"] for e in entries]
            ax.plot(K_grid, ys, marker="o", color=colour, lw=1.6,
                    linestyle=style, ms=5, label=mlabel, alpha=0.95)
        ax.set_xscale("log", base=2)
        ax.set_title(label, fontsize=10)
        ax.grid(alpha=0.25)
    for ax in flat[len(SCENES):]:
        ax.set_visible(False)
    # X/Y labels on outer plots
    for ax in axes[-1]:
        ax.set_xlabel(r"dictionary size $K$ (number of basis spectra, $\log_2$ scale)", fontsize=9.5)
    for row in axes:
        row[0].set_ylabel("normalised held-out RMSE", fontsize=9.5)

    # Single legend on the first panel
    axes[0, 0].legend(loc="upper right", fontsize=8.5, frameon=False)

    fig.suptitle(
        "F-11 distortion vs dictionary size K of θ — LDA vs NMF vs PCA per scene",
        fontsize=11, y=1.00,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "rate-distortion.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "rate-distortion.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote rate-distortion.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
