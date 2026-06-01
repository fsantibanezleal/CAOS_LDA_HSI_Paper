"""P4 figure — schematic of the four backbone priors' document-topic geometry.

A pure-matplotlib, data-free schematic (no numbers invented) that contrasts
the geometric assumption each backbone imposes on the per-document topic
distribution theta:

  - LDA      : Dirichlet on the (K-1)-simplex  -> a bounded triangle of mass.
  - HDP      : stick-breaking / GEM            -> an unbounded, self-truncating
                                                   ladder of stick lengths.
  - ProdLDA  : logistic-normal                 -> a Gaussian blob in the
                                                   softmax-pre-image, warped
                                                   onto the simplex.
  - ETM      : embedding directions            -> topics are unit vectors in a
                                                   shared word/topic embedding
                                                   space; theta is a softmax of
                                                   inner products.

This figure motivates why the SAME wordification can rank differently per
backbone (the P4 result): the prior geometry, not the vocabulary, drives the
re-ranking. It carries no measured quantities, only the qualitative shapes.

Output: figures/p4-prior-geometry.{pdf,png}
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "figures"

RNG = np.random.default_rng(20)  # fixed seed -> deterministic schematic clouds

ACCENT = {
    "LDA": "#2563eb", "HDP": "#16a34a",
    "ProdLDA": "#d97706", "ETM": "#9333ea",
}


def _clean(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# --------------------------------------------------------------------------
def panel_lda(ax):
    c = ACCENT["LDA"]
    # 2-simplex triangle (K=3).
    tri = np.array([[0.5, 0.92], [0.08, 0.12], [0.92, 0.12]])
    ax.add_patch(Polygon(tri, closed=True, facecolor="#dbeafe",
                         edgecolor=c, linewidth=1.8, zorder=1))
    for (x, y), lab in zip(tri, ["topic 1", "topic 2", "topic 3"]):
        ax.scatter(x, y, s=42, color=c, zorder=4)
        dy = 0.045 if y > 0.5 else -0.055
        ax.text(x, y + dy, lab, ha="center",
                va="bottom" if dy > 0 else "top", fontsize=8, color="#0f172a")

    # Dirichlet draws concentrated toward a vertex/edge (sparse, alpha<1).
    def bary(a):
        return a @ tri
    draws = RNG.dirichlet([0.45, 0.45, 0.45], size=160)
    pts = np.array([bary(d) for d in draws])
    ax.scatter(pts[:, 0], pts[:, 1], s=8, color=c, alpha=0.45, zorder=3)
    ax.text(0.5, 0.015, r"$\theta \sim \mathrm{Dirichlet}(\alpha)$,  $\alpha<1$",
            ha="center", fontsize=8.5, color="#0f172a")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("LDA — Dirichlet simplex", fontsize=10.5, color=c,
                 fontweight="bold")
    _clean(ax)


def panel_hdp(ax):
    c = ACCENT["HDP"]
    # Stick-breaking: a unit stick repeatedly broken; bar lengths beta_k.
    betas = [0.40, 0.26, 0.16, 0.09, 0.05, 0.025, 0.013]  # schematic GEM draw
    remaining = 1.0
    y0 = 0.86
    h = 0.085
    x_left = 0.10
    full = 0.80  # drawing width of the full stick
    for k, b in enumerate(betas):
        w = b * full
        ax.barh(y0 - k * (h + 0.018), w, height=h, left=x_left,
                color=c, alpha=0.85 - 0.07 * k, edgecolor="#064e3b",
                linewidth=0.6, zorder=3)
        ax.text(x_left + w + 0.015, y0 - k * (h + 0.018),
                rf"$\beta_{{{k+1}}}$", va="center", fontsize=8, color="#0f172a")
        remaining -= b
    # the ever-shrinking tail (countably infinite truncation)
    ax.text(x_left, y0 - len(betas) * (h + 0.018) + 0.01,
            r"$\cdots$  (truncated at $T$)", fontsize=9, color="#475569")
    ax.annotate("", xy=(x_left + full, 0.96), xytext=(x_left, 0.96),
                arrowprops=dict(arrowstyle="<->", color="#475569", lw=1.0))
    ax.text(x_left + full / 2, 0.985, "unit stick", ha="center",
            fontsize=8, color="#475569")
    ax.text(0.5, 0.02,
            r"$\beta_k = v_k\!\prod_{j<k}(1-v_j)$,  $v_k\!\sim\!\mathrm{Beta}(1,\gamma)$",
            ha="center", fontsize=8.5, color="#0f172a")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_title("HDP — stick-breaking (GEM)", fontsize=10.5, color=c,
                 fontweight="bold")
    _clean(ax)


def panel_prodlda(ax):
    c = ACCENT["ProdLDA"]
    # logistic-normal: a Gaussian blob in the softmax pre-image, then warped.
    # Left: the Gaussian cloud in eta-space; right arrow -> simplex.
    mean = np.array([0.40, 0.55])
    cov = np.array([[0.012, 0.007], [0.007, 0.010]])
    cloud = RNG.multivariate_normal(mean, cov, size=220)
    ax.scatter(cloud[:, 0], cloud[:, 1], s=7, color=c, alpha=0.4, zorder=2)
    # 1-sigma ellipse
    vals, vecs = np.linalg.eigh(cov)
    ang = np.degrees(np.arctan2(*vecs[:, 1][::-1]))
    from matplotlib.patches import Ellipse
    for nsig, a in ((1, 0.9), (2, 0.45)):
        ax.add_patch(Ellipse(mean, 2 * nsig * np.sqrt(vals[1]),
                             2 * nsig * np.sqrt(vals[0]), angle=ang,
                             fill=False, edgecolor=c, linewidth=1.3,
                             alpha=a, zorder=3))
    ax.scatter(*mean, marker="x", s=55, color="#7c2d12", zorder=4, linewidth=2)
    ax.text(mean[0], mean[1] + 0.18, r"$\mu$", ha="center", fontsize=10,
            color="#7c2d12")
    ax.text(0.40, 0.06,
            r"$\eta\sim\mathcal{N}(\mu,\Sigma)$,  $\theta=\mathrm{softmax}(\eta)$",
            ha="center", fontsize=8.5, color="#0f172a")
    # softmax warp arrow to a mini simplex on the right
    arr = FancyArrowPatch((0.70, 0.55), (0.85, 0.55),
                          arrowstyle="-|>", mutation_scale=14,
                          color="#475569", lw=1.4)
    ax.add_patch(arr)
    ax.text(0.775, 0.60, "softmax", ha="center", fontsize=7.5, color="#475569")
    tri = np.array([[0.93, 0.78], [0.80, 0.30], [1.04, 0.30]])
    ax.add_patch(Polygon(tri, closed=True, facecolor="#fef3c7",
                         edgecolor=c, linewidth=1.2, zorder=3))
    ax.set_xlim(0.05, 1.08)
    ax.set_ylim(0, 1.0)
    ax.set_title("ProdLDA — logistic-normal", fontsize=10.5, color=c,
                 fontweight="bold")
    _clean(ax)


def panel_etm(ax):
    c = ACCENT["ETM"]
    # Embedding space: words (grey) + topic directions (arrows) on a unit circle.
    centre = np.array([0.5, 0.5])
    R = 0.40
    circ = plt.Circle(centre, R, fill=False, edgecolor="#cbd5e1",
                      linewidth=1.2, linestyle="--", zorder=1)
    ax.add_patch(circ)
    # scattered word embeddings
    n = 110
    rad = R * np.sqrt(RNG.uniform(0, 1, n))
    ang = RNG.uniform(0, 2 * np.pi, n)
    wx = centre[0] + rad * np.cos(ang)
    wy = centre[1] + rad * np.sin(ang)
    ax.scatter(wx, wy, s=9, color="#94a3b8", alpha=0.55, zorder=2)
    # topic embedding directions (alpha_k), as arrows from centre
    topic_ang = np.array([20, 95, 160, 250, 320]) * np.pi / 180.0
    for k, a in enumerate(topic_ang):
        tx = centre[0] + R * np.cos(a)
        ty = centre[1] + R * np.sin(a)
        arr = FancyArrowPatch(centre, (tx, ty), arrowstyle="-|>",
                              mutation_scale=12, color=c, lw=1.8, zorder=4)
        ax.add_patch(arr)
        ax.text(centre[0] + (R + 0.06) * np.cos(a),
                centre[1] + (R + 0.06) * np.sin(a),
                rf"$\alpha_{{{k+1}}}$", ha="center", va="center",
                fontsize=8, color="#0f172a")
    ax.text(0.5, 0.025,
            r"$\beta_{kv}\propto \exp(\alpha_k^\top\rho_v)$  (shared embedding)",
            ha="center", fontsize=8.5, color="#0f172a")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_title("ETM — embedding directions", fontsize=10.5, color=c,
                 fontweight="bold")
    _clean(ax)


def main() -> int:
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 9.0))
    panel_lda(axes[0, 0])
    panel_hdp(axes[0, 1])
    panel_prodlda(axes[1, 0])
    panel_etm(axes[1, 1])

    fig.suptitle(
        "Four backbone priors impose four different geometries on $\\theta$\n"
        "Same vocabulary, different generative assumption $\\Rightarrow$ "
        "recipe re-ranking (the P4 mechanism)",
        fontsize=12.5, y=0.985,
    )
    fig.text(
        0.012, 0.006,
        "Schematic only — no measured quantities. Shapes drawn from the "
        "published priors: Dirichlet (Blei+ 2003), HDP/GEM stick-breaking "
        "(Teh+ 2006), ProdLDA logistic-normal (Srivastava & Sutton 2017), "
        "ETM embeddings (Dieng+ 2020). Fixed RNG seed for the schematic clouds.",
        fontsize=7.0, color="#475569", ha="left",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = OUT_DIR / f"p4-prior-geometry.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
