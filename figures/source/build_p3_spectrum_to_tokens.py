"""P3 methods schematic — how ONE pixel spectrum becomes tokens.

A 4-panel "spectrum -> token bag" figure that makes the wordification
abstraction concrete. The left of every panel shows the SAME real
labelled pixel spectrum from Indian Pines (a Soybean-notill pixel,
200 bands, 400-2500 nm). An arrow points to the token bag that each of
four representative recipes produces from that one spectrum:

  V1  band-frequency        token = band id, count = quantised intensity
                            (one emission per band; weight = bin value)
  V8  NFINDR endmember      NFINDR(K) + NNLS unmix -> K abundance
       fractions             fractions, each quantised into a bin
  V12 GMM responsibilities  a 1-D GMM(Q) over intensities; every band's
                            value is assigned a component g -> (band,g)
  V20 MI-weighted bands     V1 (band,bin) joints, but each band emits
                            round(MI_b/maxMI * 8) copies; low-MI bands
                            fall silent.

The four recipes are intentionally one-per-family (pure-spectral,
chemistry-aware, learnt-codebook, label-aware) so the panel doubles as
a tour of the P3 design axes.

Data provenance — everything here is computed live from authoritative
derived artifacts, no hand-typed numbers:
  - the pixel spectrum + its V1 quantised levels come from
    data/derived/real/real_samples.json (example_documents).
  - the V8 endmembers are the real NFINDR fit from
    data/derived/endmember_baseline/indian-pines-corrected.json,
    unmixed with the same scipy NNLS + sum-to-one penalty the pipeline
    uses (build_wordifications_v6plus.py).
  - V12 fits sklearn GaussianMixture(Q) on this pixel's intensities,
    matching wordify_v12_gmm.
  - V20 computes per-band MI against the 16 Indian-Pines class means
    (a faithful stand-in for the corpus-level mutual_info_classif the
    builder runs over the full stratified sample) and re-weights V1
    exactly as build_wordifications_v20.py does.

If the real artifacts cannot be loaded the panel falls back to a clearly
labelled 'illustrative' synthetic spectrum.

Output: figures/p3-spectrum-to-tokens.{pdf,png}  (png at 180 dpi)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
HSI_ROOT = REPO_ROOT.parent / "CAOS_LDA_HSI"
REAL_SAMPLES = HSI_ROOT / "data" / "derived" / "real" / "real_samples.json"
ENDMEMBER_JSON = (
    HSI_ROOT / "data" / "derived" / "endmember_baseline"
    / "indian-pines-corrected.json"
)
# Authoritative V20 doc-term matrix — its per-band copy multiplicity is the
# real corpus-level MI weighting (mutual_info_classif over the full
# stratified sample) baked in by build_wordifications_v20.py.
V20_DOCTERM = (
    HSI_ROOT / "data" / "local" / "wordifications" / "V20" / "uniform_Q8"
    / "indian-pines-corrected" / "doc_term.npz"
)
OUT_DIR = REPO_ROOT / "figures"

SCENE_ID = "indian-pines-corrected"
PIXEL_CLASS = "Soybean-notill"   # a mixed agricultural pixel -> non-trivial bags
Q = 8                            # quantisation levels, matches the headline grid
MAX_COPIES = 8                   # V20 max copies per band (build_wordifications_v20)

# Palette (per recipe family, aligned with wordification-taxonomy.py)
C_SPECTRUM = "#0f172a"
C_V1 = "#0ea5e9"    # pure spectral
C_V8 = "#10b981"    # chemistry-aware
C_V12 = "#a855f7"   # learnt codebook
C_V20 = "#9333ea"   # label-aware
C_GRID = "#e2e8f0"
C_ARROW = "#94a3b8"


# --------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------
def load_real_pixel() -> dict | None:
    """Return {wavelengths, spectrum01, class_name, quantized_levels,
    endmembers01 (K,B), class_means01 (C,B), illustrative=False} or None."""
    if not REAL_SAMPLES.exists():
        return None
    try:
        with REAL_SAMPLES.open() as h:
            payload = json.load(h)
        scene = next(s for s in payload["scenes"] if s["id"] == SCENE_ID)
        wl = np.asarray(scene["approximate_wavelengths_nm"], dtype=float)
        ex = next(
            e for e in scene["example_documents"]
            if e["class_name"] == PIXEL_CLASS
        )
        spec = np.asarray(ex["spectrum"], dtype=float)
        qlev = np.asarray(ex.get("quantized_levels", []), dtype=float)
        class_means = np.asarray(
            [c["mean_spectrum"] for c in scene["class_summaries"]], dtype=float
        )
        endmembers = None
        if ENDMEMBER_JSON.exists():
            with ENDMEMBER_JSON.open() as h:
                em = np.asarray(json.load(h)["nfindr_endmembers"], dtype=float)
            # per-endmember min-max to [0,1] (matches normalize01_per_row)
            lo = em.min(axis=1, keepdims=True)
            hi = em.max(axis=1, keepdims=True)
            endmembers = (em - lo) / np.maximum(hi - lo, 1e-12)
        # Real V20 per-band copy multiplicity (the baked-in MI weighting).
        v20_copies = None
        if V20_DOCTERM.exists():
            import scipy.sparse as sp
            mat = sp.load_npz(V20_DOCTERM)
            b_count = mat.shape[1] // Q
            # band b emits the same #copies for whichever bin it lands in;
            # take any document row and reduce over the Q bins per band.
            row0 = mat.getrow(0).toarray().ravel().reshape(b_count, Q)
            v20_copies = row0.max(axis=1).astype(int)
        return {
            "wavelengths": wl,
            "spectrum01": spec,
            "class_name": ex["class_name"],
            "quantized_levels": qlev,
            "endmembers01": endmembers,
            "class_means01": class_means,
            "v20_copies": v20_copies,
            "illustrative": False,
        }
    except Exception as exc:  # pragma: no cover - defensive
        print(f"  real load failed ({exc}); using illustrative spectrum", flush=True)
        return None


def synthetic_pixel() -> dict:
    """Clearly-labelled illustrative fallback (water + chlorophyll dips)."""
    wl = np.linspace(400.0, 2500.0, 200)
    rng = np.random.default_rng(7)
    base = 0.30 + 0.45 / (1.0 + np.exp(-(wl - 720.0) / 40.0))  # red edge
    base -= 0.18 * np.exp(-((wl - 680.0) / 30.0) ** 2)         # chlorophyll
    base -= 0.30 * np.exp(-((wl - 1450.0) / 60.0) ** 2)        # water
    base -= 0.28 * np.exp(-((wl - 1940.0) / 70.0) ** 2)        # water
    base += 0.02 * rng.standard_normal(wl.size)
    spec = (base - base.min()) / (base.max() - base.min())
    # fake but plausible endmembers
    k = 6
    ems = np.clip(
        spec[None, :] + 0.25 * rng.standard_normal((k, wl.size)), 0, 1
    )
    # synthetic MI-copy profile: a few discriminative bands, most muted
    rng2 = np.random.default_rng(11)
    mi = np.abs(np.sin(np.linspace(0, 6 * np.pi, wl.size))) * rng2.uniform(
        0.2, 1.0, wl.size)
    copies = np.round(mi / mi.max() * MAX_COPIES).astype(int)
    return {
        "wavelengths": wl,
        "spectrum01": spec,
        "class_name": "illustrative",
        "quantized_levels": np.clip(np.floor(spec * Q), 0, Q - 1),
        "endmembers01": ems,
        "class_means01": ems,
        "v20_copies": copies,
        "illustrative": True,
    }


# --------------------------------------------------------------------------
# tokenisations (faithful to the pipeline builders)
# --------------------------------------------------------------------------
def v1_tokens(spec01: np.ndarray) -> np.ndarray:
    """V1 band-frequency: per band, count = uniform bin id in [0, Q-1]."""
    return np.clip(np.floor(spec01 * Q), 0, Q - 1).astype(int)


def v8_abundances(spec01: np.ndarray, endmembers01: np.ndarray) -> np.ndarray:
    """V8 NFINDR + NNLS-with-sum-to-one unmix -> normalised abundance vector."""
    from scipy.optimize import nnls
    K, B = endmembers01.shape
    delta = 100.0  # SUM_TO_ONE_DELTA in build_wordifications_v6plus
    A = np.vstack([endmembers01.T, delta * np.ones((1, K))])
    b = np.append(spec01, delta)
    try:
        a, _ = nnls(A, b, maxiter=10 * (B + K + 1))
    except RuntimeError:
        a = np.clip(np.linalg.pinv(endmembers01.T) @ spec01, 0.0, None)
    s = a.sum()
    return a / s if s > 1e-12 else a


def v12_components(spec01: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """V12: fit a 1-D GMM(Q) on this pixel's intensities, return (per-band
    component id, sorted component means)."""
    from sklearn.mixture import GaussianMixture
    x = spec01.reshape(-1, 1)
    gmm = GaussianMixture(
        n_components=Q, covariance_type="diag", random_state=42, max_iter=80
    )
    gmm.fit(x)
    order = np.argsort(gmm.means_.ravel())
    inv = np.empty_like(order)
    inv[order] = np.arange(Q)
    comp = inv[gmm.predict(x)]
    return comp.astype(int), gmm.means_.ravel()[order]


def v20_weights(data: dict) -> np.ndarray:
    """V20 per-band MI weight in copies. Prefer the authoritative weighting
    extracted from the persisted V20 doc-term matrix (round(MI_b/maxMI × 8)
    over the full stratified corpus). Fall back to a corpus-mean MI estimate
    only if that artifact is unavailable."""
    real = data.get("v20_copies")
    if real is not None and real.size == data["spectrum01"].size:
        return real.astype(int)
    # fallback: corpus-mean MI over the class-mean population
    from sklearn.feature_selection import mutual_info_classif
    cm = data["class_means01"]
    C, B = cm.shape
    lo = cm.min(axis=1, keepdims=True)
    hi = cm.max(axis=1, keepdims=True)
    X = (cm - lo) / np.maximum(hi - lo, 1e-12)
    n_nb = max(1, min(3, C - 1))
    mi = mutual_info_classif(X, np.arange(C), random_state=42, n_neighbors=n_nb)
    mi_norm = mi / max(mi.max(), 1e-12)
    return np.round(mi_norm * MAX_COPIES).astype(int)


# --------------------------------------------------------------------------
# panel renderers
# --------------------------------------------------------------------------
def _band_to_nm(idx: int, wl: np.ndarray) -> int:
    return int(round(wl[idx]))


def draw_token_chip(ax, x, y, w, h, text, colour, count=None, alpha=0.9, fs=7.0):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012",
        facecolor=colour, edgecolor="white", linewidth=0.8, alpha=alpha,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color="white", fontweight="bold", family="monospace")
    if count is not None:
        ax.text(x + w - 0.004, y + h - 0.004, f"×{count}",
                ha="right", va="top", fontsize=fs - 1.2,
                color="white", alpha=0.85)


def panel_spectrum(ax, data, recipe_colour, marks=None, title=""):
    """Left mini-spectrum, optionally annotated with marks (list of band idx)."""
    wl = data["wavelengths"]
    spec = data["spectrum01"]
    ax.plot(wl, spec, color=C_SPECTRUM, linewidth=1.3, zorder=3)
    ax.fill_between(wl, 0, spec, color=recipe_colour, alpha=0.10, zorder=1)
    ax.set_xlim(wl[0], wl[-1])
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("wavelength (nm)", fontsize=7.2)
    ax.set_ylabel("norm. reflectance", fontsize=7.2)
    ax.tick_params(labelsize=6.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if marks is not None:
        for b in marks:
            ax.plot([wl[b]], [spec[b]], "o", ms=3.2,
                    color=recipe_colour, zorder=5)
    if title:
        ax.set_title(title, fontsize=8.0, color=recipe_colour,
                     fontweight="bold", pad=3)


def render(data: dict) -> None:
    wl = data["wavelengths"]
    spec = data["spectrum01"]
    B = spec.size

    # --- compute the four tokenisations ---
    v1 = v1_tokens(spec)
    v8 = v8_abundances(spec, data["endmembers01"])
    v12_comp, v12_means = v12_components(spec)
    v20w = v20_weights(data)
    # v20 token = (band, bin) with copies = v20w; needs same V1 bins
    v1_bins = v1  # identical quantiser

    fig = plt.figure(figsize=(15.5, 9.2))
    gs = GridSpec(
        4, 2, width_ratios=[1.0, 1.95], height_ratios=[1, 1, 1, 1],
        hspace=0.62, wspace=0.16,
        left=0.055, right=0.985, top=0.885, bottom=0.085,
    )

    # ---- title block ----
    illus = data["illustrative"]
    src = (
        "illustrative synthetic spectrum"
        if illus else
        f"real {data['class_name']} pixel — Indian Pines (200 bands, 400-2500 nm)"
    )
    fig.text(0.5, 0.965,
             "One spectrum, four token bags — the wordification step of LDA-on-HSI",
             ha="center", fontsize=15.5, fontweight="bold", color="#0f172a")
    fig.text(0.5, 0.93,
             f"The identical pixel spectrum (left of each row) is turned into a "
             f"bag-of-tokens by four recipes, one per design family.   Source: {src}.",
             ha="center", fontsize=9.5, color="#475569", style="italic")
    if illus:
        fig.text(0.5, 0.905, "ILLUSTRATIVE — real derived artifacts were not loadable",
                 ha="center", fontsize=9, color="#b91c1c", fontweight="bold")

    # ============================ V1 ============================
    axL = fig.add_subplot(gs[0, 0])
    # mark a handful of representative bands
    mark_idx = np.linspace(8, B - 8, 6).astype(int)
    panel_spectrum(axL, data, C_V1, marks=mark_idx,
                   title="V1 · band-frequency  (pure spectral)")
    axR = fig.add_subplot(gs[0, 1]); axR.axis("off")
    axR.set_xlim(0, 1); axR.set_ylim(0, 1)
    axR.text(0.0, 0.92,
             "token = band id   ·   count = quantised intensity (0..7)   ·   "
             f"vocab = B = {B} bands",
             fontsize=8.2, color="#334155")
    # show 6 band chips with their bin counts
    n = len(mark_idx)
    cw, ch, gap = 0.135, 0.30, 0.018
    x0 = 0.02
    for i, b in enumerate(mark_idx):
        x = x0 + i * (cw + gap)
        draw_token_chip(axR, x, 0.40, cw, ch,
                        f"b{b:03d}\n{_band_to_nm(b, wl)}nm", C_V1,
                        count=int(v1[b]), fs=6.8)
    axR.annotate("", xy=(x0 - 0.006, 0.55), xytext=(-0.085, 0.55),
                 xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=1.8))
    axR.text(0.02, 0.18,
             "Every band fires once; its weight is the bin height. "
             "Canonical Procemin-2022 baseline — the reference all other "
             "recipes are scored against.",
             fontsize=7.4, color="#64748b", style="italic")

    # ============================ V8 ============================
    axL = fig.add_subplot(gs[1, 0])
    panel_spectrum(axL, data, C_V8,
                   title="V8 · NFINDR endmember fractions  (chemistry-aware)")
    axR = fig.add_subplot(gs[1, 1]); axR.axis("off")
    axR.set_xlim(0, 1); axR.set_ylim(0, 1)
    K = v8.size
    axR.text(0.0, 0.92,
             f"NFINDR extracts K={K} endmembers; NNLS unmix -> abundance "
             "fractions; each fraction quantised.   token = endmember id",
             fontsize=8.2, color="#334155")
    # tiny abundance bar strip, then chips for the non-trivial endmembers
    order = np.argsort(v8)[::-1]
    keep = [int(k) for k in order if v8[k] > 0.02][:6]
    bw = 0.92 / K
    for k in range(K):
        h = 0.26 * (v8[k] / max(v8.max(), 1e-9))
        axR.add_patch(mpatches.Rectangle(
            (0.04 + k * bw, 0.56), bw * 0.8, max(h, 0.004),
            facecolor=C_V8, edgecolor="white", linewidth=0.5,
            alpha=0.55 + 0.45 * (v8[k] > 0.02)))
    axR.text(0.04, 0.84, "abundance simplex (sum=1)", fontsize=6.8,
             color="#64748b")
    cw, ch, gap = 0.135, 0.20, 0.018
    for i, k in enumerate(keep):
        x = 0.02 + i * (cw + gap)
        binq = int(np.clip(np.floor(v8[k] / max(v8.max(), 1e-9) * Q), 0, Q - 1))
        draw_token_chip(axR, x, 0.20, cw, ch,
                        f"em{k:02d}_q{binq:02d}", C_V8, fs=6.6)
    axR.text(0.02, 0.03,
             f"Only {len(keep)} of {K} endmembers carry weight in this pixel — "
             "the bag is short and chemistry-anchored.",
             fontsize=7.4, color="#64748b", style="italic")

    # ============================ V12 ===========================
    axL = fig.add_subplot(gs[2, 0])
    panel_spectrum(axL, data, C_V12,
                   title="V12 · GMM responsibilities  (learnt codebook)")
    axR = fig.add_subplot(gs[2, 1]); axR.axis("off")
    axR.set_xlim(0, 1); axR.set_ylim(0, 1)
    axR.text(0.0, 0.92,
             f"a 1-D GMM(Q={Q}) is fit on the intensities; each band's value is "
             "assigned a component g.   token = (band, component) joint",
             fontsize=8.2, color="#334155")
    # histogram of component assignments
    comp_counts = np.bincount(v12_comp, minlength=Q)
    bw = 0.92 / Q
    for g in range(Q):
        h = 0.26 * comp_counts[g] / max(comp_counts.max(), 1)
        axR.add_patch(mpatches.Rectangle(
            (0.04 + g * bw, 0.56), bw * 0.8, max(h, 0.004),
            facecolor=C_V12, edgecolor="white", linewidth=0.5, alpha=0.85))
        axR.text(0.04 + g * bw + bw * 0.4, 0.535, f"g{g}",
                 ha="center", fontsize=6.0, color="#64748b")
    axR.text(0.04, 0.84, f"bands per GMM component (B={B} total)",
             fontsize=6.8, color="#64748b")
    # a few representative (band, component) chips
    cw, ch, gap = 0.135, 0.20, 0.018
    samp = np.linspace(10, B - 10, 6).astype(int)
    for i, b in enumerate(samp):
        x = 0.02 + i * (cw + gap)
        draw_token_chip(axR, x, 0.20, cw, ch,
                        f"b{b:03d}_g{int(v12_comp[b])}", C_V12, fs=6.6)
    axR.text(0.02, 0.03,
             "Bins are data-driven (EM-fit means) rather than equi-spaced — "
             "this is V12's only change versus V3's fixed alphabet.",
             fontsize=7.4, color="#64748b", style="italic")

    # ============================ V20 ===========================
    axL = fig.add_subplot(gs[3, 0])
    # mark the high-MI bands on the spectrum
    top_mi = np.argsort(v20w)[::-1][:6]
    panel_spectrum(axL, data, C_V20, marks=list(top_mi),
                   title="V20 · MI-weighted bands  (label-aware)")
    axR = fig.add_subplot(gs[3, 1]); axR.axis("off")
    axR.set_xlim(0, 1); axR.set_ylim(0, 1)
    n_zero = int((v20w == 0).sum())
    axR.text(0.0, 0.92,
             "V1 (band,bin) joints, but band b emits round(MI_b/maxMI × 8) "
             f"copies.   {n_zero} of {B} bands fall silent (MI≈0).",
             fontsize=8.2, color="#334155")
    # MI weight profile across bands
    axw = axR.inset_axes([0.04, 0.60, 0.92, 0.28])
    axw.bar(np.arange(B), v20w, width=1.0, color=C_V20, alpha=0.75)
    axw.set_xlim(0, B); axw.set_ylim(0, MAX_COPIES)
    axw.set_ylabel("copies", fontsize=6.2); axw.tick_params(labelsize=5.6)
    axw.set_xlabel("band index (per-band MI copy multiplicity, 0..8)",
                   fontsize=6.2, labelpad=1.5)
    for s in ("top", "right"):
        axw.spines[s].set_visible(False)
    # chips for the top-MI bands, with their copy multiplicity
    cw, ch, gap = 0.135, 0.18, 0.018
    for i, b in enumerate(top_mi):
        x = 0.02 + i * (cw + gap)
        draw_token_chip(axR, x, 0.145, cw, ch,
                        f"miw_b{b:03d}_q{int(v1_bins[b]):02d}", C_V20,
                        count=int(v20w[b]), fs=6.0)
    axR.text(0.02, 0.03,
             "Discriminative bands dominate the bag; uninformative ones vanish. "
             "The only label-aware recipe in the sweep — P3's headline winner.",
             fontsize=7.4, color="#64748b", style="italic")

    # footer
    fig.text(
        0.5, 0.022,
        "All four bags come from the same pixel. V1/V20 keep the band grid; "
        "V8 collapses to a chemistry simplex; V12 swaps equi-spaced bins for "
        "EM-learnt ones; V20 re-weights by label mutual information. "
        "Tokens & weights computed live from the Indian-Pines derived artifacts "
        "(real_samples.json + NFINDR endmember_baseline).",
        ha="center", fontsize=7.6, color="#475569",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = OUT_DIR / f"p3-spectrum-to-tokens.{ext}"
        fig.savefig(out, bbox_inches="tight", dpi=180 if ext == "png" else None)
        print(f"  wrote {out}", flush=True)
    plt.close(fig)


def main() -> int:
    data = load_real_pixel()
    if data is None:
        data = synthetic_pixel()
    print(
        f"  pixel: {data['class_name']} | B={data['spectrum01'].size} | "
        f"endmembers={'yes' if data['endmembers01'] is not None else 'no'} | "
        f"illustrative={data['illustrative']}",
        flush=True,
    )
    render(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
