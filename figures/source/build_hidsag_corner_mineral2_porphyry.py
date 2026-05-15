"""Extended corner plots for MINERAL2 + PORPHYRY HIDSAG subsets.

Mirrors `build_hidsag_corner_geomet.py` for two additional subsets,
auto-selecting the 5 variables with the largest normalised
per-topic-mean range so the figure focuses on the strongest topic-
versus-assay discriminations.

MINERAL2 = high-sulfidation epithermal mineralogy (small sample,
N=20); the alunite/Al-OH/pyrophyllite signature is the canonical
porphyry-Cu lithocap motif.

PORPHYRY = porphyry-copper-deposit mineralogy. The Bt% (biotite)
signature is the strongest single discriminator in the entire
HIDSAG layer (per-topic means range 1.1..39.6); this corner plot
embeds Bt% alongside Mb%, Qz%, Py%, and the combined sulfide
[Cpy+Py+Bo]% so the K=6 topic clusters can be inspected in the
operational-decision-relevant assay space.

Reference: Foreman-Mackey 2016 corner.py JOSS 1(2):24.
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
       / "hidsag_topic_measurements")
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


def select_top_vars(payload, n: int = 5) -> list[str]:
    K = payload["topic_count"]
    stats = payload["per_topic_var_stats"]
    scored = []
    for v in payload["variable_names"]:
        means = [stats[str(k)][v].get("mean")
                 for k in range(K)
                 if stats[str(k)][v].get("n", 0) > 0]
        means = [m for m in means if m is not None]
        if len(means) < 2:
            continue
        rng = max(means) - min(means)
        scale = max(abs(max(means)), abs(min(means)), 1e-6)
        nrng = rng / scale
        scored.append((nrng, v))
    scored.sort(reverse=True)
    return [v for _, v in scored[:n]]


def build_one(subset: str, outname: str, title_suffix: str) -> None:
    with (SRC / f"{subset}.json").open("r", encoding="utf-8") as fh:
        d = json.load(fh)
    K = d["topic_count"]
    var_names = select_top_vars(d, n=5)
    M = len(var_names)
    per_topic_xy = {k: {v: [] for v in var_names} for k in range(K)}
    for r in d["records"]:
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
                ax.set_visible(False); continue
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
    handles = [mpatches.Patch(facecolor=cmap(k % 10),
                              edgecolor="black", linewidth=0.4,
                              label=f"topic {k}")
               for k in range(K)]
    fig.legend(handles=handles, loc="upper right",
               bbox_to_anchor=(0.99, 0.99), ncol=1,
               fontsize=9, frameon=False)
    fig.suptitle(
        f"{subset} corner plot — 5 most-discriminative assays vs "
        f"dominant topic (K={K}). {title_suffix}",
        fontsize=10.5, y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / f"{outname}.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / f"{outname}.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {outname}.{{svg,pdf}}")


def main() -> int:
    build_one("MINERAL2", "hidsag-corner-mineral2",
              "High-sulfidation epithermal mineralogy.")
    build_one("PORPHYRY", "hidsag-corner-porphyry",
              "Porphyry-copper-deposit signature.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
