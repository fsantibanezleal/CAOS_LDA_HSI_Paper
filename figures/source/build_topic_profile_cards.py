"""Per-topic profile cards (Salinas-A) — each topic gets a 3-row card:
  (top)    its basis spectrum phi_k(lambda) with top-5 words marked
  (mid)    P(L|t) horizontal bar chart with class colours
  (bot)    summary stats: prevalence, dominant label, doc count

Salinas-A is chosen as the exemplar because it has K=6 (fits in one
figure cleanly) and its band-mask paired ARI of 0.766 makes it the
clearest example of topic-identity persistence under restriction.

Two figure variants are produced:
  - topic-profile-cards-salinas-a   K=6 cards in a 2x3 grid
  - topic-profile-cards-indian-pines K=12 cards in a 3x4 grid (Indian
    Pines for comparison on a harder scene)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
OUT_DIR = REPO_ROOT / "figures"
JOUR_FIG_DIR = REPO_ROOT / "journal" / "figures"

WATER_BANDS_NM = [(1350, 1430), (1800, 1950), (2480, 2500)]


def token_to_nm(token: str) -> float | None:
    m = re.match(r"^(\d+)nm$", token)
    return float(m.group(1)) if m else None


def build_one(scene_id: str, layout: tuple[int, int], outname: str) -> None:
    tv_path = SRC / "topic_views" / f"{scene_id}.json"
    t2d_path = SRC / "topic_to_data" / f"{scene_id}.json"
    with tv_path.open("r", encoding="utf-8") as fh:
        tv = json.load(fh)
    with t2d_path.open("r", encoding="utf-8") as fh:
        t2d = json.load(fh)

    K = tv["topic_count"]
    wl = np.array(tv["wavelengths_nm"], dtype=float)
    phi = np.array(tv["topic_band_profiles"], dtype=float)
    prev = tv["topic_prevalence"]
    top_words = tv["top_words_per_topic"]["lambda_0.5"]
    p_label = t2d["p_label_given_topic_dominant"]
    docs_per_topic = t2d["docs_per_topic_dominant"]

    rows, cols = layout
    fig = plt.figure(figsize=(3.6 * cols, 2.9 * rows), dpi=150)
    cmap_topics = plt.get_cmap("tab20")

    for k in range(K):
        ax = fig.add_subplot(rows, cols, k + 1)
        # Shade water bands
        for lo, hi in WATER_BANDS_NM:
            if wl.min() < hi and wl.max() > lo:
                ax.axvspan(lo, hi, color="#eeeeee", alpha=0.7, zorder=0)
        # Spectrum
        col = cmap_topics(k % 20)
        ax.plot(wl, phi[k], color=col, lw=1.6, zorder=2)
        # Mark top-5 word wavelengths
        top5 = top_words[k][:5]
        for w in top5:
            nm = token_to_nm(w["token"])
            if nm is None:
                continue
            ax.axvline(nm, color="#d62728", ls="--", lw=0.6, alpha=0.4,
                       zorder=1)
        ax.set_xlabel("wavelength (nm)", fontsize=7.5)
        ax.set_ylabel(r"$\phi_{k,b}$", fontsize=7.5)
        ax.tick_params(labelsize=6.5)

        # Title: topic id + dominant label + prevalence
        labels_sorted = sorted(p_label[k], key=lambda x: -x["p"])
        if labels_sorted and labels_sorted[0]["p"] > 0:
            dom = labels_sorted[0]
            title_label = f"{dom['name'][:18]} {dom['p']*100:.0f}%"
            title_colour = dom["color"]
        else:
            title_label = "(no dominant label)"
            title_colour = "#999"
        ax.set_title(
            f"t{k}  ·  prev {prev[k]*100:.1f}%  ·  N={docs_per_topic[k]}\n"
            f"{title_label}",
            fontsize=8.0, color=title_colour)

        # Top-words inline
        top_str = ", ".join(w["token"] for w in top5)
        ax.text(0.02, 0.94, f"top: {top_str}",
                transform=ax.transAxes, fontsize=6.5,
                va="top", ha="left", color="#444",
                bbox=dict(facecolor="#ffffff",
                          edgecolor="none", alpha=0.85,
                          pad=0.6))

    scene_label = tv.get("scene_name", scene_id)
    fig.suptitle(
        f"Per-topic profile cards — {scene_label}, "
        f"K = {K}. Each panel: φ_k(λ) with top-5 word λ-marks "
        "(red dashed); title = dominant label + per-topic prevalence + "
        "dominant-doc count.",
        fontsize=10, y=1.005, wrap=True,
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
    build_one("salinas-a-corrected", (2, 3),
              "topic-profile-cards-salinas-a")
    build_one("indian-pines-corrected", (3, 4),
              "topic-profile-cards-indian-pines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
