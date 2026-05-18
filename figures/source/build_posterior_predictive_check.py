"""Posterior predictive check for the F-1 hierarchical Bayesian model.

Closes one item from issue #7 — Suppl G claims residuals on the F-1
likelihood `y ~ N(method_effect + scene_effect, sigma^2)` are
"not visibly non-Gaussian" without an actual PPC figure. This
builder produces the missing figure.

Method:
1. Gather per-(method, scene, fold) accuracy values from each scene's
   `topic_routed_classifier/<scene>.json` (5 methods × 6 scenes × 5
   folds = 150 observations).
2. Fit a fixed-effects OLS regression
   y ~ C(method) + C(scene)
   to recover method + scene main effects with the rest of the
   variance assigned to residuals (matches the hierarchical-model
   likelihood under the standard noninformative limit).
3. Plot two panels:
   - Histogram of residuals with N(0, sigma_hat) overlay
   - Q-Q plot of residuals vs standard normal
4. Report Shapiro-Wilk p-value and Kolmogorov-Smirnov p-value
   against a fitted normal as text annotations on the figure.

Saves SVG + PDF to `figures/`. Embedded into Suppl G as a new
figure under the multiplicity-correction discussion.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_DATA = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
OUT_DIR = REPO_ROOT / "figures"

SCENES = [
    "indian-pines-corrected",
    "salinas-corrected",
    "salinas-a-corrected",
    "pavia-university",
    "kennedy-space-center",
    "botswana",
]
METHODS = [
    "raw_logistic",
    "theta_logistic",
    "pca_12_logistic",
    "topic_routed_soft",
    "topic_routed_hard",
]


def gather_observations() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns y, method_idx, scene_idx as 1D arrays (length 150)."""
    y = []
    m_idx = []
    s_idx = []
    for si, scene in enumerate(SCENES):
        path = CODE_DATA / "topic_routed_classifier" / f"{scene}.json"
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        payload = json.loads(path.read_text())
        for mi, method in enumerate(METHODS):
            if method not in payload["method_metrics"]:
                continue
            folds = payload["method_metrics"][method]["accuracy"]["per_fold"]
            for v in folds:
                y.append(v)
                m_idx.append(mi)
                s_idx.append(si)
    return np.array(y), np.array(m_idx), np.array(s_idx)


def fit_fixed_effects(y: np.ndarray, m_idx: np.ndarray, s_idx: np.ndarray
                       ) -> tuple[np.ndarray, float]:
    """OLS on dummy-coded method + scene; returns residuals + sigma_hat."""
    n = y.shape[0]
    n_methods = len(METHODS)
    n_scenes = len(SCENES)
    # Design matrix: 1 intercept + (n_methods-1) method dummies + (n_scenes-1) scene dummies.
    X = np.zeros((n, 1 + (n_methods - 1) + (n_scenes - 1)))
    X[:, 0] = 1.0
    for i in range(n):
        if m_idx[i] > 0:
            X[i, m_idx[i]] = 1.0
        if s_idx[i] > 0:
            X[i, n_methods + s_idx[i] - 1] = 1.0
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ beta
    residuals = y - fitted
    sigma_hat = float(np.std(residuals, ddof=X.shape[1]))
    return residuals, sigma_hat


def render(residuals: np.ndarray, sigma_hat: float) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    # Panel 1: histogram + N(0, sigma_hat) overlay
    ax = axes[0]
    n_bins = 20
    ax.hist(
        residuals,
        bins=n_bins,
        density=True,
        color="#88CCEE",
        edgecolor="#444444",
        alpha=0.78,
        label=f"Empirical residuals (n={residuals.size})",
    )
    xs = np.linspace(residuals.min(), residuals.max(), 400)
    pdf = stats.norm.pdf(xs, loc=0.0, scale=sigma_hat)
    ax.plot(xs, pdf, color="#CC6677", lw=2.2,
            label=fr"$\mathcal{{N}}(0,\,\hat\sigma^2)$, $\hat\sigma={sigma_hat:.4f}$")
    ax.axvline(0.0, color="black", lw=0.6, ls="--", alpha=0.5)
    ax.set_xlabel("Residual (accuracy units)")
    ax.set_ylabel("Density")
    ax.set_title("Residual distribution vs Normal")
    ax.legend(loc="upper right", fontsize=9)

    # Panel 2: Q-Q plot against standard normal
    ax = axes[1]
    (osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist="norm")
    ax.scatter(osm, osr, s=22, color="#88CCEE", edgecolor="#444444", lw=0.5,
               alpha=0.9, zorder=2)
    line_xs = np.array([osm.min(), osm.max()])
    ax.plot(line_xs, slope * line_xs + intercept, color="#CC6677", lw=2.2,
            zorder=1, label=f"OLS fit (r={r:.3f})")
    ax.set_xlabel("Standard-normal quantile")
    ax.set_ylabel("Empirical residual quantile")
    ax.set_title("Q-Q vs standard normal")
    ax.legend(loc="upper left", fontsize=9)

    # Annotated test statistics
    sw_stat, sw_p = stats.shapiro(residuals)
    ks_stat, ks_p = stats.kstest(
        residuals / sigma_hat if sigma_hat > 0 else residuals,
        "norm",
    )
    txt = (
        f"Shapiro-Wilk: W={sw_stat:.3f}, p={sw_p:.3f}\n"
        f"KS vs $\\mathcal{{N}}(0,\\,\\hat\\sigma^2)$: D={ks_stat:.3f}, p={ks_p:.3f}\n"
        f"Skewness: {float(stats.skew(residuals)):+.3f}\n"
        f"Excess kurtosis: {float(stats.kurtosis(residuals)):+.3f}"
    )
    fig.text(0.5, -0.04, txt, ha="center", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#F7F7F7",
                       edgecolor="#888888"))

    fig.suptitle(
        "F-1 posterior predictive check: residuals vs Normal(0, $\\hat\\sigma^2$)",
        fontsize=12, y=1.02,
    )
    plt.tight_layout()
    out_svg = OUT_DIR / "posterior-predictive-check.svg"
    out_pdf = OUT_DIR / "posterior-predictive-check.pdf"
    fig.savefig(out_svg, format="svg", bbox_inches="tight")
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    print(f"wrote {out_svg.relative_to(REPO_ROOT)}")
    print(f"wrote {out_pdf.relative_to(REPO_ROOT)}")
    print()
    print(f"Shapiro-Wilk W={sw_stat:.4f}, p={sw_p:.4f}")
    print(f"KS vs N(0, hat_sigma): D={ks_stat:.4f}, p={ks_p:.4f}")
    print(f"hat_sigma = {sigma_hat:.4f}")
    print(f"skew = {float(stats.skew(residuals)):.4f}, "
          f"excess kurtosis = {float(stats.kurtosis(residuals)):.4f}")


def main() -> None:
    y, m_idx, s_idx = gather_observations()
    print(f"Loaded {y.size} observations ({len(METHODS)} methods x "
          f"{len(SCENES)} scenes x ~5 folds)")
    residuals, sigma_hat = fit_fixed_effects(y, m_idx, s_idx)
    render(residuals, sigma_hat)


if __name__ == "__main__":
    main()
