"""Theta-PCA 2D scatter coloured by topic + ground-truth class
contours.

Reads `topic_to_data/<scene>.json` field `theta_embedding_pca_2d`
(one record per sampled document with x, y, label_id, dominant_topic_k,
confidence) and renders a two-row × scene-count figure. Top row:
points coloured by **dominant topic**; bottom row: points coloured
by **ground-truth label**. 1-σ and 2-σ covariance ellipses per class
overlaid on the bottom row to show whether the topic axis separates
the class manifolds in PCA-of-θ space.

Reference: corner.py-style scatterplot + matplotlib confidence-
ellipse recipe. Each panel is a marginalised view of the K-dim
theta simplex.

Three scenes selected for diagnostic contrast (Salinas-A band-robust,
Indian Pines partial, Botswana band-fragile).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.transforms as transforms  # noqa: E402
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


def confidence_ellipse(x, y, ax, n_std=2.0, **kwargs):
    """Matplotlib gallery recipe for 2D Gaussian confidence ellipse."""
    if len(x) < 3:
        return
    cov = np.cov(x, y)
    if not np.all(np.isfinite(cov)):
        return
    pearson = cov[0, 1] / (np.sqrt(cov[0, 0] * cov[1, 1]) + 1e-12)
    if not np.isfinite(pearson):
        pearson = 0.0
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = mpatches.Ellipse((0, 0), width=ell_radius_x * 2,
                               height=ell_radius_y * 2, **kwargs)
    scale_x = np.sqrt(cov[0, 0]) * n_std
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_x, mean_y = np.mean(x), np.mean(y)
    transf = (transforms.Affine2D()
              .rotate_deg(45)
              .scale(scale_x, scale_y)
              .translate(mean_x, mean_y))
    ellipse.set_transform(transf + ax.transData)
    ax.add_patch(ellipse)


def panel_topic(ax, emb, topic_colours):
    for rec in emb:
        k = rec["dominant_topic_k"]
        col = topic_colours[k % len(topic_colours)]
        ax.scatter(rec["x"], rec["y"], s=6,
                   c=[col], alpha=0.55, edgecolor="none")
    ax.set_xticks([]); ax.set_yticks([])


def panel_label(ax, emb, label_colours_map):
    # gather per-label points for ellipse drawing
    per_label = {}
    for rec in emb:
        lid = rec.get("label_id")
        if lid is None:
            continue
        per_label.setdefault(lid, []).append((rec["x"], rec["y"]))
    for lid, pts in per_label.items():
        col = label_colours_map.get(lid, "#888")
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        ax.scatter(xs, ys, s=6, c=[col], alpha=0.4, edgecolor="none")
        if len(xs) > 4:
            confidence_ellipse(np.array(xs), np.array(ys), ax,
                               n_std=2.0, facecolor="none",
                               edgecolor=col, lw=1.0, alpha=0.85)
    ax.set_xticks([]); ax.set_yticks([])


def main() -> int:
    fig, axes = plt.subplots(2, len(SCENES), figsize=(13.0, 7.6),
                             dpi=150)
    cmap_topics = plt.get_cmap("tab20")
    topic_colours = [cmap_topics(i / 20) for i in range(20)]
    for col, (scene_id, scene_label) in enumerate(SCENES):
        path = SRC / f"{scene_id}.json"
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        emb = d["theta_embedding_pca_2d"]
        K = d["topic_count"]
        # Build label-id -> colour map
        label_meta = d["p_label_given_topic_dominant"][0]
        label_colours = {item["label_id"]: item["color"]
                         for item in label_meta}

        panel_topic(axes[0, col], emb, topic_colours)
        axes[0, col].set_title(f"{scene_label} — coloured by topic "
                               f"(K={K})", fontsize=10)
        panel_label(axes[1, col], emb, label_colours)
        axes[1, col].set_title(
            f"{scene_label} — coloured by label "
            f"(2σ ellipses)", fontsize=10)
    fig.suptitle(
        "PCA-2D embedding of θ — top row: dominant topic; "
        "bottom row: ground-truth label with 2σ Gaussian confidence "
        "ellipses",
        fontsize=11, y=0.995,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "theta-embedding-scatter.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "theta-embedding-scatter.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote theta-embedding-scatter.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
