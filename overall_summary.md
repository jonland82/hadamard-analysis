# Overall Theory Summary

## Core narrative

The project begins with a tension:

> A Hadamard matrix is completely rigid when viewed as a whole, yet a small local window may reveal very little about the next entry.

The theory aims to quantify that tension and then ask whether even weak local information can accelerate an exact construction algorithm.

## 1. Exact global structure

A Hadamard matrix of order \(d\) is

\[
H\in\{-1,+1\}^{d\times d},
\qquad
HH^\top=dI_d.
\]

Thus every pair of distinct rows—and likewise columns—is orthogonal:

\[
\sum_{\ell=1}^{d} H_{i\ell}H_{j\ell}=0.
\]

After normalizing the first row and column to \(+1\), every other row must contain exactly \(d/2\) plus signs and \(d/2\) minus signs.

Conceptually, every row must be perfectly balanced and perfectly coordinated with all the others. This is the project's known global rigidity.

## 2. Local prediction asks a different question

Choose a way to read entries from the matrix—along rows, down columns, or through a flattened ordering—and call the resulting signs

\[
X_1,X_2,\ldots,
\qquad
X_t\in\{-1,+1\}.
\]

Given the last \(k\) signs,

\[
C_k=(X_{t-k+1},\ldots,X_t),
\]

ask how well they predict \(X_{t+1}\).

The local bias associated with a context \(c\) is

\[
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|.
\]

A value near zero means the context provides little predictive advantage; a large value means the local pattern strongly suggests the next sign.

The key idea is that exact global coordination does not necessarily imply strong short-range prediction.

## 3. Probability must come from somewhere

A deterministic matrix has no intrinsic probability distribution. Before the conditional probability above is meaningful, the theory must say what is sampled.

Possible models include:

- fix one matrix and choose a position uniformly;
- sample a normalized matrix from a finite collection, then choose a position;
- sample an equivalence class and specify how its representative is chosen;
- sample from a construction family such as the Sylvester matrices.

These models can produce different answers. Selecting the probability space, traversal, and treatment of boundaries is therefore the most important unresolved definition.

## 4. The proposed measure of local unpredictability

Once the probability model is fixed, the draft definition says the process is \(k\)-local \(\varepsilon\)-unpredictable if

\[
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|
\le \varepsilon
\]

for every supported context \(c\).

Two versions matter:

\[
\varepsilon_k^{\max}
=
\max_c
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|,
\]

which detects the most predictable context, and

\[
\varepsilon_k^{\mathrm{avg}}
=
\mathbb E_{C_k}
\left[
\left|
\Pr(X_{t+1}=+1\mid C_k)-\frac12
\right|
\right],
\]

which describes typical predictability. The average version is less vulnerable to rare contexts with very few observations.

An information-theoretic alternative is

\[
I(X_{t+1};C_k)
=
H(X_{t+1})-H(X_{t+1}\mid C_k),
\]

which measures how many bits of information the local context provides about the next sign.

## 5. The main theorem is still a target

The hoped-for result has the form

\[
\varepsilon_k\le \varepsilon(d,k)
\]

for a precisely defined ensemble and traversal, perhaps with

\[
\varepsilon(d,k)\longrightarrow 0
\qquad\text{as }d\to\infty
\]

when \(k\) is fixed.

In simple language: as matrices become larger, a bounded local window might become progressively less informative even though the complete matrix remains exactly constrained.

This is currently a conjectural direction, not a proved theorem. Highly structured families may expose strong local patterns, so such a bound may hold only for certain ensembles or averaging procedures.

## 6. Weak dependence is compatible with unpredictability

Earlier work apparently observed a nonzero "Markov" effect, but its exact statement has not been recovered.

The intended picture is not perfect local randomness. It is instead

\[
0<\varepsilon_k\ll \frac12.
\]

That would mean local patterns carry real but weak predictive information. The matrix is not locally independent, yet bounded history still leaves substantial uncertainty about the next sign.

## 7. Global constraints already produce exact search rules

When constructing two rows coordinate by coordinate, define their partial inner product

\[
S_{ij}(m)
=
\sum_{\ell=1}^{m}H_{i\ell}H_{j\ell}.
\]

Only \(d-m\) coordinates remain, so they can correct the partial sum by at most \(d-m\). Therefore a completion is possible only if

\[
|S_{ij}(m)|\le d-m,
\]

together with the appropriate parity condition.

If this inequality fails, the branch is mathematically impossible and can be safely discarded. Normalization, row balance, orthogonality, parity, and symmetry provide similar exact reductions.

## 8. Local prediction has a different algorithmic role

Suppose a model estimates

\[
\widehat p
=
\widehat{\Pr}(X_{t+1}=+1\mid C_k).
\]

The solver can try \(+1\) first when \(\widehat p>1/2\), and \(-1\) first otherwise. But unless the theory proves that one sign is impossible, the solver must retain both branches.

So the division is:

- global mathematical constraints determine which branches may be pruned;
- local statistical information determines which surviving branch should be tried first.

This preserves completeness: a poor predictor can slow the search, but it cannot cause the solver to miss a valid Hadamard matrix.

## 9. The intended endpoint

The strongest theoretical arc would be

\[
\text{exact global orthogonality}
\;\Longrightarrow\;
\text{provable limits on local prediction}
\;\Longrightarrow\;
\text{certified consequences for exact search}.
\]

A more modest but still coherent result would be:

- define local predictability rigorously;
- measure weak local dependence across Hadamard families;
- build a complete exact solver;
- show that the measured dependence improves branch ordering;
- clearly separate empirical speedups from proved mathematical facts.

In one sentence: the project is investigating how a system can be globally choreographed, locally hard to predict, and still locally informative enough to guide an exact search.
