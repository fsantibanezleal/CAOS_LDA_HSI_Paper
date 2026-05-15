"""Corner-plot matrix of GEOMET continuous assays coloured by
dominant topic.

GEOMET ships 5 geometallurgical variables (Cu rec, Mo rec, PH, Lime
cons, WI). The corner plot shows: diagonal = per-variable KDE per
topic; off-diagonal lower-triangle = scatter of variable_i vs
variable_j coloured by dominant topic. Reference:
Foreman-Mackey 2016 *corner.py* (JOSS 1(2):24, doi:10.21105/joss.00024).
Each off-diagonal cell additionally carries a 2-σ Gaussian
confidence ellipse per topic (matplotlib gallery recipe).

Reads `hidsag_topic_measurements/GEOMET.json`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms as transforms  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = (REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
       / "hidsag_topic_measurements" / "GEOMET.json")
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"


def confidence_ellipse(x, y, ax, n_std=2.0, **kwargs):
    if len(x) < 3:
        return
    cov = np.cov(x, y)
    if not np.all(np.isfinite(cov)):
        return
    pearson = cov[0, 1] / (np.sqrt(cov[0, 0] * cov[1, 1]) + 1e-12)
    if not np.isfinite(pearson):
        pearson = 0.0
    rx = np.sqrt(1 + pearson)
    ry = np.sqrt(1 - pearson)
    ell = mpatches.Ellipse((0, 0), width=rx * 2, height=ry * 2,
                           **kwargs)
    sx = np.sqrt(cov[0, 0]) * n_std
    sy = np.sqrt(cov[1, 1]) * n_std
    mx, my = np.mean(x), np.mean(y)
    transf = (transforms.Affine2D().rotate_deg(45)
              .scale(sx, sy).translate(mx, my))
    ell.set_transform(transf + ax.transData)
    ax.add_patch(ell)


def kde(values: np.ndarray, x_grid: np.ndarray,
        bw: float) -> np.ndarray:
    if len(values) == 0:
        return np.zeros_like(x_grid)
    diff = (x_grid[None, :] - values[:, None]) / bw
    return (np.exp(-0.5 * diff * diff)
            / (np.sqrt(2 * np.pi) * bw)).mean(axis=0)


def main() -> int:
    with SRC.open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    K = d["topic_count"]
    var_names = d["variable_names"]
    records = d["records"]
    M = len(var_names)
    per_topic_xy = {k: {v: [] for v in var_names} for k in range(K)}
    for r in records:
        for v in var_names:
            val = r["vars"].get(v)
            if val is not None:
                per_topic_xy[r["dominant_topic"]][v].append(val)

    cmap = plt.get_cmap("tab10")
    cell = 2.2
    fig, axes = plt.subplots(M, M, figsize=(cell * M + 1.0,
                                            cell * M + 0.5), dpi=150)

    for i in range(M):
        for j in range(M):
            ax = axes[i, j]
            vi = var_names[i]
            vj = var_names[j]
            if j > i:
                ax.set_visible(False)
                continue
            if i == j:
                all_vals = []
                for k in range(K):
                    all_vals.extend(per_topic_xy[k][vi])
                if not all_vals:
                    ax.set_visible(False); continue
                lo, hi = min(all_vals), max(all_vals)
                pad = (hi - lo) * 0.07 + 1e-9
                x_grid = np.linspace(lo - pad, hi + pad, 200)
                bw = (hi - lo) / 16 + 1e-6
                for k in range(K):
                    vals = np.array(per_topic_xy[k][vi], dtype=float)
                    if len(vals) < 1: continue
                    c = kde(vals, x_grid, bw)
                    col = cmap(k % 10)
                    ax.fill_between(x_grid, 0, c,
                                    facecolor=col, alpha=0.35,
                                    edgecolor=col, lw=1.0)
                ax.set_xlim(lo - pad, hi + pad)
                ax.set_yticks([])
            else:
                for k in range(K):
                    xs = np.array(per_topic_xy[k][vj], dtype=float)
                    ys = np.array(per_topic_xy[k][vi], dtype=float)
                    if len(xs) < 1: continue
                    col = cmap(k % 10)
                    ax.scatter(xs, ys, s=14, c=[col], alpha=0.6,
                               edgecolor="black", linewidth=0.25)
                    if len(xs) > 4:
                        confidence_ellipse(xs, ys, ax, n_std=2.0,
                                           facecolor="none",
                                           edgecolor=col, lw=1.0,
                                           alpha=0.85)
            if j == 0 and i > 0:
                ax.set_ylabel(vi, fontsize=8.5)
            else:
                ax.set_yticklabels([])
            if i == M - 1:
                ax.set_xlabel(vj, fontsize=8.5)
                ax.tick_params(labelsize=7.5)
            else:
                ax.set_xticklabels([])
            ax.tick_params(labelsize=7.5)
            ax.grid(alpha=0.18)

    # legend
    handles = [mpatches.Patch(facecolor=cmap(k % 10),
                              edgecolor="black", linewidth=0.4,
                              label=f"topic {k}")
               for k in range(K)]
    fig.legend(handles=handles, loc="upper right",
               bbox_to_anchor=(0.99, 0.99), ncol=1,
               fontsize=9, frameon=False)
    fig.suptitle(
        "GEOMET corner plot — 5 assays vs dominant topic "
        f"(K={K}; off-diagonal = 2σ Gaussian confidence ellipses; "
        "diagonal = KDE per topic). Foreman-Mackey 2016 *corner.py* idiom.",
        fontsize=10.5, y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hidsag-corner-geomet.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "hidsag-corner-geomet.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hidsag-corner-geomet.{{svg,pdf}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
