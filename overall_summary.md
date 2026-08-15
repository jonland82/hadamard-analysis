# Overall Theory Summary

This document gives the conceptual theory. The operational plan, data requirements, formal statement--experiment pairings, and proposed short-note sequence are in [`research_program.md`](research_program.md). The original handoff remains available under [`context_initial_deprecated/`](context_initial_deprecated/) as historical reference.

**Current status:** the structural Hadamard facts, exact pruning rules, and regional correction laws are established. An equivalence-invariant next-entry theorem remains open but is no longer the hinge of the project. Note 1 showed that nearly all strong serialized predictability disappears under equivalence-preserving randomization. Note 2 changed the local object: exact balance and partial-inner-product state significantly predicts next-block composition under randomized equivalent presentations, including early in construction. Its all-pair composite score also strongly ranks observed valid nonterminal blocks above random, balance-only, one-pair, and minimum-pressure policies. Serialized context adds no further randomized-presentation gain. Exact-search benefit remains untested.

## Core narrative

The canonical one-sentence research narrative is:

> Hadamard matrices are globally choreographed, locally elusive entry by entry, yet regionally predictable through their evolving constraint state—structure that may guide an exact search.

The project begins with the underlying tension:

> A Hadamard matrix can be elusive one entry at a time even while its unfinished regions carry exactly calculable correction burdens.

The theory now resolves the first half of that tension: serialized windows are representation-sensitive, while balance and partial inner products expose representation-resilient regional information. The remaining question is whether that information accelerates exact construction.

### How the experiments test the sentence

| Narrative clause | Mathematical content | Experiments |
|---|---|---|
| **Globally choreographed** | Exact orthogonality, normalization, balance, symmetry, and partial feasibility constrain the full matrix. | Structural lemmas establish this; the later solver ablation isolates each constraint's algorithmic contribution. |
| **Locally elusive entry by entry** | Short coordinate contexts need not carry invariant next-sign information. | Note 1 and Note 2's representation ablations show that the strong serialized signal follows catalog coordinate order. |
| **Regionally predictable through constraint state** | Partial row sums and inner products fix remaining sign and agreement inventories, inducing next-block laws. | Note 2 proves the hypergeometric laws and verifies them for $b=2,4,8$ under randomized equivalent presentations. |
| **Structure that may guide exact search** | A state score may order feasible blocks, while only proved impossibility may prune. | Note 2 establishes offline candidate ranking; the next note measures first-solution nodes and backtracks. |

This mapping is the backbone of the short-note sequence. The Note 1 representation result redirected the project from serialized adjacency to construction state; the next note must similarly abandon the search claim if offline ranking fails to reduce exact-search work.

## 1. Exact global structure

A Hadamard matrix of order $d$ is

$$
H\in\{-1,+1\}^{d\times d},
\qquad
HH^\top=dI_d.
$$

Thus every pair of distinct rows—and likewise columns—is orthogonal:

$$
\sum_{\ell=1}^{d} H_{i\ell}H_{j\ell}=0.
$$

Except for $d=1,2$, a necessary condition for existence is

$$
d\equiv0\pmod 4.
$$

This condition is necessary, not sufficient; the project must not assume existence at an order merely because it is divisible by four.

Multiplying rows or columns by $-1$ preserves the Hadamard property. Using these equivalences, one may normalize the first row and first column to $+1$. Every nonfirst row is then orthogonal to the all-$+1$ first row, so it contains exactly $d/2$ plus signs and $d/2$ minus signs.

With its first entry fixed to $+1$, a nonfirst normalized row has only

$$
\binom{d-1}{d/2}
$$

balanced possibilities rather than $2^{d-1}$. Further canonical choices, such as fixing a second row, may remove additional equivalent representations, but they require a proof that at least one representative of every equivalence class in scope survives.

Conceptually, every row must be perfectly balanced and perfectly coordinated with all the others. This is the project's known global rigidity.

## 2. Local prediction asks a different question

Choose a way to read entries from the matrix—along rows, down columns, or through a flattened ordering—and call the resulting signs

$$
X_1,X_2,\ldots,
\qquad
X_t\in\{-1,+1\}.
$$

Given the last $k$ signs,

$$
C_k=(X_{t-k+1},\ldots,X_t),
$$

