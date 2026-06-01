#!/usr/bin/env python
"""Build the two P5 (interpretability) figures from the V-sweep doc-term data.

Outputs (vector PDF, into ../figures/):
  p5-dispersion-scatter.pdf  : mechanism plot. Per-recipe mean topic-word
      token-mass dispersion N_eff = exp(H(phi_k)) (x, log scale) vs F-15
      LLM-judge alignment (y), point size keyed to nominal |V|. The F-15
      rule compares a topic's top-N against a document's top-N, so the
      relevant dispersion is that of the topic-word distribution phi_k:
      a topic whose mass is spread over many tokens (high N_eff) rarely
      sees its top-N overlap a document's top-N, depressing F-15. The
      decisive comparison is the three large-|V| recipes that share the
      identical 1376-token alphabet: V3 (N_eff~444), V12 (~393) and
      V20 (~300). They differ only in phi dispersion, and F-15 tracks
      that ordering (0.12 / 0.16 / 0.64), not their identical |V|.
  p5-f15-vocab.pdf           : refutation plot. F-15 (y) vs nominal |V|
      (x, log scale). If F-15 were a pure vocabulary-size artefact the
      points would lie on a monotone curve; V14 (|V|=1024) and V20
      (|V|=1376) break it, refuting the pure-cardinality hypothesis.

N_eff is eq:dispersion applied to the LDA topic-word distribution phi_k
(rather than the raw per-document counts p_d): both are valid instances
of the same effective-support functional, and the topic-word version is
the quantity the topic-side of the F-15 rule actually reads. All numbers
are computed from the LDA fits (uniform Q=8, phi.npy) averaged over the
six labelled scenes and their topics, paired with the F-15 alignment
JSONs under data/derived/v_sweep/f15_llm_alignment/. LDA backbone only.
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HSI_ROOT = "d:/_Repos/_Web_Projects/CAOS_LDA_HSI"
WORDIF = os.path.join(HSI_ROOT, "data", "local", "wordifications")
FITS = os.path.join(HSI_ROOT, "data", "local", "v_sweep", "lda_fits")
F15_DIR = os.path.join(HSI_ROOT, "data", "derived", "v_sweep",
                       "f15_llm_alignment")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")

SCENES = [
    "indian-pines-corrected",
    "salinas-corrected",
    "salinas-a-corrected",
    "pavia-university",
    "kennedy-space-center",
    "botswana",
]

# Recipes that exist as uniform_Q8 wordifications under the LDA sweep.
RECIPES = ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10",
           "V11", "V12", "V13", "V14", "V15", "V17", "V18", "V19", "V20"]


def _neff(p):
    """Effective support N_eff = exp(H(p)) of a non-negative mass vector."""
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]
    if p.size == 0:
        return 0.0
    p = p / p.sum()
    H = -float(np.sum(p * np.log(p)))
    return float(np.exp(H))


def neff_for_cell(recipe, scene):
    """Mean per-topic effective vocabulary N_eff = exp(H(phi_k)) and |V|.

    eq:dispersion applied to the LDA topic-word distribution phi_k. The
    topic-side of the F-15 rule reads top-N(phi_{z}); a topic with high
    N_eff spreads its mass over many tokens, so its top-N rarely overlaps
    a document's top-N. |V| is taken from the wordification doc-term matrix.
    """
    phi_path = os.path.join(FITS, f"{scene}_{recipe}_uniform_Q8", "phi.npy")
    if not os.path.isfile(phi_path):
        return None, None
    phi = np.load(phi_path)  # K x V
    vocab_dim = int(phi.shape[1])
    neffs = [_neff(phi[k]) for k in range(phi.shape[0])]
    if not neffs:
        return None, vocab_dim
    return float(np.mean(neffs)), vocab_dim


def f15_for_cell(recipe, scene):
    p = os.path.join(F15_DIR, f"{scene}_{recipe}_uniform_Q8.json")
    if not os.path.isfile(p):
        return None
    d = json.load(open(p))
    return float(d.get("f15_alignment"))


def main():
    rows = []
    for r in RECIPES:
        neffs, vocabs, f15s = [], [], []
        for s in SCENES:
            ne, vd = neff_for_cell(r, s)
            f = f15_for_cell(r, s)
            if ne is not None:
                neffs.append(ne)
                vocabs.append(vd)
            if f is not None:
                f15s.append(f)
        if not neffs or not f15s:
            print(f"  skip {r}: neff={len(neffs)} f15={len(f15s)}")
            continue
        rows.append({
            "recipe": r,
            "neff": float(np.mean(neffs)),
            "vocab": int(round(np.mean(vocabs))),
            "f15": float(np.mean(f15s)),
        })
        print(f"  {r:>4}  N_eff={np.mean(neffs):8.2f}  "
              f"|V|={int(round(np.mean(vocabs))):5d}  "
              f"F-15={np.mean(f15s):.3f}")

    os.makedirs(OUT_DIR, exist_ok=True)
    # dump computed numbers for provenance / paper text
    with open(os.path.join(OUT_DIR, "p5-dispersion-data.json"), "w") as fh:
        json.dump(rows, fh, indent=2)

    recipes = [x["recipe"] for x in rows]
    neff = np.array([x["neff"] for x in rows])
    vocab = np.array([x["vocab"] for x in rows], dtype=float)
    f15 = np.array([x["f15"] for x in rows])

    # ---- Figure 1: dispersion mechanism scatter -----------------------
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    # point size keyed to log |V|
    sizes = 30 + 70 * (np.log10(vocab) - np.log10(vocab.min())) / (
        np.log10(vocab.max()) - np.log10(vocab.min()) + 1e-9)
    sc = ax.scatter(neff, f15, s=sizes ** 1.0 * 3.0, c=np.log10(vocab),
                    cmap="viridis", edgecolor="black", linewidth=0.5,
                    zorder=3)
    for x, y, name in zip(neff, f15, recipes):
        dx = 1.04
        ax.annotate(name, (x, y), xytext=(x * dx, y), fontsize=7,
                    va="center", zorder=4)
    ax.set_xscale("log")
    ax.set_xlabel(r"topic-word dispersion  $\overline{N_{\mathrm{eff}}}"
                  r"=\exp(H(\phi_k))$  (per-topic mean, log scale)")
    ax.set_ylabel(r"F-15 LLM-judge alignment")
    ax.set_ylim(-0.05, 1.08)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label(r"$\log_{10}|\mathcal{V}|$  (nominal vocabulary)")
    ax.set_title("At fixed $|\\mathcal{V}|$=1376 (V3,V12,V20) F-15 tracks "
                 "dispersion, not cardinality", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "p5-dispersion-scatter.pdf"))
    plt.close(fig)

    # ---- Figure 2: F-15 vs nominal |V| (refutation) -------------------
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    ax.scatter(vocab, f15, s=42, c="#34507a", edgecolor="black",
               linewidth=0.5, zorder=3)
    for x, y, name in zip(vocab, f15, recipes):
        ax.annotate(name, (x, y), xytext=(x * 1.05, y), fontsize=7,
                    va="center", zorder=4)
    # highlight the two large-vocab high-F15 counterexamples
    hl = [(x, y, n) for x, y, n in zip(vocab, f15, recipes)
          if n in ("V14", "V20")]
    if hl:
        hx, hy, _ = zip(*hl)
        ax.scatter(hx, hy, s=140, facecolor="none", edgecolor="#c0392b",
                   linewidth=1.6, zorder=2,
                   label="large $|\\mathcal{V}|$ yet high F-15")
    ax.set_xscale("log")
    ax.set_xlabel(r"nominal vocabulary $|\mathcal{V}|$  (log scale)")
    ax.set_ylabel(r"F-15 LLM-judge alignment")
    ax.set_ylim(-0.05, 1.08)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)
    ax.legend(fontsize=7, loc="lower left")
    ax.set_title("F-15 vs vocabulary cardinality: V14 / V20 break monotonicity",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "p5-f15-vocab.pdf"))
    plt.close(fig)

    print("Wrote figures to", os.path.abspath(OUT_DIR))


if __name__ == "__main__":
    main()
