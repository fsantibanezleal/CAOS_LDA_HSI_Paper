"""Build the hierarchical-Bayesian method-comparison figure for the
journal manuscript.

Renders two side-by-side panels:
  (a) Labelled-scene block: posterior mean +/- std for the 5 methods.
  (b) HIDSAG block: posterior mean +/- std for the 5 methods.

The contrast between the two panels surfaces the HIDSAG inversion
discussed in Section V of the journal paper.
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
LBL_JSON = (
    REPO_ROOT.parent
    / "CAOS_LDA_HSI"
    / "data"
    / "derived"
    / "method_statistics_labelled"
    / "cross_classification_bayesian.json"
)
HID_JSON = (
    REPO_ROOT.parent
    / "CAOS_LDA_HSI"
    / "data"
    / "derived"
    / "method_statistics_hidsag"
    / "cross_classification_bayesian.json"
)
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"


def panel(ax, payload, title: str) -> None:
    posts = payload["method_posteriors"]
    names = [p["method"] for p in posts]
    mu = np.array([p["posterior_mean"] for p in posts])
    sd = np.array([p["posterior_std"] for p in posts])

    order = np.argsort(mu)
    names = [names[i] for i in order]
    mu = mu[order]
    sd = sd[order]

    y = np.arange(len(names))
    ax.errorbar(mu, y, xerr=sd, fmt="o", color="#1f77b4",
                ecolor="#888", elinewidth=1.4, capsize=4, ms=6)
    ax.axvline(0.0, ls="--", color="#999", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([n.replace("_logistic_regression", "")
                        .replace("_logistic", "")
                        for n in names], fontsize=8.5)
    ax.set_xlabel(r"posterior $\mu_m$ (NUTS, 2 chains)", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="x", alpha=0.3)


def main() -> int:
    for p in (LBL_JSON, HID_JSON):
        if not p.exists():
            print(f"ERROR: source artefact not found: {p}", file=sys.stderr)
            return 2

    with LBL_JSON.open("r", encoding="utf-8") as fh:
        labelled = json.load(fh)
    with HID_JSON.open("r", encoding="utf-8") as fh:
        hidsag = json.load(fh)

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.4), dpi=150)
    panel(axes[0], labelled,
          "(a) Labelled scenes: 6 scenes x 5 folds x 5 methods")
    panel(axes[1], hidsag,
          "(b) HIDSAG: 5 subsets x 19 targets x 5 methods")
    fig.suptitle("Hierarchical-Bayesian method comparison (B-1 axis)",
                 fontsize=11, y=1.03)
    fig.tight_layout()

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "bayesian-method-comparison.svg", format="svg")
        fig.savefig(outdir / "bayesian-method-comparison.pdf", format="pdf")
    plt.close(fig)
    print(f"wrote bayesian-method-comparison.{{svg,pdf}} to "
          f"{OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
