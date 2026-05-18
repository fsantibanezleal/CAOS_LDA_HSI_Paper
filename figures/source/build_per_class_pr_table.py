"""Per-class precision / recall table for the canonical topic-routed-hard
classifier across the 6 labelled scenes.

Closes one item from issue #7 ("Per-class precision/recall table
missing for labelled scenes").

Construction:

1. For each scene, read `topic_to_data/<scene>.json` from the code
   repo. That file exposes
   - `docs_per_topic_dominant[k]` = N_k, the number of pixels with
     argmax theta_k,
   - `p_label_given_topic_dominant[k][i]` = {label_id, name, count, p}
     for each label i, given the N_k pixels assigned to topic k.
2. The joint pixel count C[k, l] = count from
   `p_label_given_topic_dominant`.
3. Topic-routed-hard predicted class for topic k is
   k* = argmax_l C[k, l].
4. Per-class metrics:
     TP_l       = sum_{k : k* = l} C[k, l]
     predicted_l = sum_{k : k* = l} N_k
     actual_l   = sum_k C[k, l]
   precision_l = TP_l / predicted_l (0 if predicted_l == 0)
   recall_l    = TP_l / actual_l    (always > 0 by construction)
   f1_l        = 2 * precision_l * recall_l / (precision_l + recall_l)

5. Output: a LaTeX longtable per scene at
   `supplementary/journal/per_class_pr_table.tex` to be \\input from
   Suppl F.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT.parent / "CAOS_LDA_HSI" / "data" / "derived" / "topic_to_data"
OUT_TEX = REPO_ROOT / "supplementary" / "journal" / "per_class_pr_table.tex"

SCENES = [
    ("indian-pines-corrected", "Indian Pines"),
    ("salinas-corrected", "Salinas"),
    ("salinas-a-corrected", "Salinas-A"),
    ("pavia-university", "Pavia U"),
    ("kennedy-space-center", "KSC"),
    ("botswana", "Botswana"),
]


def per_class_pr_for_scene(payload: dict) -> list[dict]:
    """Build per-class P/R/F1 from a topic_to_data JSON."""
    n_k = payload["docs_per_topic_dominant"]
    rows = payload["p_label_given_topic_dominant"]  # K x L list of dicts

    # Collect all label rows from topic 0 (every topic uses the same
    # label vocabulary in the same order, by builder convention).
    labels = [{"id": d["label_id"], "name": d["name"]} for d in rows[0]]
    L = len(labels)
    K = len(n_k)

    # Build C[k, l] = count of pixels with topic=k and label=l.
    C = [[rows[k][l]["count"] for l in range(L)] for k in range(K)]

    # Topic-routed-hard: each topic maps to its arg-max label.
    topic_to_label = [max(range(L), key=lambda l: C[k][l]) for k in range(K)]

    metrics = []
    for l_idx, lab in enumerate(labels):
        tp = sum(C[k][l_idx] for k in range(K) if topic_to_label[k] == l_idx)
        predicted = sum(n_k[k] for k in range(K) if topic_to_label[k] == l_idx)
        actual = sum(C[k][l_idx] for k in range(K))
        precision = tp / predicted if predicted > 0 else 0.0
        recall = tp / actual if actual > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        metrics.append({
            "label_id": lab["id"],
            "name": lab["name"],
            "support": actual,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "predicted_count": predicted,
        })
    return metrics


def latex_escape(s: str) -> str:
    return s.replace("&", "\\&").replace("_", "\\_").replace("%", "\\%")


def render_scene_table(scene_label: str, rows: list[dict]) -> str:
    n_classes = len(rows)
    macro_p = sum(r["precision"] for r in rows) / n_classes
    macro_r = sum(r["recall"] for r in rows) / n_classes
    macro_f1 = sum(r["f1"] for r in rows) / n_classes
    total_support = sum(r["support"] for r in rows)
    micro_tp = sum(r["precision"] * r["predicted_count"] for r in rows)
    micro_predicted = sum(r["predicted_count"] for r in rows)
    micro_p = micro_tp / micro_predicted if micro_predicted > 0 else 0.0
    micro_r = micro_tp / total_support if total_support > 0 else 0.0

    lines = [
        f"\\subsection*{{{latex_escape(scene_label)}}}",
        f"Per-class precision, recall and F1 for the topic-routed-hard "
        f"classifier under the canonical fit ($K = \\max(4, \\min(12, n_{{\\text{{classes}}}}))$, "
        f"$\\alpha = 0.45$, $\\eta = 0.20$). "
        f"$n_{{\\text{{classes}}}} = {n_classes}$, support $= {total_support}$.",
        "",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Class & Support & Precision & Recall & F1 \\\\",
        "\\midrule",
    ]
    for r in rows:
        lines.append(
            f"{latex_escape(r['name'])} & {r['support']} & "
            f"{r['precision']:.3f} & {r['recall']:.3f} & {r['f1']:.3f} \\\\"
        )
    lines.append("\\midrule")
    lines.append(
        f"\\textit{{Macro avg}} & {total_support} & "
        f"{macro_p:.3f} & {macro_r:.3f} & {macro_f1:.3f} \\\\"
    )
    lines.append(
        f"\\textit{{Micro avg}} & {total_support} & "
        f"{micro_p:.3f} & {micro_r:.3f} & "
        f"{(2*micro_p*micro_r/(micro_p+micro_r) if (micro_p+micro_r) > 0 else 0.0):.3f} \\\\"
    )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    sections = []
    for scene_id, scene_label in SCENES:
        src = SRC / f"{scene_id}.json"
        if not src.exists():
            print(f"SKIP {scene_id}: {src} missing")
            continue
        payload = json.loads(src.read_text())
        rows = per_class_pr_for_scene(payload)
        sections.append(render_scene_table(scene_label, rows))
        print(
            f"OK {scene_label}: {len(rows)} classes, "
            f"macro F1 = {sum(r['f1'] for r in rows) / len(rows):.3f}"
        )

    OUT_TEX.write_text("\n".join(sections))
    print(f"wrote {OUT_TEX.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
