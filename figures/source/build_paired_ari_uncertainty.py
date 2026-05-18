"""Permutation null + bootstrap CI on paired ARI per (scene, mask).

Closes one item from issue #7 ("Permutation null / bootstrap CI on
paired ARI — headline 0.766 vs 0.01 has no error bars").

Reads:
- Per-scene canonical dominant-topic map (uint8) from
  `topic_to_data/<scene>_dominant_topic_map.bin`.
- Per-(scene, mask) band-mask dominant-topic map (uint8) from
  `band_masks/<scene>/<mask>/dominant_topic_map.bin`.
- The list of 24 (scene, mask) tuples from
  `band_masks/canonical_comparison.json`.

For each (scene, mask) pair:
1. Restrict to pixels labelled in BOTH maps (= not == sentinel 255).
2. Compute the observed paired ARI on those D paired pixels.
3. **Permutation null**: shuffle the masked-map labels uniformly
   1000 times, compute ARI each time. p-value = fraction of
   permuted ARIs >= observed (one-sided, since the null is 0).
4. **Bootstrap CI**: resample paired pixels with replacement 1000
   times, compute ARI each time. Report mean + 2.5% / 97.5%
   percentile CI.

Writes a LaTeX longtable to
`supplementary/journal/paired_ari_uncertainty.tex` referencing
the 24 (scene, mask) tuples, with permutation p-value and 95% CI
per row. Embedded from Suppl F's F-5 (paired ARI per scene-mask).

Sampling-budget caveat: 1000 permutations + 1000 bootstraps per
tuple = 48,000 ARI computations. On a 2812-pixel scene this is
~30 s wall-clock; on Salinas (10366 pixels) ~2 min per tuple. We
cap pixels at 10000 per tuple via random subsample with a fixed
seed for reproducibility — the resulting permutation null is
identical in distribution to the full-population null on this
sample size.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import adjusted_rand_score

REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_DATA = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived"
COMPARISON_JSON = CODE_DATA / "band_masks" / "canonical_comparison.json"
OUT_TEX = REPO_ROOT / "supplementary" / "journal" / "paired_ari_uncertainty.tex"

N_PERMUTATIONS = 1000
N_BOOTSTRAPS = 1000
MAX_PAIRED_PIXELS = 10_000
SENTINEL = 255
RNG = np.random.default_rng(42)


def load_canonical_map(scene_id: str) -> np.ndarray:
    p = CODE_DATA / "topic_to_data" / f"{scene_id}_dominant_topic_map.bin"
    if not p.exists():
        raise FileNotFoundError(p)
    return np.fromfile(p, dtype=np.uint8)


def load_masked_map(scene_id: str, mask_id: str) -> np.ndarray:
    p = CODE_DATA / "band_masks" / scene_id / mask_id / "dominant_topic_map.bin"
    if not p.exists():
        raise FileNotFoundError(p)
    return np.fromfile(p, dtype=np.uint8)


def compute_row(entry: dict) -> dict:
    if entry.get("skipped"):
        return {
            "scene_id": entry["scene_id"],
            "mask_id": entry["mask_id"],
            "skipped": True,
            "reason": entry.get("reason", "skipped"),
        }
    scene_id = entry["scene_id"]
    mask_id = entry["mask_id"]
    try:
        canon = load_canonical_map(scene_id)
        masked = load_masked_map(scene_id, mask_id)
    except FileNotFoundError as exc:
        return {
            "scene_id": scene_id,
            "mask_id": mask_id,
            "skipped": True,
            "reason": f"missing file: {exc}",
        }

    if canon.shape != masked.shape:
        return {
            "scene_id": scene_id,
            "mask_id": mask_id,
            "skipped": True,
            "reason": f"shape mismatch: {canon.shape} vs {masked.shape}",
        }

    paired = (canon != SENTINEL) & (masked != SENTINEL)
    n_paired = int(paired.sum())
    if n_paired == 0:
        return {
            "scene_id": scene_id,
            "mask_id": mask_id,
            "skipped": True,
            "reason": "zero paired pixels",
        }

    a = canon[paired].astype(np.int32)
    b = masked[paired].astype(np.int32)

    # Subsample to bound runtime
    if a.shape[0] > MAX_PAIRED_PIXELS:
        idx = RNG.choice(a.shape[0], MAX_PAIRED_PIXELS, replace=False)
        a = a[idx]
        b = b[idx]

    observed_ari = float(adjusted_rand_score(a, b))

    # Permutation null
    null_aris = np.empty(N_PERMUTATIONS, dtype=np.float64)
    b_perm = b.copy()
    for i in range(N_PERMUTATIONS):
        RNG.shuffle(b_perm)
        null_aris[i] = adjusted_rand_score(a, b_perm)
    p_value = float((null_aris >= observed_ari).mean())

    # Bootstrap CI
    boot_aris = np.empty(N_BOOTSTRAPS, dtype=np.float64)
    n = a.shape[0]
    for i in range(N_BOOTSTRAPS):
        idx = RNG.integers(0, n, n)
        boot_aris[i] = adjusted_rand_score(a[idx], b[idx])
    ci_low = float(np.percentile(boot_aris, 2.5))
    ci_high = float(np.percentile(boot_aris, 97.5))
    boot_mean = float(boot_aris.mean())

    return {
        "scene_id": scene_id,
        "mask_id": mask_id,
        "n_paired_pixels": int(a.shape[0]),
        "observed_ari": observed_ari,
        "permutation_p_value": p_value,
        "bootstrap_mean_ari": boot_mean,
        "bootstrap_ci_2_5": ci_low,
        "bootstrap_ci_97_5": ci_high,
        "null_mean_ari": float(null_aris.mean()),
        "null_std_ari": float(null_aris.std()),
    }


def render_latex(rows: list[dict]) -> str:
    SCENE_PRETTY = {
        "indian-pines-corrected": "Indian Pines",
        "salinas-corrected": "Salinas",
        "salinas-a-corrected": "Salinas-A",
        "pavia-university": "Pavia U",
        "kennedy-space-center": "KSC",
        "botswana": "Botswana",
    }
    MASK_PRETTY = {
        "vnir": "VNIR",
        "swir": "SWIR",
        "no_water": "no-water",
        "top_50_fisher": "top-50 Fisher",
    }
    lines = [
        "% Paired-ARI permutation null + bootstrap CI per (scene, mask).",
        "% Generated by figures/source/build_paired_ari_uncertainty.py.",
        "\\begin{tabular}{llrrrrr}",
        "\\toprule",
        "Scene & Mask & $D_{\\text{paired}}$ & Observed ARI & "
        "Bootstrap 95\\% CI & Perm. $p$ & Null $\\mu \\pm \\sigma$ \\\\",
        "\\midrule",
    ]
    for r in rows:
        scene = SCENE_PRETTY.get(r["scene_id"], r["scene_id"])
        mask = MASK_PRETTY.get(r["mask_id"], r["mask_id"])
        if r.get("skipped"):
            lines.append(
                f"{scene} & {mask} & \\multicolumn{{5}}{{l}}{{"
                f"(skipped: {r.get('reason', '').replace('_', '-')})}} \\\\"
            )
            continue
        p_str = f"{r['permutation_p_value']:.3f}" if r['permutation_p_value'] > 0 else f"$<$ {1/N_PERMUTATIONS:.3f}"
        lines.append(
            f"{scene} & {mask} & {r['n_paired_pixels']} & "
            f"{r['observed_ari']:.3f} & "
            f"[{r['bootstrap_ci_2_5']:.3f}, {r['bootstrap_ci_97_5']:.3f}] & "
            f"{p_str} & "
            f"{r['null_mean_ari']:+.3f} $\\pm$ {r['null_std_ari']:.3f} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def main() -> None:
    payload = json.loads(COMPARISON_JSON.read_text())
    entries = payload["entries"]
    print(f"Processing {len(entries)} (scene, mask) tuples; "
          f"N_perm={N_PERMUTATIONS}, N_boot={N_BOOTSTRAPS}, "
          f"D_max={MAX_PAIRED_PIXELS}")

    rows = []
    for i, entry in enumerate(entries):
        print(f"[{i+1}/{len(entries)}] {entry['scene_id']} / {entry['mask_id']}",
              flush=True)
        rows.append(compute_row(entry))
        r = rows[-1]
        if not r.get("skipped"):
            print(f"    observed={r['observed_ari']:.3f}, "
                  f"p={r['permutation_p_value']:.3f}, "
                  f"95% CI=[{r['bootstrap_ci_2_5']:.3f}, {r['bootstrap_ci_97_5']:.3f}]")

    OUT_TEX.write_text(render_latex(rows))
    print(f"\nwrote {OUT_TEX.relative_to(REPO_ROOT)}")

    # Also dump as JSON for reproducibility / sidecar consumption.
    out_json = OUT_TEX.with_suffix(".json")
    out_json.write_text(json.dumps({
        "n_permutations": N_PERMUTATIONS,
        "n_bootstraps": N_BOOTSTRAPS,
        "max_paired_pixels": MAX_PAIRED_PIXELS,
        "rng_seed": 42,
        "rows": rows,
    }, indent=2))
    print(f"wrote {out_json.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
