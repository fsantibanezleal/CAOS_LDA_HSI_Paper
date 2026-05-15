"""Topic → class Sankey / alluvial diagrams for the labelled scenes.

For each scene, render a 2-stage bipartite flow:
  left axis  = canonical topic ids (sized by docs_per_topic_dominant)
  right axis = ground-truth class labels (sized by sum_k
               docs_per_topic * P(label | t))
  ribbons    = topic -> class mass

Demonstrates where the topic basis aggregates / disperses class
labels — visually surfaces the one-to-many and many-to-one mappings
that the ARI scalar hides. Reference: Sankey diagram tradition
(Sankey 1898; modern revivals in Data-to-Viz / d3-sankey). Salinas-A
is the cleanest example because K=6 and L=6 produce a legible
diagram; Botswana (K=12, L=14) is included as the harder case.

Two-panel figure: Salinas-A (left) and Botswana (right).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "topic_to_data"
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENES = [
    ("salinas-a-corrected", "Salinas-A (K=6, L=6) — band-robust"),
    ("botswana", "Botswana (K=12, L=14) — band-fragile"),
]


def truncate(s: str, n: int = 16) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"


def draw_sankey(ax, scene_id: str, title: str) -> None:
    path = SRC / f"{scene_id}.json"
    with path.open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    p_label = d["p_label_given_topic_dominant"]
    docs_per_topic = np.array(d["docs_per_topic_dominant"], dtype=float)
    K = len(p_label)
    label_meta = p_label[0]
    L = len(label_meta)
    label_colors = [item["color"] for item in label_meta]
    label_names = [truncate(item["name"]) for item in label_meta]

    # K x L flow matrix in absolute counts
    F = np.zeros((K, L), dtype=float)
    for k in range(K):
        for j, item in enumerate(p_label[k]):
            F[k, j] = item["count"]
    total = F.sum()

    # Left node heights = topic counts
    left_heights = F.sum(axis=1)
    right_heights = F.sum(axis=0)
    gap = total * 0.012

    cum_left = 0.0
    left_pos = []
    for k in range(K):
        left_pos.append((cum_left, cum_left + left_heights[k]))
        cum_left += left_heights[k] + gap
    left_total = cum_left - gap

    cum_right = 0.0
    right_pos = []
    for j in range(L):
        right_pos.append((cum_right, cum_right + right_heights[j]))
        cum_right += right_heights[j] + gap
    right_total = cum_right - gap

    scale = max(left_total, right_total)
    ax.set_xlim(0, 100)
    ax.set_ylim(scale * 1.02, -scale * 0.02)

    x_left = 8
    x_right = 80
    node_w = 6

    cmap_topics = plt.get_cmap("tab20")

    # Draw nodes
    for k, (top, bot) in enumerate(left_pos):
        col = cmap_topics(k % 20)
        ax.add_patch(mpatches.Rectangle((x_left, top), node_w, bot - top,
                                        facecolor=col, edgecolor="black",
                                        lw=0.5))
        ax.text(x_left - 1, (top + bot) / 2, f"t{k} (n={int(left_heights[k])})",
                fontsize=7, va="center", ha="right")
    for j, (top, bot) in enumerate(right_pos):
        col = label_colors[j]
        ax.add_patch(mpatches.Rectangle((x_right, top), node_w, bot - top,
                                        facecolor=col, edgecolor="black",
                                        lw=0.5))
        ax.text(x_right + node_w + 1, (top + bot) / 2,
                f"{label_names[j]} (n={int(right_heights[j])})",
                fontsize=7, va="center", ha="left")

    # Draw flows
    # For each topic, walk through its outgoing flows in order
    left_used = [pos[0] for pos in left_pos]
    right_used = [pos[0] for pos in right_pos]
    for k in range(K):
        col = cmap_topics(k % 20)
        for j in range(L):
            mass = F[k, j]
            if mass <= 0.5:  # skip negligible
                continue
            y0_top = left_used[k]
            y0_bot = left_used[k] + mass
            y1_top = right_used[j]
            y1_bot = right_used[j] + mass
            left_used[k] += mass
            right_used[j] += mass
            # cubic Bezier path
            verts = [
                (x_left + node_w, y0_top),
                ((x_left + node_w + x_right) / 2, y0_top),
                ((x_left + node_w + x_right) / 2, y1_top),
                (x_right, y1_top),
                (x_right, y1_bot),
                ((x_left + node_w + x_right) / 2, y1_bot),
                ((x_left + node_w + x_right) / 2, y0_bot),
                (x_left + node_w, y0_bot),
            ]
            codes = [matplotlib.path.Path.MOVETO,
                     matplotlib.path.Path.CURVE4,
                     matplotlib.path.Path.CURVE4,
                     matplotlib.path.Path.CURVE4,
                     matplotlib.path.Path.LINETO,
                     matplotlib.path.Path.CURVE4,
                     matplotlib.path.Path.CURVE4,
                     matplotlib.path.Path.CURVE4]
            path_obj = matplotlib.path.Path(verts, codes)
            patch = mpatches.PathPatch(path_obj, facecolor=col,
                                       edgecolor="none", alpha=0.35)
            ax.add_patch(patch)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=10)
    for s in ax.spines.values():
        s.set_visible(False)


def main() -> int:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 7.5), dpi=150)
    for ax, (scene_id, title) in zip(axes, SCENES):
        draw_sankey(ax, scene_id, title)
    fig.suptitle(
        "Topic → class Sankey/alluvial flow — ribbon thickness = number "
        "of pixels with dominant topic $t$ and ground-truth label $\\ell$",
        fontsize=11, y=0.995,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "topic-class-sankey.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "topic-class-sankey.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote topic-class-sankey.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
