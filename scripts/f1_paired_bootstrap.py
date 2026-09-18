"""Paired bootstrap of the V-sweep F-1 scores and the nineteen-recipe F-1 table (P3, Section IX and Table XII).

Reads the per-fold F-1 records archived in CAOS_LDA_HSI (data/derived/v_sweep/f1_per_fold/, one JSON per scene,
recipe and Q) for the uniform Q = 8 sweep and prints:
  - the per-scene and six-scene mean macro-F1 of topic_routed_soft for all nineteen recipes, as LaTeX rows
    (bold = the full-precision best per scene, exact ties included, as in Table II);
  - for every recipe, the mean difference from V12 over the 30 (scene, fold) cells and its paired bootstrap
    interval: 3 % and 97 % quantiles of B = 5000 resamples of the 30 differences (numpy default_rng(42),
    one generator per comparison).
All recipes share the stratified sample and the StratifiedKFold split (random_state 42) of each scene, so the
fold scores pair across recipes. The five folds of a scene share training pixels, so these intervals are
narrower than a resampling of independent cells would give.

Usage: python scripts/f1_paired_bootstrap.py <path to the CAOS_LDA_HSI checkout>
"""
import json
import sys
from pathlib import Path

import numpy as np

SCENES = [("botswana", "Botswana"), ("indian-pines-corrected", "Indian Pines"),
          ("kennedy-space-center", "Kennedy SC"), ("pavia-university", "Pavia U"),
          ("salinas-a-corrected", "Salinas-A"), ("salinas-corrected", "Salinas")]
RECIPES = [f"V{i}" for i in range(1, 16)] + ["V17", "V18", "V19", "V20"]
B = 5000


def main() -> int:
    root = Path(sys.argv[1]) / "data" / "derived" / "v_sweep" / "f1_per_fold"
    rec = {(s, r): json.loads((root / f"{s}_{r}_uniform_Q8.json").read_text(encoding="utf-8"))
           for s, _ in SCENES for r in RECIPES}
    for (s, r), x in rec.items():
        assert x["status"] == "ok" and len(x["topic_routed_soft_per_fold"]) == 5, (s, r)
        assert x["D"] == rec[(s, "V1")]["D"], (s, r)  # same stratified sample in every recipe

    print("% Table XII rows: topic_routed_soft macro-F1, uniform Q = 8")
    for s, name in SCENES:
        vals = {r: rec[(s, r)]["topic_routed_soft_mean"] for r in RECIPES}
        top = max(vals.values())
        cells = [f"\\textbf{{{v:.3f}}}" if v == top else f"{v:.3f}" for v in vals.values()]
        print(f"{name:12s} & " + " & ".join(cells) + r" \\")
    means = {r: float(np.mean([rec[(s, r)]["topic_routed_soft_mean"] for s, _ in SCENES])) for r in RECIPES}
    top = max(means.values())
    print("mean         & " + " & ".join(f"\\textbf{{{v:.3f}}}" if v == top else f"{v:.3f}"
                                          for v in means.values()) + r" \\")
    print()
    print("% six-scene means, descending")
    for r, m in sorted(means.items(), key=lambda t: -t[1]):
        print(f"%   {r:4s} {m:.4f}")
    print()

    def folds(r):
        return np.array([f for s, _ in SCENES for f in rec[(s, r)]["topic_routed_soft_per_fold"]])

    ref = folds("V12")
    print("% V12 minus recipe: mean difference, paired 94 % bootstrap interval, cells where V12 is higher")
    for r in RECIPES:
        if r == "V12":
            continue
        d = ref - folds(r)
        idx = np.random.default_rng(42).integers(0, d.size, size=(B, d.size))
        lo, hi = np.quantile(d[idx].mean(axis=1), [0.03, 0.97])
        print(f"%   V12-{r:4s} {d.mean():+.4f}  [{lo:+.4f}, {hi:+.4f}]  {int((d > 0).sum())}/{d.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
