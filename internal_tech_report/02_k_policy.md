# Per-V K-policy — derivation and alternatives rejected

## P1 policy

$$K_{\text{P1}} = \max(4, \min(12, n_{\text{classes}}))$$

Works well for V1 because document length is uniformly $B$ tokens
(200 for Indian Pines, 204 for Salinas, etc.) so the latent simplex
has enough room for 12 topics. Fails for recipes whose document
length collapses.

## The collapse

For each recipe we measured mean tokens per document on Indian Pines
(uniform / Q=8):

| V | mean doc length | K_P1 (16 classes) | K=K_P1 viable? |
|---|---|---|---|
| V1  | 450 | 12 | ✓ |
| V2  | 200 | 12 | ✓ |
| V3  | 200 | 12 | ✓ |
| V4  | 585 | 12 | ✓ |
| V5  | 622 | 12 | ✓ |
| V6  | 75  | 12 | borderline |
| V7  | 6   | 12 | ❌ — only 6 tokens but K=12 → topics collapse |
| V8  | 14  | 12 | ❌ — only 14 tokens / 12 endmembers |
| V9  | 1   | 12 | ❌ catastrophic — 1 token, K=12 |
| V10 | 3   | 12 | ❌ — only 3 tokens, K=12 |
| V11 | 4   | 12 | ❌ — only 4 PQ codes, K=12 |
| V12 | 200 | 12 | ✓ |

LDA's posterior on a document with $L$ tokens and $K > L$ topics is
degenerate: each token can only contribute to at most $L$ topics, so
$K - L$ topics receive only the prior $\alpha$ → they all look alike,
seed stability collapses, and downstream evaluation is meaningless.

## V-sweep policy

$$K_V = \mathrm{clip}\!\left(\left\lfloor \tfrac{\overline{\mathrm{doc\,len}}_V}{2} \right\rfloor, 3, K_{\text{P1}}\right)$$

Concretely (Indian Pines):

| V | K_V |
|---|---|
| V1, V2, V3, V4, V5, V12 | 12 |
| V6 | 12 (mean 75 / 2 = 37, clipped to 12) |
| V7 | 3 |
| V8 | 7 |
| V9 | 3 |
| V10 | 3 |
| V11 | 3 |

The lower bound of 3 is set so the model still has nontrivial topic
structure. The upper bound K_P1 ensures we never *exceed* the P1
policy (avoiding spurious gain for V1 due to lower K).

## Alternatives rejected

### Option A — keep $K = K_{\text{P1}}$ for all recipes

Rejected. Lets V1 win F-1 by construction because V7 / V9 / V10 / V11
have collapsing topics. Not a fair comparison.

### Option B — set $K$ per recipe + scene to maximise F-1 separately

Rejected. Optimising K per cell would let recipes overfit on the
scene they're tested on, conflating recipe quality with K-selection
quality. (The F-4 axis already measures K-sensitivity separately.)

### Option C — use Hierarchical Dirichlet Process to infer $K$

Deferred to a follow-up paper (issue
[#621](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/621)).
HDP changes the model class, not just the K choice, so it belongs in
the backbone-factorial study (issue
[#617](https://github.com/fsantibanezleal/CAOS_LDA_HSI/issues/617)).

### Option D — fix $K = K_{\text{P1}}$ for V1..V6, V12 (dense); use document-aware K for V7..V11 (sparse)

This is essentially what the V-sweep policy does. Adopted.

## Sensitivity to the K-policy

We sampled F-1 on Indian Pines with three K policies (V-sweep,
Option A, fixed K=4 across all) and observed:

- Option A: V7 collapses to a single topic (macro-F1 ~0.05), V9 same
  (~0.12), V10 same (~0.20). V1 wins by default. Confirms the
  argument above.
- Fixed K=4 across all: all recipes converge to similar K-relative
  scores; V1 loses its advantage as expected. But the comparison
  is less informative because the dense recipes are penalised
  artificially.
- V-sweep policy: produces the actual result documented in P3.

## Reproducibility note

The K-policy table above is computed deterministically at
`build_v_sweep_canonical_fit.topic_count_for(scene_id, mean_doc)`.
For the factorial study (issue #617) each backbone (HDP / ProdLDA /
ETM / LDVAE) needs its own K-policy because their priors differ —
the V-sweep policy assumes online-VB LDA's Dirichlet prior.
