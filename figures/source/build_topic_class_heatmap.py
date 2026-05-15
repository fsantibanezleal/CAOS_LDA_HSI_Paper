"""Topic × class soft heatmap (P(L|t) per scene).

For each labelled scene, a heatmap where rows = canonical topics and
columns = ground-truth labels, cell colour = P(label | dominant
topic). Row marginals (docs_per_topic_dominant) shown on the right.
Column marginals (label prevalence) shown on top. Each cell is
annotated with its probability when > 0.05 to keep readability.

Six panels (one per scene) in a 3x2 grid. Replaces the per-topic
'dominant label' summary in journal Table V with a full
two-dimensional view.
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
    ("indian-pines-corrected", "Indian Pines"),
    ("salinas-corrected", "Salinas"),
    ("salinas-a-corrected", "Salinas-A"),
    ("pavia-university", "Pavia U"),
    ("kennedy-space-center", "KSC"),
    ("botswana", "Botswana"),
]


def truncate(s: str, n: int = 14) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"


def main() -> int:
    fig, axes = plt.subplots(3, 2, figsize=(12.5, 14.0), dpi=150)
    flat = axes.flatten()
    for ax, (scene_id, scene_label) in zip(flat, SCENES):
        path = SRC / f"{scene_id}.json"
        if not path.exists():
            ax.set_visible(False)
            continue
        with path.open("r", encoding="utf-8") as fh:
            d = json.load(fh)
        p_label = d["p_label_given_topic_dominant"]
        docs_per_topic = d["docs_per_topic_dominant"]
        K = len(p_label)
        labels_order = [(item["label_id"], item["name"], item["color"])
                        for item in p_label[0]]
        L = len(labels_order)
        # Build K x L probability matrix
        M = np.zeros((K, L), dtype=float)
        for k in range(K):
            for j, item in enumerate(p_label[k]):
                M[k, j] = item["p"]
        # Marginal column probability = sum_k P(L|t)*P(t)
        topic_weight = np.array(docs_per_topic, dtype=float)
        topic_weight /= topic_weight.sum()
        col_marginal = (M * topic_weight[:, None]).sum(axis=0)

        cmap = plt.get_cmap("YlOrRd").copy()
        cmap.set_bad(color="#eeeeee")
        im = ax.imshow(M, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
        ax.set_xticks(range(L))
        ax.set_yticks(range(K))
        ax.set_xticklabels([truncate(n) for _, n, _ in labels_order],
                           rotation=40, ha="right", fontsize=7.5)
        ax.set_yticklabels([f"t{k}\n(n={docs_per_topic[k]})"
                            for k in range(K)], fontsize=7.5)
        for i in range(K):
            for j in range(L):
                v = M[i, j]
                if v < 0.05:
                    continue
                colour = "white" if v > 0.55 else "black"
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6.0, color=colour)
        # Column-marginal bar above the heatmap
        ax2 = ax.inset_axes([0, 1.02, 1, 0.10])
        ax2.bar(range(L), col_marginal,
                color=[c for _, _, c in labels_order],
                edgecolor="black", linewidth=0.3)
        ax2.set_xlim(-0.5, L - 0.5)
        ax2.set_xticks([])
        ax2.set_yticks([])
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.set_facecolor("none")
        ax.set_title(scene_label, fontsize=10, pad=20)

    fig.suptitle(
        "Topic × class soft heatmap — P(label | dominant topic) per "
        "scene. Top strip = label marginal weighted by topic "
        "prevalence.",
        fontsize=11, y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "topic-class-heatmap.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "topic-class-heatmap.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote topic-class-heatmap.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
