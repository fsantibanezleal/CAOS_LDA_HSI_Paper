"""Build the F-1 method-comparison figure for the journal manuscript.

Four-panel layout:
  (a) Labelled scenes: mean paired macro-F1 difference of each method from
      raw_logistic over the 30 (scene, fold) cells, with the 94 % paired
      bootstrap interval (B = 5000, numpy default_rng(42)).
  (b) Labelled scenes: pairwise P[A > B] from the hierarchical Bayesian model.
  (c) HIDSAG: the same paired difference over the 19 (subset, target) cells.
  (d) HIDSAG: pairwise P[A > B] from the hierarchical Bayesian model.

The panels (a) and (c) replace a forest plot of the posterior method
locations mu_m: the model score = mu_m + delta_s + rho_f + eps fixes no
reference scene, so mu_m is identified only up to the scene offsets and its
94 % HDI extended beyond the [0, 1] range of macro-F1. Differences between
methods are identified and are what the figure shows. The five folds of a
scene share training pixels, so the paired intervals are narrower than a
resampling of independent cells would give.

Source artefacts (CAOS_LDA_HSI, data/derived/):
  - topic_routed_classifier/<scene>.json (per-fold macro-F1, labelled scenes)
  - core/local_core_benchmarks.json (per-target macro-F1, HIDSAG)
  - method_statistics_labelled/cross_classification_bayesian.json
  - method_statistics_hidsag/cross_classification_bayesian.json
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
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
LBL_JSON = SRC / "method_statistics_labelled" / "cross_classification_bayesian.json"
HID_JSON = SRC / "method_statistics_hidsag" / "cross_classification_bayesian.json"
TR_DIR = SRC / "topic_routed_classifier"
BENCH_JSON = SRC / "core" / "local_core_benchmarks.json"

OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"
B = 5000

SHORT = {
    "pca_K_logistic": "PCA-K + logreg",
    "raw_logistic": "raw + logreg",
    "theta_logistic": "θ + logreg",
    "topic_routed_hard": "topic-routed (hard)",
    "topic_routed_soft": "topic-routed (soft)",
    "cube_topic_logistic_regression": "cube-topic + logreg",
    "pca_logistic_regression": "PCA + logreg",
    "raw_logistic_regression": "raw + logreg",
    "region_topic_logistic_regression": "region-topic + logreg",
    "topic_logistic_regression": "θ + logreg",
}


def labelled_cells() -> dict:
    """method -> {(scene, fold): macro-F1}, pca_<K>_logistic pooled as pca_K_logistic
    (as build_bayesian_classification_labelled does)."""
    out: dict = {}
    for path in sorted(TR_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        scene = payload.get("scene_id") or path.stem
        for raw_method, block in payload.get("method_metrics", {}).items():
            method = "pca_K_logistic" if raw_method.startswith("pca_") and raw_method.endswith("_logistic") else raw_method
            for f, score in enumerate((block.get("macro_f1") or {}).get("per_fold") or []):
                out.setdefault(method, {})[(scene, f)] = float(score)
    return out


def hidsag_cells() -> dict:
    """method -> {(subset, target): macro-F1}, as build_bayesian_method_comparison collects them."""
    bench = json.loads(BENCH_JSON.read_text(encoding="utf-8"))
    out: dict = {}
    for run in bench.get("measured_target_runs", []) or []:
        for task in run.get("classification_tasks", []) or []:
            for method, block in (task.get("metrics") or {}).items():
                val = block.get("macro_f1")
                if val is not None and np.isfinite(val):
                    out.setdefault(method, {})[(run.get("subset_code"), str(task.get("target")))] = float(val)
    return out


def paired_summary(cells: dict, ref: str) -> dict:
    """method -> (observed mean, mean difference from ref, 3 %, 97 % bootstrap quantiles)."""
    keys = sorted(cells[ref])
    base = np.array([cells[ref][k] for k in keys])
    out = {}
    for m, sc in cells.items():
        v = np.array([sc[k] for k in keys])
        d = v - base
        if m == ref:
            out[m] = (float(v.mean()), 0.0, 0.0, 0.0)
            continue
        idx = np.random.default_rng(42).integers(0, d.size, size=(B, d.size))
        lo, hi = np.quantile(d[idx].mean(axis=1), [0.03, 0.97])
        out[m] = (float(v.mean()), float(d.mean()), float(lo), float(hi))
    return out


def difference_panel(ax, summary: dict, ref: str, n_cells: int, title: str) -> list:
    names = sorted(summary, key=lambda m: summary[m][0])
    y = np.arange(len(names))
    for yi, m in zip(y, names):
        mean, dm, lo, hi = summary[m]
        if m == ref:
            ax.plot(0.0, yi, "D", color="#555555", ms=6)
            ax.text(0.012, yi, f"reference, mean {mean:.3f}", fontsize=7.5, va="center", color="#333")
            continue
        ax.hlines(yi, lo, hi, color="#999999", lw=2.2)
        ax.plot(dm, yi, "o", color="#1f77b4", ms=7, markeredgecolor="black", markeredgewidth=0.6)
        ax.text(max(hi, 0.0) + 0.012, yi, f"Δ={dm:+.3f} (mean {mean:.3f})", fontsize=7.5, va="center", color="#333")
    ax.axvline(0.0, ls="--", color="#aaaaaa", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT.get(n, n) for n in names], fontsize=8.5)
    ax.set_xlabel(f"macro-F1 difference from raw + logreg ({n_cells} paired cells, 94% bootstrap)", fontsize=8.5)
    ax.set_xlim(-0.48, 0.25)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="x", alpha=0.25)
    return names


def pairwise_panel(ax, payload, names_in_order: list, title: str) -> None:
    pair = payload["pairwise_p_a_gt_b"]
    n = len(names_in_order)
    M = np.full((n, n), np.nan, dtype=float)
    for i, a in enumerate(names_in_order):
        for j, b in enumerate(names_in_order):
            if a == b:
                continue
            M[i, j] = pair[a][b]
    cmap = plt.get_cmap("RdYlGn").copy()
    cmap.set_bad(color="#dddddd")
    masked = np.ma.masked_invalid(M)
    ax.imshow(masked, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    short = [SHORT.get(n, n) for n in names_in_order]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(short, rotation=30, ha="right", fontsize=7.5)
    ax.set_yticklabels(short, fontsize=7.5)
    for i in range(n):
        for j in range(n):
            if np.isnan(M[i, j]):
                ax.text(j, i, "–", ha="center", va="center", fontsize=7.5,
                        color="#777")
                continue
            v = M[i, j]
            colour = "white" if (v < 0.30 or v > 0.70) else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=7.5, color=colour)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("vs method B (col)", fontsize=9)
    ax.set_ylabel("method A (row)", fontsize=9)


def main() -> int:
    for p in (LBL_JSON, HID_JSON, BENCH_JSON):
        if not p.exists():
            print(f"ERROR: missing artefact: {p}", file=sys.stderr)
            return 2
    if not TR_DIR.exists():
        print(f"ERROR: missing artefact folder: {TR_DIR}", file=sys.stderr)
        return 2

    labelled = json.loads(LBL_JSON.read_text(encoding="utf-8"))
    hidsag = json.loads(HID_JSON.read_text(encoding="utf-8"))
    lbl = paired_summary(labelled_cells(), "raw_logistic")
    hid = paired_summary(hidsag_cells(), "raw_logistic_regression")
    for name, s in (("labelled", lbl), ("HIDSAG", hid)):
        for m, (mean, dm, lo, hi) in sorted(s.items(), key=lambda t: -t[1][0]):
            print(f"  {name:8s} {m:34s} mean {mean:.4f}  diff {dm:+.4f} [{lo:+.4f}, {hi:+.4f}]")

    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.0), dpi=150,
                             gridspec_kw={"width_ratios": [1.0, 1.05]})
    lbl_order = difference_panel(axes[0, 0], lbl, "raw_logistic", 30,
                                 "(a) Labelled scenes: paired difference")
    pairwise_panel(axes[0, 1], labelled, lbl_order,
                   "(b) Labelled scenes: P[A > B] (hierarchical model)")
    hid_order = difference_panel(axes[1, 0], hid, "raw_logistic_regression", 19,
                                 "(c) HIDSAG: paired difference")
    pairwise_panel(axes[1, 1], hidsag, hid_order,
                   "(d) HIDSAG: P[A > B] (hierarchical model)")

    fig.suptitle(
        "Method comparison on axis F-1: paired macro-F1 differences and "
        "hierarchical-model P[A > B]",
        fontsize=11, y=1.00,
    )
    fig.tight_layout()

    for outdir in (OUT_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "bayesian-method-comparison.svg",
                    format="svg", bbox_inches="tight")
        fig.savefig(outdir / "bayesian-method-comparison.pdf",
                    format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote bayesian-method-comparison.{{svg,pdf}} "
          f"(paired differences + pairwise P[A>B] heatmap) to {OUT_DIR}, {JOUR_FIG_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
