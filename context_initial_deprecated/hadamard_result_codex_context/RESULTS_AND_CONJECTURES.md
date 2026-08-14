# Results, Definitions, and Conjectures

This file deliberately separates established facts from project-level hypotheses.

---

## R1. Global orthogonality

For a Hadamard matrix $H$,

$$
HH^\top=dI.
$$

Hence for $i\neq j$,

$$
\sum_{\ell=1}^{d}H_{i\ell}H_{j\ell}=0.
$$

**Status:** KNOWN.

---

## R2. Balance after normalization

If the first row is normalized to all $+1$, every other row contains exactly $d/2$ plus signs and $d/2$ minus signs.

**Status:** KNOWN.

---

## R3. Exact partial-orthogonality feasibility bound

Suppose two rows are being constructed and after $k$ coordinates their partial inner product is

$$
S_{ij}(k)
=
\sum_{\ell=1}^{k}H_{i\ell}H_{j\ell}.
$$

There are $d-k$ coordinates left. Each remaining product contributes either $+1$ or $-1$. Therefore the largest possible correction magnitude is $d-k$.

A necessary condition for eventual orthogonality is

$$
|S_{ij}(k)|\le d-k.
$$

Thus if

$$
|S_{ij}(k)|>d-k,
$$

the partial branch is impossible and may be pruned immediately.

A parity constraint also applies: to finish at zero, $S_{ij}(k)$ and $d-k$ must have compatible parity.

**Status:** DERIVED from the Hadamard constraint; elementary and exact.

---

## D1. Draft definition: local $\varepsilon$-unpredictability

After fixing a probability model and traversal, define a binary process $X_t\in\{-1,+1\}$.

A natural candidate definition is that the process is **$k$-local $\varepsilon$-unpredictable** if, for every context $c$ of length at most $k$ with positive probability,

$$
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|
\le \varepsilon.
$$

Equivalent sign-expectation form:

$$
\left|
\mathbb E[X_{t+1}\mid C_k=c]
\right|
\le 2\varepsilon.
$$

Interpretation:

- $\varepsilon=0$: locally indistinguishable from an unbiased sign with respect to the chosen context;
- small $\varepsilon>0$: weak but nonzero local predictability;
- large $\varepsilon$: substantial local structure.

**Status:** DEFINITION DRAFT.

### Alternative average-case version

The worst-context definition can be dominated by rare contexts. An average-case measure is

$$
\varepsilon_k^{\mathrm{avg}}
=
\mathbb E_{C_k}
\left[
\left|
\Pr(X_{t+1}=+1\mid C_k)-\frac12
\right|
\right].
$$

A maximum-context version is

$$
\varepsilon_k^{\max}
=
\max_{c:\Pr(C_k=c)>0}
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|.
$$

These should be measured separately.

**Status:** DEFINITION DRAFT.

---

## C1. Global rigidity with bounded local unpredictability

Candidate theorem shape:

> Under a specified ensemble of normalized Hadamard matrices and a specified traversal, there exists a function $\varepsilon(d,k)$ such that bounded local contexts satisfy
>
> $$
> \left|
> \Pr(X_{t+1}=+1\mid C_k=c)-\frac12
> \right|
> \le \varepsilon(d,k),
> $$
>
> while the full matrix obeys exact global orthogonality.

The research goal is to determine whether a useful bound exists, for which ensembles/traversals, and whether

$$
\varepsilon(d,k)\to0
$$

in any asymptotic regime such as fixed $k$ and increasing $d$.

**Status:** CONJECTURE / theorem target.

### Why this is nontrivial

Global orthogonality alone does not automatically imply small local conditional bias for every ordering or every Hadamard family. Highly structured constructions may expose deterministic local patterns under some traversals.

Therefore this theorem must be proved for a precisely defined ensemble, family, or averaging scheme.

---

## C2. Weak Markov predictability can coexist with C1

The earlier project direction suggested a weak finite-history predictive advantage.

A compatible formal target is

$$
0 < \varepsilon_k \ll \frac12.
$$

Thus the desired statement is not “locally random,” but “locally only weakly predictable.”

**Status:** CONJECTURE until the previous Markov result is reconstructed and certified.

---

## C3. Search heuristic from local information

If a fitted local model estimates

$$
p_t
=
\Pr(X_{t+1}=+1\mid C_k),
$$

then a backtracking search can try the more likely sign first.

This can reduce expected search work if the model has real predictive value.

However, unless a local rule logically excludes a sign, it must **not** be used for pruning in an exact complete search.

**Status:** ALGORITHMIC PRINCIPLE.

---

## Open mathematical questions

1. What is the correct probability space?
2. Should local context be measured in rows, columns, or both?
3. Does $\varepsilon_k$ depend strongly on the Hadamard equivalence class?
4. For fixed $k$, does local predictive bias decrease with order $d$?
5. Are Sylvester/Walsh matrices atypically predictable compared with generic equivalence classes?
6. Can orthogonality imply a nontrivial information-theoretic upper bound on local mutual information?
7. Can the earlier Markov result be proved analytically rather than only observed?
8. Can local information yield a **safe pruning theorem**, not merely better branch ordering?
