"""Hammock plot for PORPHYRY: combines the categorical 'dominant
topic' axis with three continuous mineralogical assays (Bt%, Mb%,
Py%) on a single parallel-coordinates-like diagram. Each axis is
binned into 5 categorical levels (low … high quintiles for
continuous variables; categorical-as-is for topic); ribbons connect
adjacent axes weighted by joint pixel count.

Reference: Schonlau (2025) "Hammock plot for mixed numerical and
categorical variables" (arXiv:2506.13630). The hammock plot
unifies mosaic plots (categorical-only) and parallel coordinates
(continuous-only) under one visual; documents move left-to-right
through their assigned bin on each axis.

PORPHYRY chosen because its Bt% (biotite) ranges per topic 1.1..39.6
which produces the strongest visible structure under this idiom.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.path as mpath  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = (REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
       / "hidsag_topic_measurements" / "PORPHYRY.json")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

CONTINUOUS_VARS = ["Bt (%)", "Mb (%)", "Py (%)"]
N_BINS = 5


def quintile_bin(values: list[float], n_bins: int = N_BINS
                 ) -> tuple[list[int], list[float]]:
    arr = np.array(values, dtype=float)
    qs = np.quantile(arr, np.linspace(0, 1, n_bins + 1))
    qs[0] -= 1e-9
    bins = np.clip(np.digitize(arr, qs[1:-1]), 0, n_bins - 1)
    return bins.tolist(), qs.tolist()


def main() -> int:
    with SRC.open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    K = d["topic_count"]
    records = d["records"]
    # axis 0 = dominant_topic (K categorical levels)
    # axes 1..3 = continuous variables binned into quintiles
    topic_levels = list(range(K))
    cont_bins = {}
    cont_edges = {}
    for v in CONTINUOUS_VARS:
        vs = [r["vars"].get(v) for r in records if r["vars"].get(v)
              is not None]
        bins, edges = quintile_bin(vs, N_BINS)
        cont_bins[v] = bins
        cont_edges[v] = edges

    # Build per-document axis tuple
    paths = []
    for i, r in enumerate(records):
        t = r["dominant_topic"]
        axis_values = [t] + [cont_bins[v][i] if v in cont_bins
                              and i < len(cont_bins[v]) else 0
                              for v in CONTINUOUS_VARS]
        paths.append((t, axis_values))

    axis_labels = ["topic"] + CONTINUOUS_VARS
    axis_n_levels = [K] + [N_BINS] * len(CONTINUOUS_VARS)
    n_axes = len(axis_labels)

    fig, ax = plt.subplots(figsize=(11.5, 5.5), dpi=150)
    axis_x = list(range(n_axes))
    axis_w = 0.18
    cmap = plt.get_cmap("tab10")

    # draw axis blocks
    block_h = 1.0  # per-level height
    for a, (lab, n_lev) in enumerate(zip(axis_labels, axis_n_levels)):
        for lev in range(n_lev):
            ax.add_patch(mpatches.Rectangle(
                (axis_x[a] - axis_w / 2, lev * block_h),
                axis_w, block_h * 0.92,
                facecolor="#f0f0f0", edgecolor="black", lw=0.5))
            # level label
            if a == 0:
                txt = f"t{lev}"
            else:
                edges = cont_edges[axis_labels[a]]
                txt = f"Q{lev + 1}\n[{edges[lev]:.1f},\n{edges[lev + 1]:.1f}]"
            ax.text(axis_x[a], lev * block_h + block_h * 0.46,
                    txt, ha="center", va="center", fontsize=7)
        ax.text(axis_x[a], -0.5, lab, ha="center", va="top",
                fontsize=9, weight="bold")

    # Count (topic, level_pairs)
    from collections import Counter
    for a in range(n_axes - 1):
        # ribbon counts between axis a and axis a+1, split by topic colour
        pair_counts: dict[tuple, int] = Counter()
        for t, vals in paths:
            pair_counts[(t, vals[a], vals[a + 1])] += 1
        # Drawing order: stack by source-level bottom-up
        used_left = {lev: 0 for lev in range(axis_n_levels[a])}
        used_right = {lev: 0 for lev in range(axis_n_levels[a + 1])}
        # First compute totals
        left_totals = {lev: 0 for lev in range(axis_n_levels[a])}
        right_totals = {lev: 0 for lev in range(axis_n_levels[a + 1])}
        for (t, lvl_l, lvl_r), cnt in pair_counts.items():
            left_totals[lvl_l] += cnt
            right_totals[lvl_r] += cnt
        scale_left = {lev: (block_h * 0.92) / max(left_totals[lev], 1)
                      for lev in range(axis_n_levels[a])}
        scale_right = {lev: (block_h * 0.92) / max(right_totals[lev], 1)
                       for lev in range(axis_n_levels[a + 1])}
        # Sort: largest topic ribbons first
        sorted_keys = sorted(pair_counts.items(), key=lambda kv: -kv[1])
        for (t, lvl_l, lvl_r), cnt in sorted_keys:
            h_left = cnt * scale_left[lvl_l]
            h_right = cnt * scale_right[lvl_r]
            y0_top = lvl_l * block_h + used_left[lvl_l]
            y0_bot = y0_top + h_left
            y1_top = lvl_r * block_h + used_right[lvl_r]
            y1_bot = y1_top + h_right
            used_left[lvl_l] += h_left
            used_right[lvl_r] += h_right
            xL = axis_x[a] + axis_w / 2
            xR = axis_x[a + 1] - axis_w / 2
            xM = (xL + xR) / 2
            verts = [
                (xL, y0_top),
                (xM, y0_top),
                (xM, y1_top),
                (xR, y1_top),
                (xR, y1_bot),
                (xM, y1_bot),
                (xM, y0_bot),
                (xL, y0_bot),
            ]
            codes = [mpath.Path.MOVETO,
                     mpath.Path.CURVE4, mpath.Path.CURVE4,
                     mpath.Path.CURVE4,
                     mpath.Path.LINETO,
                     mpath.Path.CURVE4, mpath.Path.CURVE4,
                     mpath.Path.CURVE4]
            path_obj = mpath.Path(verts, codes)
            col = cmap(t % 10)
            patch = mpatches.PathPatch(path_obj, facecolor=col,
                                       edgecolor="none", alpha=0.55)
            ax.add_patch(patch)

    ax.set_xlim(-0.5, n_axes - 0.5)
    ax.set_ylim(-1.0, max(axis_n_levels) * block_h + 0.1)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    # topic legend
    handles = [mpatches.Patch(facecolor=cmap(k % 10),
                              label=f"topic {k}",
                              edgecolor="black", linewidth=0.4)
               for k in range(K)]
    ax.legend(handles=handles, loc="upper right",
              bbox_to_anchor=(1.0, 1.05), ncol=K,
              fontsize=8, frameon=False)
    fig.suptitle(
        "PORPHYRY hammock plot — topic ↔ Bt% ↔ Mb% ↔ Py% "
        "(Schonlau 2025 mixed-type parallel-coordinates idiom)",
        fontsize=11, y=0.995,
    )
    fig.tight_layout()
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "porphyry-hammock.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "porphyry-hammock.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote porphyry-hammock.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