ask how well they predict $X_{t+1}$.

The local bias associated with a context $c$ is

$$
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|.
$$

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

Once the probability model is fixed, the draft definition says the process is $k$-local $\varepsilon$-unpredictable if

$$
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|
\le \varepsilon
$$

for every supported context $c$.

Two versions matter:

$$
\varepsilon_k^{\max}
=
\max_c
\left|
\Pr(X_{t+1}=+1\mid C_k=c)-\frac12
\right|,
$$

which detects the most predictable context, and

$$
\varepsilon_k^{\mathrm{avg}}
=
\mathbb E_{C_k}
\left[
\left|
\Pr(X_{t+1}=+1\mid C_k)-\frac12
\right|
\right],
$$

which describes typical predictability. The average version is less vulnerable to rare contexts with very few observations.

An information-theoretic alternative is

$$
I(X_{t+1};C_k)
=
H(X_{t+1})-H(X_{t+1}\mid C_k),
$$

which measures how many bits of information the local context provides about the next sign.

The equivalent sign-expectation form of the worst-context definition is

$$
\left|
\mathbb E[X_{t+1}\mid C_k=c]
\right|
\le 2\varepsilon.
$$

### Balance already creates local dependence

Global balance is itself a source of local predictability. If a length-$d$ sign sequence is sampled uniformly from all sequences with exactly $d/2$ plus signs, and a prefix $c$ of length $k$ contains $a$ plus signs, then

$$
\Pr(X_{k+1}=+1\mid c)
=
\frac{d/2-a}{d-k}.
$$

Therefore its balance-induced bias is

$$
\left|
\Pr(X_{k+1}=+1\mid c)-\frac12
\right|
=
\frac{|k/2-a|}{d-k}.
$$

This derived baseline sharpens the central question. We should not ask merely whether Hadamard entries are locally dependent; normalized balanced rows must be dependent. We should ask whether Hadamard orthogonality creates local information beyond the amount explained by normalization, balance, family, and traversal.

## 5. The main theorem is still a target

The hoped-for result has the form

$$
\varepsilon_k\le \varepsilon(d,k)
$$

for a precisely defined ensemble and traversal, perhaps with

$$
\varepsilon(d,k)\longrightarrow 0
\qquad\text{as }d\to\infty
$$

when $k$ is fixed.

In simple language: as matrices become larger, a bounded local window might become progressively less informative even though the complete matrix remains exactly constrained.

This is currently a conjectural direction, not a proved theorem. Highly structured families may expose strong local patterns, so such a bound may hold only for certain ensembles or averaging procedures.

The worst-context, average-context, and information-theoretic claims are different theorem targets. A rare deterministic context can make $\varepsilon_k^{\max}$ large while average bias and mutual information remain small.

## 6. Weak dependence is compatible with unpredictability

Earlier work apparently observed a nonzero "Markov" effect, but its exact statement has not been recovered.

The intended picture is not perfect local randomness. It is instead

$$
0<\varepsilon_k\ll \frac12.
$$

That would mean local patterns carry real but weak predictive information. The matrix is not locally independent, yet bounded history still leaves substantial uncertainty about the next sign.

## 7. Global constraints already produce exact search rules

A completely naive search ranges over

$$
2^{d^2}
$$

sign matrices. Normalization, balance, and symmetry reduce the representation space before orthogonality is tested. A practical exact solver then constructs rows or coordinates incrementally and rejects partial states as soon as completion becomes impossible.

When constructing two rows coordinate by coordinate, define their partial inner product

$$
S_{ij}(m)
=
\sum_{\ell=1}^{m}H_{i\ell}H_{j\ell}.
$$

Only $d-m$ coordinates remain, so they can correct the partial sum by at most $d-m$. Therefore a completion is possible only if

$$
|S_{ij}(m)|\le d-m,
$$

together with the appropriate parity condition.

More explicitly, because a sum of $d-m$ signs has parity $d-m$, eventual cancellation also requires

$$
S_{ij}(m)\equiv d-m\pmod 2.
$$

For ordinary coordinate-wise construction at even order, this congruence is usually automatic because $S_{ij}(m)$ is itself a sum of $m$ signs and $m\equiv d-m\pmod2$. It should still be recorded in the feasibility statement, but not credited as an independent pruning gain unless the solver's state representation makes it nonredundant.

