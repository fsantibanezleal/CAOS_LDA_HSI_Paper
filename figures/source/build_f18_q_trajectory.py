"""F-18 Q-trajectory figure for V20 / V8 / V2.

Plots F-18 mean matched cosine across Q=8/16/32 for the three top
contenders, alongside their F-7 LDA trajectory to show the
reliability vs informativeness tradeoff.

Output: figures/f18-q-trajectory.{pdf,svg,png}
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "v_sweep"
OUT_DIR = REPO_ROOT / "figures"

SCENES = [
    "indian-pines-corrected", "salinas-corrected", "salinas-a-corrected",
    "pavia-university", "kennedy-space-center", "botswana",
]
RECIPES = ["V20", "V8", "V2"]
Q_VALUES = [8, 16, 32]

COLOURS = {
    "V8":  "#10b981",
    "V20": "#9333ea",
    "V2":  "#0ea5e9",
}


def load_mean(axis_dir: str, key: str, recipe: str, q: int) -> float | None:
    vals: list[float] = []
    for sc in SCENES:
        f = SRC / axis_dir / f"{sc}_{recipe}_uniform_Q{q}.json"
        if not f.exists():
            continue
        d = json.load(f.open())
        v = d.get(key)
        if v is not None:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                continue
    if not vals:
        return None
    return statistics.mean(vals)


def main() -> int:
    fig, (ax_f18, ax_f7) = plt.subplots(1, 2, figsize=(12.5, 5.5))

    for r in RECIPES:
        f18 = [load_mean("f18_reliability", "mean_matched_cosine", r, q) for q in Q_VALUES]
        f7 = [load_mean("f7_topic_to_label", "normalised_mi", r, q) for q in Q_VALUES]
        c = COLOURS[r]
        for ax, ys, label in [(ax_f18, f18, f"{r}"), (ax_f7, f7, f"{r}")]:
            x = [q for q, v in zip(Q_VALUES, ys) if v is not None]
            y = [v for v in ys if v is not None]
            if y:
                marker = "*" if r == "V8" else ("o" if r == "V20" else "s")
                msize = 14 if r == "V8" else (10 if r == "V20" else 8)
                ax.plot(x, y, color=c, linewidth=2.6, marker=marker,
                        markersize=msize, label=label)

    ax_f18.set_xticks(Q_VALUES)
    ax_f18.set_xticklabels([f"Q={q}" for q in Q_VALUES], fontsize=11)
    ax_f18.set_xlabel("Quantisation level $Q$", fontsize=11)
    ax_f18.set_ylabel("Mean matched cosine (top-10 indicator)", fontsize=11)
    ax_f18.set_title("F-18 reliability (Maier 2024)", fontsize=12, fontweight="bold")
    ax_f18.grid(alpha=0.18, linewidth=0.5)
    ax_f18.spines["top"].set_visible(False)
    ax_f18.spines["right"].set_visible(False)
    ax_f18.legend(loc="center right", fontsize=10, frameon=False)
    ax_f18.set_ylim(0.3, 1.05)

    ax_f7.set_xticks(Q_VALUES)
    ax_f7.set_xticklabels([f"Q={q}" for q in Q_VALUES], fontsize=11)
    ax_f7.set_xlabel("Quantisation level $Q$", fontsize=11)
    ax_f7.set_ylabel("NMI(argmax topic, label) mean across 6 scenes", fontsize=11)
    ax_f7.set_title("F-7 informativeness (LDA backbone)", fontsize=12, fontweight="bold")
    ax_f7.grid(alpha=0.18, linewidth=0.5)
    ax_f7.spines["top"].set_visible(False)
    ax_f7.spines["right"].set_visible(False)
    ax_f7.legend(loc="lower right", fontsize=10, frameon=False)

    fig.suptitle(
        "F-18 reliability vs F-7 informativeness — V8 is the only recipe high on both",
        fontsize=13.5, fontweight="bold", y=1.0,
    )
    fig.text(
        0.5, 0.005,
        "V8 (green star) stays above 0.95 on F-18 across Q while rising monotonically on F-7. "
        "V20 (purple circle) wins F-7 and rises monotonically but stays at ~0.45 on F-18 "
        "(informative-but-seed-sensitive). V2 (cyan square) collapses on F-18 with Q while staying flat on F-7.",
        ha="center", fontsize=8.5, color="#475569",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        out = OUT_DIR / f"f18-q-trajectory.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
