"""Neural-topic-model cross-method top-word wavelength comparison.

For one exemplary scene (Indian Pines, K=12), show the wavelengths
of the top-15 words per topic for LDA / ProdLDA / ETM side by side
as horizontal tick-mark rows. Each row is one topic, each tick is
one top-word's wavelength (parsed from the 'NNNnm' token format).

Reveals whether the three methods agree on which spectral bands they
emphasise, in addition to the ARI-vs-coherence scatter (which only
reports scalars). When LDA and ETM put ticks in similar bands but
ProdLDA's distribution is rotated/shifted, the rotation is itself
the interpretability difference.

Source: data/derived/topic_variants/{lda(sklearn_online),prodlda,
etm}/<scene>.json + canonical topic_views for the LDA variant.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENE = "indian-pines-corrected"
SCENE_LABEL = "Indian Pines (K=12)"

METHOD_PATHS = [
    ("LDA (online VB)", SRC / "topic_views" / f"{SCENE}.json",
     "#1f77b4"),
    ("ProdLDA",         SRC / "topic_variants" / "prodlda" / f"{SCENE}.json",
     "#d62728"),
    ("ETM",             SRC / "topic_variants" / "etm" / f"{SCENE}.json",
     "#2ca02c"),
]

TOP_N = 15


def parse_nm(token) -> float | None:
    if isinstance(token, dict):
        token = token.get("token") or token.get("word") or ""
    s = str(token)
    m = re.search(r"(\d+)\s*nm", s)
    return float(m.group(1)) if m else None


def extract_topic_words(d: dict) -> list[list]:
    tw = d.get("top_words_per_topic")
    if isinstance(tw, dict) and "lambda_0.5" in tw:
        return tw["lambda_0.5"]
    if isinstance(tw, dict) and "lambda_1.0" in tw:
        return tw["lambda_1.0"]
    if isinstance(tw, list):
        return tw
    return []


def panel(ax, payload, colour, method_label, x_range):
    K = payload["topic_count"]
    tw = extract_topic_words(payload)
    for k in range(K):
        words = tw[k][:TOP_N] if k < len(tw) else []
        nms = [parse_nm(w) for w in words]
        nms = [v for v in nms if v is not None]
        y = K - 1 - k
        if nms:
            ax.scatter(nms, [y] * len(nms), color=colour, s=22,
                       marker="|", alpha=0.85, zorder=3)
        ax.axhspan(y - 0.18, y + 0.18, facecolor=colour, alpha=0.05,
                   zorder=0)
        ax.text(x_range[0] - 30, y, f"t{k}", fontsize=8,
                ha="right", va="center", color=colour)
    ax.set_yticks([])
    ax.set_xlim(*x_range)
    ax.set_ylim(-0.6, K - 0.4)
    ax.set_title(f"{method_label}  (prev sum = "
                 f"{sum(payload['topic_prevalence']):.2f})", fontsize=10)
    ax.grid(axis="x", alpha=0.18)


def main() -> int:
    payloads = []
    for label, path, colour in METHOD_PATHS:
        if not path.exists():
            print(f"WARN: missing {path}", file=sys.stderr)
            continue
        with path.open("r", encoding="utf-8") as fh:
            payloads.append((label, json.load(fh), colour))
    if not payloads:
        return 2

    # x-range from canonical LDA wavelengths
    wavelengths = payloads[0][1].get("wavelengths_nm", [])
    if wavelengths:
        x_range = (min(wavelengths) - 60, max(wavelengths) + 30)
    else:
        x_range = (400, 2500)

    fig, axes = plt.subplots(len(payloads), 1, figsize=(11.5, 7.5),
                             dpi=150, sharex=True)
    if len(payloads) == 1:
        axes = [axes]
    for ax, (label, d, colour) in zip(axes, payloads):
        panel(ax, d, colour, label, x_range)
    axes[-1].set_xlabel("wavelength (nm) — top-15 word λ per topic",
                        fontsize=10)
    fig.suptitle(
        f"Cross-method top-word λ comparison on {SCENE_LABEL} — "
        "LDA / ProdLDA / ETM",
        fontsize=11, y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "neural-topic-word-compare.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "neural-topic-word-compare.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote neural-topic-word-compare.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
