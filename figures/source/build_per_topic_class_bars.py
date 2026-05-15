"""Per-topic class-distribution bar panels (ridge-style for
categorical labels).

For each canonical topic on a chosen scene, render a horizontal bar
chart of P(label | dominant topic) — every topic gets its own row,
all rows stacked on a shared label-axis. The visual is the categorical
analogue of a ridge plot: each topic's 'distribution' is the
discrete bar set on its row. A topic that resolves one or two labels
shows as a single tall bar; a topic that mixes labels shows as a
spread.

Two-panel figure: Salinas-A (K=6, clean) + Indian Pines (K=12,
richer label set). Both bottom-up with shared x-axis (label names).
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
    ("salinas-a-corrected", "Salinas-A (K=6)"),
    ("indian-pines-corrected", "Indian Pines (K=12)"),
]


def truncate(s: str, n: int = 14) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"


def panel(ax, scene_id: str, scene_label: str) -> None:
    path = SRC / f"{scene_id}.json"
    with path.open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    p_label = d["p_label_given_topic_dominant"]
    docs_per_topic = d["docs_per_topic_dominant"]
    K = len(p_label)
    L = len(p_label[0])
    labels_order = p_label[0]
    label_names = [truncate(item["name"]) for item in labels_order]
    label_colours = [item["color"] for item in labels_order]

    row_h = 0.85  # height available per topic row
    bar_w = 0.85 / L  # bar width within a label cell
    x_positions = np.arange(L)

    for k in range(K):
        y_baseline = (K - 1 - k)  # invert so topic 0 is at top
        ps = [item["p"] for item in p_label[k]]
        for j, p in enumerate(ps):
            ax.bar(x_positions[j], p * row_h, bottom=y_baseline,
                   width=0.85, color=label_colours[j],
                   edgecolor="black", linewidth=0.25, alpha=0.85)
        ax.text(-0.55, y_baseline + row_h / 2,
                f"t{k}  n={docs_per_topic[k]}", fontsize=8,
                va="center", ha="right")
        # baseline line
        ax.axhline(y_baseline, color="#cccccc", lw=0.4, zorder=0)

    ax.set_xlim(-0.6, L - 0.4)
    ax.set_ylim(-0.2, K + 0.1)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(label_names, rotation=40, ha="right", fontsize=7.5)
    ax.set_yticks([])
    ax.set_title(scene_label, fontsize=10)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)


def main() -> int:
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 6.0), dpi=150)
    for ax, (sid, slab) in zip(axes, SCENES):
        panel(ax, sid, slab)
    fig.suptitle(
        "Per-topic class distribution — each row = one canonical "
        "topic, bar height = P(label | dominant topic); coloured "
        "with the canonical class palette",
        fontsize=10.5, y=0.997,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "per-topic-class-bars.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "per-topic-class-bars.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote per-topic-class-bars.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
