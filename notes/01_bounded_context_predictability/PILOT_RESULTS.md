# Pilot Results

> **Superseded as the primary evidence.** The planned repeated-split, context-sweep, order-sweep, leakage, and matched-control checks are complete in [`ROBUSTNESS_RESULTS.md`](ROBUSTNESS_RESULTS.md). This file preserves the original two-seed pipeline check.

## Status

**[EMPIRICAL — PILOT]** These results validate the pipeline and identify the next controls. They are not yet a final statistical claim.

## Setup

The main pilot used all available equivalence-class representatives at orders

$$
d\in\{16,20,24,28\},
$$

with class counts $5$, $3$, $60$, and $487$, respectively. Within each order, complete matrices were assigned to a deterministic 80/20 training/test split. No positions from a held-out matrix appeared in training.

For each order, the experiment compared:

- the normalized catalog representatives;
- independently row/column-permuted and renormalized equivalent matrices;
- independently generated normalized balanced rows;
- normalized matrices with IID interior signs.

The predictor used symmetric smoothing with $\alpha=1/2$ and contexts $k=1,\ldots,8$. Traversals were evaluated both as a complete row-major stream and with contexts reset at row boundaries.

## Exact sanity check

For every tested Hadamard matrix, the row-reset $k=1$ model has held-out log loss

$$
L=\log 2,
$$

matching the exact one-step neutrality statement. The full row-major stream shows a small $k=1$ gain caused by normalized row-boundary targets.

## Main comparison

The following table fixes the row-reset traversal and $k=8$. “Gain” is the fair-coin loss minus held-out loss, in nats per predicted sign.

| Order | Variant | Held-out loss | Gain over $\log 2$ |
|---:|---|---:|---:|
| 24 | Catalog Hadamard | 0.527024 | 0.166124 |
| 24 | Permuted equivalent | 0.657630 | 0.035517 |
| 24 | Balanced rows | 0.659605 | 0.033543 |
| 24 | Normalized IID | 0.677793 | 0.015354 |
| 28 | Catalog Hadamard | 0.553756 | 0.139391 |
| 28 | Permuted equivalent | 0.662078 | 0.031069 |
| 28 | Balanced rows | 0.663410 | 0.029737 |
| 28 | Normalized IID | 0.673917 | 0.019230 |

An independent split/control seed gave the same order-28 gains to three decimal places:

| Variant | Seed 20260814 | Seed 20260815 |
|---|---:|---:|
| Catalog Hadamard | 0.139391 | 0.138684 |
| Permuted equivalent | 0.031069 | 0.031015 |
| Balanced rows | 0.029737 | 0.029439 |
| Normalized IID | 0.019230 | 0.019258 |

## Interpretation

1. **Transfer within the catalog representation is real in this pilot.** A context model trained on some equivalence classes predicts held-out classes of the same order substantially better than a fair coin.
2. **Most of that gain is representation-dependent.** Independent row/column permutations preserve the Hadamard property but reduce the order-28 gain from about $0.139$ to $0.031$ nats.
3. **The residual after permutation is close to the balance baseline.** At order 28, permuted Hadamards and balanced rows differ by only about $0.0013$ nats at $k=8$.
4. **Normalization itself is predictive.** Even the normalized-IID control shows a small gain, so a fair coin is necessary but not sufficient as the only baseline.

The current evidence therefore does **not** support an equivalence-invariant local-predictability claim. It supports a narrower statement: the catalog's normalized representatives contain transferable sequential regularities, most of which are destroyed by equivalence-preserving permutations.

## Limitations

- Only two split/control seeds have been run.
- Each seed uses one random permutation and one generated control per matrix.
- Orders 16 and 20 contain too few equivalence classes for stable held-out conclusions.
- The current uncertainty is not quantified with class-level bootstrap intervals.
- The catalog's representative-selection algorithm may itself create common sequential structure.
- No held-out-family or held-out-order conclusion follows from the same-order class splits.

## Completed follow-up

The requested follow-up repeated orders $16$--$28$ over $20$ paired split/control seeds and context lengths through $k=12$. It reports repetition-level uncertainty for

$$
\Delta_k
=
L_k^{\mathrm{control}}
-
L_k^{\mathrm{Hadamard}},
$$

with the permuted-equivalent and balanced-row models as the primary controls. See [`ROBUSTNESS_RESULTS.md`](ROBUSTNESS_RESULTS.md) for the result: at the primary $k=8$ comparison, the permuted-equivalent and balanced-row gains are statistically indistinguishable at orders $24$ and $28$.
