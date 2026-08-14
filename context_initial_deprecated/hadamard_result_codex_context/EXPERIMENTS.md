# Experimental Program

The experiments have two distinct purposes:

1. **mathematics:** quantify local predictability;
2. **algorithms:** determine whether local predictability reduces search effort.

Do not infer theorem-level conclusions from search speedups alone.

---

## Experiment A — Local conditional bias

For an ensemble of Hadamard matrices, a traversal, and context length $k$, estimate

$$
\hat p_c
=
\widehat{\Pr}(X_{t+1}=+1\mid C_k=c).
$$

Then compute

$$
\hat\varepsilon_k^{\max}
=
\max_c
\left|\hat p_c-\frac12\right|
$$

and

$$
\hat\varepsilon_k^{\mathrm{avg}}
=
\sum_c \hat P(c)
\left|\hat p_c-\frac12\right|.
$$

Also report the sample count $n_c$ for each context.

### Required controls

- row traversal;
- column traversal;
- row-major flattening;
- column-major flattening;
- random iid Rademacher matrices as a null baseline;
- shuffled Hadamard entries preserving only selected marginals;
- multiple Hadamard orders;
- multiple inequivalent matrices where available.

### Statistical caution

Rare contexts can create spuriously large maximum bias. Use confidence intervals or minimum-support thresholds.

---

## Experiment B — Predictive log loss

Instead of only measuring accuracy, evaluate a local predictor with log loss.

For predicted probability $p_t$ assigned to the observed sign,

$$
L
=
-\frac1N\sum_t \log p_t.
$$

An unbiased predictor has baseline log loss

$$
\log 2
$$

per sign.

The excess information captured by the local model is related to the reduction below this baseline.

This is preferable to accuracy when biases are small.

---

## Experiment C — Conditional entropy

Estimate

$$
H(X_{t+1}\mid C_k).
$$

For an unbiased locally independent sign,

$$
H(X_{t+1}\mid C_k)=1 \text{ bit}.
$$

Define local predictive information

$$
I_k
=
1-H(X_{t+1}\mid C_k)
$$

when the marginal next-sign entropy is one bit.

More generally use

$$
I(X_{t+1};C_k)
=
H(X_{t+1})-H(X_{t+1}\mid C_k).
$$

This may become a cleaner theorem target than raw $\varepsilon$.

---

## Experiment D — Dependence on $k$

For

$$
k=1,2,\dots,K,
$$

plot

$$
k\mapsto
\hat\varepsilon_k^{\mathrm{avg}},
\qquad
k\mapsto
\hat\varepsilon_k^{\max},
\qquad
k\mapsto
\hat I_k.
$$

Earlier exploration considered small $k$ and then iterating upward; preserve this as a systematic sweep rather than selecting only favorable $k$.

---

## Experiment E — Row versus column order

Run exactly the same estimator with:

- horizontal local context;
- vertical local context.

This directly tests the earlier observation that the chosen ordering may materially affect predictability.

If $H$ and $H^\top$ are sampled symmetrically from the same ensemble, any persistent difference needs explanation; if the dataset construction breaks that symmetry, document it.

---

## Experiment F — Search-policy benchmark

Compare:

1. lexicographic branch ordering;
2. random branch ordering;
3. empirical $k$-Markov branch ordering;
4. optionally, a learned predictor.

Use the **same safe pruning constraints** in every condition.

Measure:

$$
N_{\text{nodes}},\quad
N_{\text{backtracks}},\quad
T.
$$

The key question is whether local information changes expected search order enough to reduce nodes visited before finding a valid completion.

Run many randomized trials where policies contain randomness.

---

## Experiment G — Ablation of exact constraints

Benchmark cumulative additions:

```text
naive
+ normalization
+ balance
+ row orthogonality
+ partial inner-product pruning
+ symmetry breaking
+ local branch ordering
```

This separates gains from established Hadamard structure from gains attributable to the new local model.

---

## Reproducibility requirements

Every experiment should record:

```text
order d
matrix family / source
equivalence normalization procedure
traversal
context length k
random seed
train/evaluation split if a model is fit
estimator
confidence method
software commit hash
hardware metadata where timing matters
```

Raw results should be saved in machine-readable form, preferably CSV/Parquet plus a small metadata JSON file.
