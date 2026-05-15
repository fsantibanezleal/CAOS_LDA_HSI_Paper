"""Per-topic confidence (max-theta) ridge plot.

For each canonical topic, the distribution of `confidence` =
max_k theta_dk across documents whose dominant topic is k. Reads
theta_embedding_pca_2d field of topic_to_data/<scene>.json, which
ships `confidence` per document. Each topic gets one ridge curve
(KDE) on a shared x-axis (max-theta). High-confidence topics show
right-shifted curves; mixed topics show flatter / left-shifted curves.

Reference: ggridges (Wilke 2017+) joy-plot pattern; Hintze & Nelson
1998 violin plots; Wilke's 'Goodbye joyplots' explanation of why
ridge is the appropriate name.

Three scenes (Salinas-A, Indian Pines, Botswana).
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
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "topic_to_data"
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENES = [
    ("salinas-a-corrected", "Salinas-A"),
    ("indian-pines-corrected", "Indian Pines"),
    ("botswana", "Botswana"),
]


def kde_curve(values: list[float], x_grid: np.ndarray,
              bw: float = 0.04) -> np.ndarray:
    """Tiny Gaussian KDE without scipy dependency."""
    if not values:
        return np.zeros_like(x_grid)
    v = np.array(values)
    n = len(v)
    diff = (x_grid[None, :] - v[:, None]) / bw
    w = np.exp(-0.5 * diff * diff) / (np.sqrt(2 * np.pi) * bw)
    return w.mean(axis=0)


def panel(ax, scene_id: str, scene_label: str) -> None:
    path = SRC / f"{scene_id}.json"
    with path.open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    emb = d["theta_embedding_pca_2d"]
    K = d["topic_count"]
    per_topic = {k: [] for k in range(K)}
    for rec in emb:
        k = rec["dominant_topic_k"]
        c = rec.get("confidence")
        if c is None:
            continue
        per_topic[k].append(c)

    x_grid = np.linspace(0.0, 1.0, 200)
    cmap = plt.get_cmap("tab20")
    row_h = 1.0
    max_density = 0
    curves = {}
    for k in range(K):
        curves[k] = kde_curve(per_topic[k], x_grid)
        if len(per_topic[k]) > 0:
            max_density = max(max_density, curves[k].max())
    scale = (row_h * 0.95) / (max_density if max_density > 0 else 1.0)

    for k in range(K - 1, -1, -1):  # plot bottom-up
        col = cmap(k % 20)
        y_baseline = (K - 1 - k) * row_h
        y_curve = y_baseline + curves[k] * scale
        ax.fill_between(x_grid, y_baseline, y_curve,
                        facecolor=col, alpha=0.6, edgecolor=col, lw=1.0)
        ax.plot(x_grid, y_curve, color="black", lw=0.4)
        ax.text(-0.03, y_baseline + row_h * 0.3,
                f"t{k}  n={len(per_topic[k])}", fontsize=8.0,
                va="center", ha="right")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, K * row_h + 0.3)
    ax.set_xlabel(r"per-document confidence  $\max_k \theta_{d,k}$",
                  fontsize=9.5)
    ax.set_yticks([])
    ax.set_title(scene_label, fontsize=10)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.axvline(1 / max(K, 1), color="#cccccc", ls="--", lw=0.6)


def main() -> int:
    fig, axes = plt.subplots(1, len(SCENES), figsize=(13.0, 6.0),
                             dpi=150)
    for ax, (sid, slab) in zip(axes, SCENES):
        panel(ax, sid, slab)
    fig.suptitle(
        "Per-topic confidence ridge — KDE of "
        r"$\max_k \theta_{d,k}$ over documents with dominant topic $k$; "
        "vertical dashed line = $1/K$ (uniform-θ baseline)",
        fontsize=10.5, y=0.995,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "confidence-ridge.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "confidence-ridge.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote confidence-ridge.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
