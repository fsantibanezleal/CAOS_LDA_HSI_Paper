"""HIDSAG topic-conditional measurement ridges.

For each subset, pick the variable with the largest per-topic-mean
range (most discriminative) and render a per-topic KDE ridge of its
distribution conditional on dominant topic. Reads
`data/derived/hidsag_topic_measurements/<subset>.json`.

Reference: Wilke 2017 ggridges; Hintze-Nelson 1998 violin precursor.

Closes the first deliverable of issue
CAOS_LDA_HSI_Paper#2.
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
       / "hidsag_topic_measurements")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SUBSETS = ["GEOMET", "MINERAL1", "MINERAL2", "GEOCHEM", "PORPHYRY"]


def pick_variable(payload: dict) -> str:
    K = payload["topic_count"]
    stats = payload["per_topic_var_stats"]
    best_var = None
    best_range = -1.0
    for v in payload["variable_names"]:
        means = [stats[str(k)][v].get("mean")
                 for k in range(K)
                 if stats[str(k)][v].get("n", 0) > 0]
        means = [m for m in means if m is not None]
        if len(means) < 2:
            continue
        rng = max(means) - min(means)
        # normalise by data scale to avoid bias toward absolute-large vars
        scale = max(abs(max(means)), abs(min(means)), 1e-6)
        nrng = rng / scale
        if nrng > best_range:
            best_range = nrng
            best_var = v
    return best_var or payload["variable_names"][0]


def kde(values: np.ndarray, x_grid: np.ndarray, bw: float) -> np.ndarray:
    if len(values) == 0:
        return np.zeros_like(x_grid)
    diff = (x_grid[None, :] - values[:, None]) / bw
    return (np.exp(-0.5 * diff * diff)
            / (np.sqrt(2 * np.pi) * bw)).mean(axis=0)


def panel(ax, payload: dict, var: str) -> None:
    K = payload["topic_count"]
    records = payload["records"]
    per_topic = {k: [] for k in range(K)}
    for r in records:
        v = r["vars"].get(var)
        if v is None:
            continue
        per_topic[r["dominant_topic"]].append(v)
    all_vals = [v for vs in per_topic.values() for v in vs]
    if not all_vals:
        ax.set_visible(False)
        return
    lo, hi = min(all_vals), max(all_vals)
    pad = (hi - lo) * 0.05 + 1e-9
    x_grid = np.linspace(lo - pad, hi + pad, 200)
    bw = (hi - lo) / 18 + 1e-6

    curves = {}
    max_dens = 0.0
    for k in range(K):
        c = kde(np.array(per_topic[k], dtype=float), x_grid, bw=bw)
        curves[k] = c
        if c.size and c.max() > max_dens:
            max_dens = c.max()
    if max_dens <= 0:
        max_dens = 1.0
    row_h = 1.0
    scale = row_h * 0.92 / max_dens
    cmap = plt.get_cmap("tab10")

    for k in range(K - 1, -1, -1):
        baseline = (K - 1 - k) * row_h
        y_curve = baseline + curves[k] * scale
        col = cmap(k % 10)
        ax.fill_between(x_grid, baseline, y_curve, facecolor=col,
                        alpha=0.55, edgecolor=col, lw=1.0)
        ax.plot(x_grid, y_curve, color="black", lw=0.4)
        # rug + label
        for v in per_topic[k]:
            ax.plot([v, v], [baseline, baseline + 0.06 * row_h],
                    color="black", lw=0.4, alpha=0.6)
        n = len(per_topic[k])
        m = np.mean(per_topic[k]) if n else float("nan")
        ax.text(lo - pad, baseline + row_h * 0.3,
                f"t{k}  n={n}  μ={m:.2f}", fontsize=7.5,
                va="center", ha="right")
    ax.set_xlim(lo - pad * 1.6, hi + pad)
    ax.set_ylim(-0.1, K * row_h + 0.3)
    ax.set_yticks([])
    ax.set_xlabel(var, fontsize=9)
    ax.set_title(f"{payload['subset_code']}", fontsize=10)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)


def main() -> int:
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.5), dpi=150)
    flat = axes.flatten()
    for ax, subset in zip(flat, SUBSETS):
        path = SRC / f"{subset}.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        var = pick_variable(payload)
        panel(ax, payload, var)
    for ax in flat[len(SUBSETS):]:
        ax.set_visible(False)
    fig.suptitle(
        "HIDSAG continuous-measurement ridge per dominant topic — "
        "one variable per subset selected by largest "
        "per-topic-mean range (normalised)",
        fontsize=10.5, y=0.99,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-measurement-ridges.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "hidsag-measurement-ridges.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-measurement-ridges.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