Partial row balance supplies another exact feasibility test: if a partial row already contains more than $d/2$ plus signs or more than $d/2$ minus signs, it cannot become balanced. The remaining coordinates must also be numerous enough to reach both final totals.

If this inequality fails, the branch is mathematically impossible and can be safely discarded. Normalization, row balance, orthogonality, parity, and symmetry provide similar exact reductions.

## 8. Local prediction has a different algorithmic role

Suppose a model estimates

$$
\widehat p
=
\widehat{\Pr}(X_{t+1}=+1\mid C_k).
$$

The solver can try $+1$ first when $\widehat p>1/2$, and $-1$ first otherwise. But unless the theory proves that one sign is impossible, the solver must retain both branches.

So the division is:

- global mathematical constraints determine which branches may be pruned;
- local statistical information determines which surviving branch should be tried first.

This preserves completeness: a poor predictor can slow the search, but it cannot cause the solver to miss a valid Hadamard matrix.

For a fixed finite search tree, branch ordering can change the number of nodes visited before the first solution but cannot change the total node set under exhaustive enumeration. Search-policy claims must therefore specify an order-sensitive stopping condition, normally the first valid completion.

The principal search measurements are

$$
N_{\mathrm{nodes}},
\qquad
N_{\mathrm{backtracks}},
\qquad
N_{\mathrm{pruned}},
\qquad
T_{\mathrm{wall}},
\qquad
T_{\mathrm{cpu}}.
$$

Node counts and backtracks are the primary scientific comparison because they depend less on hardware than runtime. A useful headline quantity is

$$
\mathrm{speedup}
=
\frac{N_{\mathrm{nodes,baseline}}}
     {N_{\mathrm{nodes,proposed}}}.
$$

Every policy comparison must use the same verifier, constraints, instances, stopping condition, and seeds where relevant.

## 9. The intended endpoint

The strongest supported arc is now

$$
\text{exact global balance and orthogonality}
\;\Longrightarrow\;
\text{exact regional correction laws}
\;\Longrightarrow\;
\text{held-out candidate-block ranking}
\;\Longrightarrow\;
\text{completeness-preserving exact-search guidance}.
$$

The first three links are established in Notes 1 and 2. The final implication is the next experimental target. A coherent solver result must:

- build a complete exact solver;
- hold its exact feasibility rules fixed across policies;
- compare all-pair ordering with random, lexicographic, balance-only, and minimum-pressure baselines;
- report first-solution nodes and backtracks as primary outcomes;
- separate empirical performance from the proved completeness guarantee.

The first two studies support a state-aware reading of this hypothesis: the global choreography is exact; arbitrary serialized windows remain difficult to predict; catalog coordinate order contains additional non-invariant information; but global correction burdens make regional behavior predictably nonrandom even under randomized equivalent presentations. Whether that state-derived regional signal improves exact search is still open.

## 10. Current claim registry

### [KNOWN]

- Hadamard orthogonality: $HH^\top=dI_d$.
- Row and column sign changes preserve the Hadamard property.
- A normalized nonfirst row is balanced.
- Except for orders $1$ and $2$, existence requires $d\equiv0\pmod 4$.
- Conditional entropy, mutual information, and optimal log loss obey their standard information-theoretic identities.

### [DERIVED]

- The partial-inner-product magnitude and parity tests are sound impossibility conditions.
- The uniform balanced-sequence formula gives the dependence forced by balance alone.
- The remaining plus count and every remaining pair-agreement count are fixed by the current partial sums; uniform remaining-coordinate order gives explicit hypergeometric next-block laws.
- Under a transpose-invariant ensemble and symmetric sampling, row and column population statistics agree.
- Sound additional pruning constraints produce a nested search tree.
- Statistical branch ordering preserves completeness when it never deletes an unproved branch.

### [DEFINITION DRAFT]

- Worst-context and average-context $k$-local $\varepsilon$-unpredictability.
- The precise matrix ensemble, equivalence weighting, traversal, boundary rule, and target-position distribution for the first theorem.

### [CONJECTURE]

- Constraint-state regional scores reduce first-solution search work when used for safe candidate ordering.
- The all-pair regional score reduces first-solution search work through completeness-preserving branch ordering.

