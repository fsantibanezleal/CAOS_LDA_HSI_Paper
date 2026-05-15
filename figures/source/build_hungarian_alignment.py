"""Build the REAL Hungarian-alignment confusion-matrix figure for
Salinas-A under the SWIR-only band mask.

Loads the actual dominant-topic maps (canonical + masked) as uint8
arrays and computes the per-cell confusion matrix on pixels labelled
in BOTH maps (sentinel 255 excluded). The Hungarian permutation
sigma* is read from canonical_comparison.json and overlaid on the
matched cells. This replaces an earlier stylised version that
distributed the recorded swap-mass uniformly off-diagonal.

Source artefacts:
  - data/derived/topic_to_data/salinas-a-corrected_dominant_topic_map.bin
  - data/derived/band_masks/salinas-a-corrected/swir/dominant_topic_map.bin
  - data/derived/band_masks/canonical_comparison.json
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
COMPARISON_JSON = SRC / "band_masks" / "canonical_comparison.json"
CANON_BIN = SRC / "topic_to_data" / "salinas-a-corrected_dominant_topic_map.bin"
MASKED_BIN = SRC / "band_masks" / "salinas-a-corrected" / "swir" / "dominant_topic_map.bin"

OUT_DIR = REPO_ROOT / "figures"
CONF_FIG_DIR = REPO_ROOT / "conference" / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

SCENE_ID = "salinas-a-corrected"
MASK_ID = "swir"
SENTINEL = 255


def main() -> int:
    for p in (COMPARISON_JSON, CANON_BIN, MASKED_BIN):
        if not p.exists():
            print(f"ERROR: missing artefact: {p}", file=sys.stderr)
            return 2

    with COMPARISON_JSON.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    entry = next(
        e for e in payload["entries"]
        if e["scene_id"] == SCENE_ID and e["mask_id"] == MASK_ID
    )
    sigma = {int(k): int(v) for k, v in entry["hungarian_assignment"].items()}
    K_canon = entry["topic_count_canonical"]
    K_masked = entry["topic_count_masked"]
    paired_ari = entry["paired_ari_dominant_topics"]
    swap_rate = entry["swap_rate_under_hungarian_alignment"]
    n_paired = entry["n_paired_pixels"]

    canon = np.fromfile(CANON_BIN, dtype=np.uint8)
    masked = np.fromfile(MASKED_BIN, dtype=np.uint8)
    assert canon.shape == masked.shape
    keep = (canon != SENTINEL) & (masked != SENTINEL)
    canon_v = canon[keep]
    masked_v = masked[keep]
    if canon_v.shape[0] != n_paired:
        print(f"WARN: paired pixels {canon_v.shape[0]} != JSON n_paired_pixels "
              f"{n_paired} (proceeding with on-disk count)")

    C = np.zeros((K_canon, K_masked), dtype=int)
    for k_c, k_m in zip(canon_v, masked_v):
        C[int(k_c), int(k_m)] += 1

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.0), dpi=150,
                             gridspec_kw={"width_ratios": [1.0, 1.0]})

    ax = axes[0]
    im = ax.imshow(C, cmap="magma", aspect="auto")
    ax.set_xticks(range(K_masked))
    ax.set_yticks(range(K_canon))
    ax.set_xticklabels([f"m{j}" for j in range(K_masked)], fontsize=9)
    ax.set_yticklabels([f"c{k}" for k in range(K_canon)], fontsize=9)
    ax.set_xlabel("masked topic id (SWIR-only)", fontsize=10)
    ax.set_ylabel("canonical topic id", fontsize=10)
    ax.set_title("(a) confusion matrix (real pixel counts)", fontsize=10)
    for i in range(K_canon):
        for j in range(K_masked):
            v = int(C[i, j])
            colour = "white" if v < C.max() * 0.5 else "black"
            ax.text(j, i, f"{v}", ha="center", va="center",
                    fontsize=8, color=colour)
    for k_c, k_m in sigma.items():
        ax.add_patch(plt.Rectangle((k_m - 0.5, k_c - 0.5), 1, 1,
                                   fill=False, edgecolor="lime", lw=1.8))
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).set_label(
        "pixels", fontsize=9)

    # Right panel: permutation-realigned diagonal mass
    ax2 = axes[1]
    realign = np.zeros((K_canon, K_masked), dtype=float)
    for k_c, k_m in sigma.items():
        realign[k_c, k_c] = C[k_c, k_m]
        for j in range(K_masked):
            if j != k_m:
                realign[k_c, sigma_inverse(sigma, j)] += C[k_c, j]
    im2 = ax2.imshow(realign, cmap="magma", aspect="auto")
    ax2.set_xticks(range(K_canon))
    ax2.set_yticks(range(K_canon))
    ax2.set_xticklabels([f"c{k}" for k in range(K_canon)], fontsize=9)
    ax2.set_yticklabels([f"c{k}" for k in range(K_canon)], fontsize=9)
    ax2.set_xlabel("masked topic id (Hungarian-relabelled)", fontsize=10)
    ax2.set_ylabel("canonical topic id", fontsize=10)
    ax2.set_title("(b) post-permutation: diagonal=matched mass", fontsize=10)
    for i in range(K_canon):
        for j in range(K_canon):
            v = int(realign[i, j])
            colour = "white" if v < realign.max() * 0.5 else "black"
            ax2.text(j, i, f"{v}", ha="center", va="center",
                     fontsize=8, color=colour)
    fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04).set_label(
        "pixels", fontsize=9)

    fig.suptitle(
        f"Hungarian alignment on Salinas-A (SWIR mask) — "
        f"paired ARI = {paired_ari:.3f}, swap rate = {swap_rate:.3f}, "
        f"n = {canon_v.shape[0]} px",
        fontsize=10, y=1.02,
    )
    fig.tight_layout()

    for outdir in (OUT_DIR, CONF_FIG_DIR, JOUR_FIG_DIR):
        outdir.mkdir(parents=True, exist_ok=True)
        fig.savefig(outdir / "hungarian-alignment-example.svg", format="svg",
                    bbox_inches="tight")
        fig.savefig(outdir / "hungarian-alignment-example.pdf", format="pdf",
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote hungarian-alignment-example.{{svg,pdf}} (real confusion "
          f"matrix) to {OUT_DIR}, {CONF_FIG_DIR}, {JOUR_FIG_DIR}")
    return 0


def sigma_inverse(sigma: dict, masked_id: int) -> int:
    for k_c, k_m in sigma.items():
        if k_m == masked_id:
            return k_c
    return masked_id


if __name__ == "__main__":
    sys.exit(main())
