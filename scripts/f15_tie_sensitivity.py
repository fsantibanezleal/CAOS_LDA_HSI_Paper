"""Construction effects of the F-15 rule (P5, Section V): tied counts and forced outcomes.

Re-applies the deterministic F-15 rule of CAOS_LDA_HSI data-pipeline/build_v_sweep_f15_self_judge.py
(N = 10, tau = 3, 20 documents per cell drawn with numpy default_rng(42)) to the Q = 8 LDA fits and
documents, and reports per recipe (six-scene means):
  - the archived F-15 (data/derived/v_sweep/f15_llm_alignment/);
  - F-15 with the document's tied counts ordered as in the archive (numpy.argsort, descending), by band
    index, and at random (seeds 0-4);
  - the outcome counts over the 120 judged documents (aligned / misaligned / ambiguous);
  - how many judged documents have all non-zero counts equal (their top-10 is set by the tie order).
V15 is skipped: its archived Q = 8 document file holds the Q = 32 vocabulary.

Needs a CAOS_LDA_HSI checkout whose data/local/ holds the rebuilt V-sweep fits
(data/local/v_sweep/lda_fits/) and wordifications (data/local/wordifications/), as the judge does.

Usage: python scripts/f15_tie_sensitivity.py <path to the CAOS_LDA_HSI checkout>
"""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

SCENES = ["indian-pines-corrected", "salinas-corrected", "salinas-a-corrected",
          "pavia-university", "kennedy-space-center", "botswana"]
RECIPES = [f"V{i}" for i in range(1, 15)] + ["V17", "V18", "V19", "V20"]


def top_idx(w, n, order):
    return [int(i) for i in order[:n] if w[int(i)] > 0]


def judge(doc_top, topic_top):
    """The rule of build_v_sweep_f15_self_judge.self_judge: Y(es), N(o) or A(mbiguous)."""
    if not doc_top:
        return "A"
    ts = set(topic_top)
    ov = sum(1 for t in doc_top if t in ts)
    if ov >= 3 or doc_top[0] in set(topic_top[:5]):
        return "Y"
    if len(doc_top) >= 3 and not any(t in ts for t in doc_top[:3]):
        return "N"
    return "A" if ov == 0 else "Y"


def cell(data, recipe, scene, mode, seed=0):
    fit = data / "local" / "v_sweep" / "lda_fits" / f"{scene}_{recipe}_uniform_Q8"
    phi = np.load(fit / "phi.npy")
    theta = np.load(fit / "theta.npy")
    dt = sp.load_npz(data / "local" / "wordifications" / recipe / "uniform_Q8" / scene / "doc_term.npz").tocsr()
    idx = np.random.default_rng(42).choice(theta.shape[0], size=min(20, theta.shape[0]), replace=False)
    z = np.argmax(theta[idx], axis=1)
    topic_top = [top_idx(phi[k], 10, np.argsort(phi[k])[::-1]) for k in range(phi.shape[0])]
    rng = np.random.default_rng(seed)
    counts = {"Y": 0, "N": 0, "A": 0}
    equal = 0
    for i, d in enumerate(idx):
        w = np.asarray(dt[d].toarray()).reshape(-1).astype(np.float64)
        nz = w[w > 0]
        equal += int(nz.size > 0 and nz.max() == nz.min())
        if mode == "archived":
            order = np.argsort(w)[::-1]
        elif mode == "index":
            order = np.lexsort((np.arange(w.size), -w))
        else:
            order = np.lexsort((rng.random(w.size), -w))
        counts[judge(top_idx(w, 10, order), topic_top[int(z[i])])] += 1
    return counts, equal


def f15(counts):
    return counts["Y"] / max(counts["Y"] + counts["N"], 1)


def main() -> int:
    data = Path(sys.argv[1]) / "data"
    print("recipe stored archived-order index-order random-order(5 seeds)  aligned misaligned ambiguous  equal-count docs")
    for r in RECIPES:
        stored = st.mean(json.loads((data / "derived" / "v_sweep" / "f15_llm_alignment" /
                                     f"{s}_{r}_uniform_Q8.json").read_text(encoding="utf-8"))["f15_alignment"]
                         for s in SCENES)
        tot = {"Y": 0, "N": 0, "A": 0}
        equal = 0
        arch = []
        for s in SCENES:
            c, e = cell(data, r, s, "archived")
            arch.append(f15(c))
            equal += e
            for k in tot:
                tot[k] += c[k]
        index = st.mean(f15(cell(data, r, s, "index")[0]) for s in SCENES)
        rand = st.mean(st.mean(f15(cell(data, r, s, "random", seed)[0]) for s in SCENES) for seed in range(5))
        print(f"{r:4s} {stored:.3f} {st.mean(arch):.3f} {index:.3f} {rand:.3f}  "
              f"{tot['Y']:3d} {tot['N']:3d} {tot['A']:3d}  {equal:3d}/120")
    return 0


if __name__ == "__main__":
    sys.exit(main())