### [EMPIRICAL]

- Across $20$ paired repetitions, the order-$28$, $k=8$ canonical representatives improve log loss over the fair-coin baseline by $0.13935$ nats, with a 95% repetition-bootstrap interval of $[0.13850,0.14014]$.
- Equivalence-preserving row and column permutations reduce that gain to $0.03047$ nats, while the balanced-row control gains $0.03033$ nats. Their paired difference is $0.00014$ with interval $[-0.00024,0.00052]$.
- The canonical-minus-permuted contrast is positive throughout $k=2,\ldots,12$ at orders $24$ and $28$. This indicates that most of the canonical signal is representation-specific rather than an invariant of the Hadamard equivalence class. Full conditions and tables are in [`ROBUSTNESS_RESULTS.md`](notes/01_bounded_context_predictability/ROBUSTNESS_RESULTS.md).
- Note 2 finds the exact predicted pooling invariances: row-reset statistics are unchanged by whole-row permutation and column-reset statistics are unchanged by whole-column permutation, to less than $4\times10^{-17}$ numerical discrepancy over all tested conditions.
- At $k=8$, disrupting within-row coordinate order reduces catalog gain by $0.13361$ nats/entry at order $24$ and $0.10895$ at order $28$; the column-traversal dual reductions are $0.12617$ and $0.09323$. Strict-interior prediction retains $0.10625$--$0.15113$ nats/entry, so normalization anchors explain only a minority of the catalog gain. Full results are in [`RESULTS.md`](notes/02_representation_ablation/RESULTS.md).
- For a partial row with $r$ positions remaining, balance fixes its remaining plus count and each partial inner product fixes the remaining agreement count with every completed row. Under randomized remaining-coordinate order, the next-block counts therefore follow explicit hypergeometric laws.
- In the $20$-repetition regional experiment, this constraint state predicts block summaries under both fixed-anchor and unrestricted randomized presentations for $b=2,4,8$. At unrestricted randomized order $28$, $b=8$, early gains are $0.05724$ nats for row composition and $0.12014$ nats for pressured-pair agreement; middle gains are $0.20139$ and $0.54619$.
- Serialized context adds no gain beyond constraint state after randomization, while retaining a large catalog-only residual. This separates representation-resilient global-to-regional information from representation-specific adjacency.
- In ambiguous nonterminal states, the all-pair composite likelihood strongly ranks observed valid blocks under randomized presentations. At order $28$, $b=8$, mean percentile is $0.8481$ early and $0.9316$ middle, compared with $0.5634$ and $0.6270$ for balance alone.

### [OPEN]

- The exact earlier "Markov result" must be reconstructed from code, data, or notes before it is cited.
- Generalization beyond the fixed catalog must be tested across construction families, representative-selection rules, and held-out orders.
- The offline all-pair ranking policy must be embedded in a complete solver and tested for first-solution node reduction.
- It remains unknown whether the demonstrated offline ranking reduces exact-search work.

## 11. Open mathematical questions

1. Does the all-pair score reduce first-solution nodes and backtracks in a complete solver?
2. How should pairwise marginal scores be combined or calibrated when their constraints are dependent?
3. Does the regional result generalize to held-out construction families and larger orders?
4. Which block size and row/column selection policy best balances guidance against branching cost?
5. Can one derive a tractable joint regional law stronger than the composite likelihood?
6. How does symmetry breaking interact with the state score during partial construction?
7. Can state information support a new sound pruning theorem, rather than branch ordering alone?
8. What asymptotic regional-information law follows as $d$ grows with fixed or slowly growing $b$?

## 12. Publication paths

The short notes support two coherent fallback papers:

- **Global Rigidity and Regional Prediction:** representation diagnosis, correction-state laws, regional log loss, and candidate ranking.
- **Constraint-Guided Hadamard Search:** normalized enumeration, exact partial pruning, completeness-preserving branch ordering, benchmarks, and ablations.

The strongest integrated paper would connect the two:

$$
\text{global balance and orthogonality}
\Longrightarrow
\text{proved regional correction distributions}
\Longrightarrow
\text{complete search with empirically improved branch ordering}.
$$

If the final performance implication fails, the regional-prediction paper remains complete and the exact-search paper should report the negative benchmark at the correct level.
