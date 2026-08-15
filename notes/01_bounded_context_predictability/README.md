# Note 1: Bounded-Context Predictability

## Working title

*Where the Signal Lives: Bounded-Context Prediction in Hadamard Representatives*

## Workshop manuscript

- [`paper/note1.pdf`](paper/note1.pdf) is the compiled five-page, single-column workshop note.
- [`paper/note1.tex`](paper/note1.tex) is the LaTeX source and [`paper/references.bib`](paper/references.bib) is its bibliography.

Build from the `paper/` directory with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error note1.tex
```

## Question

Read a normalized Hadamard matrix from left to right and top to bottom, producing

$$
X_1,X_2,\ldots,X_{d^2}.
$$

For a bounded context

$$
C_k=(X_{t-k+1},\ldots,X_t),
$$

does $C_k$ contain information about $X_{t+1}$ that transfers to held-out matrices?

The note does not assume that the flattened sequence is a genuine finite-order Markov chain. A smoothed $k$-context model is simply the first estimator of

$$
\Pr(X_{t+1}=+1\mid C_k=c).
$$

## Narrative role

This note tests the first two clauses of the project's now-revised narrative:

> Hadamard matrices are globally choreographed, locally elusive entry by entry, yet regionally predictable through their evolving constraint state—structure that may guide an exact search.

The first note stops before the regional and search claims. Its PDF intentionally preserves the earlier project wording under which it was written; Note 2 records the evidence that motivated the revision above.

## Planned mathematical statements

1. **Interior one-step neutrality.** When all rows are included, transitions between adjacent entries that remain inside a row have an unbiased next sign under uniform sampling of eligible positions.
2. **Boundary effect.** Row-major flattening introduces $d-1$ transitions whose target is the normalized first-column value $+1$.
3. **Training-fit monotonicity.** Because the order-$k$ context-model class contains the order-$(k-1)$ class, optimized training log loss cannot increase with $k$.
4. **Representation dependence.** Row and column permutations preserve the Hadamard property but can change row-major $k$-gram statistics.
5. **Balance baseline.** A uniformly random balanced row has a known sampling-without-replacement conditional law that must be separated from Hadamard-specific structure.

## Experiment sequence

1. Acquire, normalize, and independently verify a small-order matrix corpus.
2. Reproduce context counts for $k=1,\ldots,K$ on row-major sequences.
3. Compare training and held-out log loss using matrix-level splits.
4. Ablate row boundaries, the normalized first row and column, and representative ordering.
5. Compare with IID signs, uniformly balanced rows, and shuffled Hadamard controls.
6. Repeat across orders and equivalence classes, reporting context support and uncertainty.

Detailed implementation and output conventions are in [`experiments/README.md`](experiments/README.md).

The completed five-check analysis is summarized in [`ROBUSTNESS_RESULTS.md`](ROBUSTNESS_RESULTS.md). The earlier pipeline checks remain in [`PILOT_RESULTS.md`](PILOT_RESULTS.md) for provenance. Raw CSV results and metadata are under [`experiments/results/`](experiments/results/).

## Compute policy

Start locally. The proposed corpus through order $28$ contains only hundreds of equivalence-class representatives and well under one million matrix entries. Exact verification and context counting at modest $K$ should be easy on the current 8-core, 32-GB machine.

Consider AWS only after the local pipeline is tested and one of these conditions holds:

- a representative run takes more than roughly two hours;
- a sweep requires many thousands of independent permutation, bootstrap, or hyperparameter runs;
- the working set approaches available memory;
- we intentionally expand toward the millions of known order-$32$ equivalence classes.

The code should remain deterministic, command-line driven, and partitionable by matrix/order so the same experiment can move to AWS without being rewritten.

## Status

- **[KNOWN]:** the underlying Hadamard orthogonality and normalization facts.
- **[DERIVED]:** normalization/balance, exact one-step neutrality, the balance-only conditional law, representation non-invariance, and completeness under branch ordering are proved in the workshop manuscript.
- **[EMPIRICAL]:** across $20$ paired repetitions, bounded contexts predict held-out canonical representatives from the same order, but nearly all of the gain disappears under independent row/column permutations and approaches the balanced-row control.
- **[EMPIRICAL]:** no practically meaningful equivalence-invariant residual is detected at the primary $k=8$ comparison for orders $24$ and $28$.
- **[OPEN]:** the earlier remembered in-sample result has not yet been reconstructed and is not treated as evidence.
- **[OPEN]:** whether the representation-dependent signal improves canonical exact search.
