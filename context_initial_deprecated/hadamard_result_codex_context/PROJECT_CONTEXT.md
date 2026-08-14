# Project Context

## 1. Core object

A Hadamard matrix of order $d$ is a matrix

$$
H=(H_{ij})\in\{-1,+1\}^{d\times d}
$$

satisfying

$$
HH^\top=dI_d.
$$

Equivalently, for distinct rows $r_i,r_j$,

$$
\langle r_i,r_j\rangle
=
\sum_{\ell=1}^{d}H_{i\ell}H_{j\ell}
=
0.
$$

The same holds for distinct columns.

Except for $d=1,2$, a necessary condition for existence is $d\equiv0\pmod 4$.

## 2. Normalization

By multiplying rows and columns by $-1$, one may normalize a Hadamard matrix so that its first row and first column are all $+1$.

For a normalized Hadamard matrix, every nonfirst row is orthogonal to the all-$+1$ first row, so it contains equally many $+1$ and $-1$ entries:

$$
\sum_{\ell=1}^{d}H_{i\ell}=0
\qquad (i>1).
$$

Because the first entry is fixed to $+1$, a candidate nonfirst row may be chosen from

$$
\binom{d-1}{d/2}
$$

balanced possibilities.

**Status:** KNOWN.

## 3. Research tension

The project is centered on a useful tension:

> Hadamard matrices are globally rigid but may remain only weakly predictable from bounded local context.

Global rigidity comes from exact orthogonality and balance constraints.

Local predictability asks a different question: if only a short local history is known, how much better than chance can one predict the next sign?

These two properties are not contradictory. A sequence or matrix can satisfy strong long-range/global constraints while exhibiting low short-range predictive bias.

## 4. Local context

A generic local context of length $k$ may be denoted

$$
C_k=(X_{t-k+1},\dots,X_t),
$$

where $X_t\in\{-1,+1\}$ is obtained from some specified traversal of a Hadamard matrix.

Possible traversals include:

- left-to-right within a row;
- top-to-bottom within a column;
- flattened row-major order;
- flattened column-major order;
- a traversal defined on an equivalence-normalized matrix.

Experiments already raised the possibility that row and column traversal may behave differently.

**Important:** a theorem must state which traversal is being used.

## 5. Probability-space issue

A conditional probability such as

$$
\Pr(X_{t+1}=+1\mid C_k=c)
$$

requires an explicit source of randomness.

Candidate probability spaces include:

1. uniformly sample a matrix from a finite set of Hadamard matrices of order $d$, then sample a valid position;
2. uniformly sample an equivalence class, then a normalized representative according to a specified rule;
3. fix a matrix and sample positions uniformly;
4. study an empirical distribution over a particular enumerated dataset;
5. study a generative family (e.g. Sylvester matrices) under a random index.

These choices are mathematically different and may produce different local biases.

No “local unpredictability theorem” should be treated as rigorous until this is fixed.

## 6. Markov/local-dependence direction

Prior project discussion found nonzero local dependence described informally as a **Markov result**. Its exact formal theorem statement is not preserved in this handoff.

Therefore:

- do not invent its statement;
- treat “there is some measurable local predictive structure” as project context, not a proved theorem;
- reconstruct the exact result from experiments/notes before citing it formally;
- once reconstructed, record its order $k$, probability model, estimator, bound, and proof/empirical status.

## 7. Intended conceptual claim

The desired end result is stronger and more precise than saying “Hadamard matrices are random.”

The intended direction is:

> Hadamard matrices have exact global structure, while bounded local information leaves at most a small predictive advantage, quantified by $\varepsilon$.

This is a research target, not yet a certified theorem in the form above.
