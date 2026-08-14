# Research Program: Mathematical Notes and Experiments

## Purpose

The canonical one-sentence research hypothesis is:

> Hadamard matrices are globally choreographed, locally hard to predict, yet potentially locally informative enough to guide an exact search.

The work will be developed as a sequence of short notes. Each experiment is paired with a precise mathematical statement, an empirical hypothesis, and an explicit limitation. The strongest compatible sequence can later be consolidated into a final paper.

The completed Note 1 robustness study narrows the intended reading: canonical representatives are locally predictable at moderate context length, but nearly all of that gain disappears after equivalence-preserving row and column permutations and becomes statistically indistinguishable from the balanced-row baseline at the primary comparison. Thus local information is currently established as a representation-dependent empirical signal; generalization beyond the fixed catalog and usefulness for exact search remain open.

## Narrative-to-experiment map

| One-sentence clause | What must be established | Experiments and notes |
|---|---|---|
| **Globally choreographed** | The full matrix obeys exact orthogonality, normalization, balance, symmetry, and partial feasibility constraints. | The structural lemmas are the starting point; Experiment G measures their separate algorithmic effects. |
| **Locally hard to predict** | Bounded context leaves high conditional entropy and only small conditional bias under an explicit probability model. | Experiments A and C measure bias and entropy; D studies the context scale; E tests traversal dependence. |
| **Still locally informative** | The local signal is nonzero, survives controls, and improves held-out prediction. | Experiment B tests predictive log loss; A and C determine whether the signal exceeds balance-only information. |
| **Enough to guide exact search** | The signal improves the order in which feasible branches are explored without becoming an unsafe pruning rule. | Experiment F tests first-solution node reduction; G separates ordering gains from exact pruning gains. |

This table is not merely organizational. It gives the dependency structure of the argument. Experiments F and G support the full narrative only if Experiments A--C first identify reproducible, held-out local information. A null result earlier in the chain should shorten or redirect the later notes.

## Claim discipline

Use the following labels throughout the project:

- **[KNOWN]**: an established mathematical fact;
- **[DERIVED]**: proved within this project;
- **[EMPIRICAL]**: supported by a reproducible computation;
- **[CONJECTURE]**: a mathematical or empirical hypothesis not yet established;
- **[DEFINITION DRAFT]**: a proposed definition still being refined;
- **[OPEN]**: unresolved.

An experiment can support an empirical statement, but it cannot by itself establish a universal theorem. Exact statements and measured findings should appear separately in every note.

## Shared formal setup

For each order $d$, specify:

- a distribution $\mathcal E_d$ over Hadamard matrices or equivalence classes;
- a normalization and representative-selection procedure;
- a traversal $T$;
- a distribution over valid target positions $t$;
- a rule for whether contexts may cross row or column boundaries.

The traversal produces signs

$$
X_1,X_2,\ldots,
\qquad X_t\in\{-1,+1\}.
$$

For a length-$k$ context

$$
C_k=(X_{t-k+1},\ldots,X_t),
$$

define

$$
p_k(c)=\Pr(X_{t+1}=+1\mid C_k=c),
$$

$$
\varepsilon_k^{\max}
=
\max_{c:\Pr(C_k=c)>0}
\left|p_k(c)-\frac12\right|,
$$

and

$$
\varepsilon_k^{\mathrm{avg}}
=
\mathbb E
\left[
\left|p_k(C_k)-\frac12\right|
\right].
$$

These are **[DEFINITION DRAFT]** until the shared sampling choices are fixed for a particular note.

## Data plan

The Note 1 experiment code now downloads and caches a small-order McKay corpus locally, verifies each matrix exactly, and records the completed robustness study under [`notes/01_bounded_context_predictability/`](notes/01_bounded_context_predictability/). Raw downloaded data remain untracked; reproducible result tables and metadata are tracked. Every matrix must pass the exact integer check

$$
H\in\{-1,+1\}^{d\times d},
\qquad HH^\top=dI_d.
$$

For Experiments A--E, one derived observation should record at least

```text
matrix_id
order_d
family_or_source
equivalence_class_if_known
normalization
traversal
target_position
context_length_k
context
next_sign
split
```

Training and evaluation splits should be made by matrix or equivalence class, rather than by individual positions, when the goal is to test generalization beyond a known matrix.

Required controls are:

- IID Rademacher signs;
- uniformly sampled balanced sign sequences;
- shuffled Hadamard entries with the preserved marginals documented;
- multiple orders and inequivalent matrices where available;
- structured families such as Sylvester/Walsh matrices analyzed separately.

Experiments F--G generate solver-run data rather than next-sign observations. Each run should record the order, instance or construction task, policy, exact constraints, seed, stopping condition, nodes, prunes, backtracks, depth profile, CPU time, and wall time.

## Note 1 / Experiment A: Balance and local conditional bias

**Narrative role:** distinguishes the unavoidable dependence created by global choreography from any additional Hadamard-specific local signal, and begins the test of “locally hard to predict.”

### Question

How much next-sign bias is explained by balance alone, and is there residual bias specific to Hadamard structure?

### [DERIVED] Lemma: balanced-sequence baseline

Let $X_1,\ldots,X_d$ be uniform over sign sequences containing exactly $d/2$ plus signs. If a prefix $c$ of length $k$ contains $a$ plus signs, then

$$
\Pr(X_{k+1}=+1\mid X_1,\ldots,X_k=c)
=
\frac{d/2-a}{d-k}.
$$

Consequently,

$$
\left|
\Pr(X_{k+1}=+1\mid c)-\frac12
\right|
=
\frac{|k/2-a|}{d-k}.
$$

The proof is immediate by counting the plus signs remaining after conditioning on the prefix. This shows that global balance alone creates weak local dependence.

### [EMPIRICAL] Result

Catalog representatives exhibit substantial same-order held-out local information, but nearly all of the gain disappears after equivalence-preserving row and column permutations. At the primary orders $24$ and $28$, the permuted-equivalent residual is statistically indistinguishable from the balanced-row baseline at $k=8$.

### Experiment

Estimate $p_k(c)$, $\varepsilon_k^{\max}$, and $\varepsilon_k^{\mathrm{avg}}$, reporting the support count for every context. Compare Hadamard data with IID, balanced-sequence, and shuffled controls. Use confidence intervals or minimum-support thresholds for rare contexts.

### Limitation

The result is conditional on the fixed catalog, row-reset traversal, representative-selection convention, and same-order splits. It is not an equivalence-invariant, held-out-family, held-out-order, or asymptotic claim.

### Workshop manuscript

[*Where the Signal Lives: Bounded-Context Prediction in Hadamard Representatives*](notes/01_bounded_context_predictability/paper/note1.pdf)

## Note 2 / Experiment B: Predictive log loss

**Narrative role:** tests the word “informative” by requiring the local signal to improve probability forecasts on held-out matrices, not merely appear in in-sample counts.

### Question

Does measured local bias generalize into useful out-of-sample probability predictions?

### [KNOWN] Proposition: optimal conditional log loss

Among predictors using $C_k$, the true conditional distribution minimizes expected log loss, with minimum

$$
H(X_{t+1}\mid C_k).
$$

The gain over a fair-coin predictor is

$$
\log 2-H(X_{t+1}\mid C_k).
$$

When $X_{t+1}$ is marginally unbiased, this gain equals

$$
I(X_{t+1};C_k).
$$

When it is not marginally unbiased, the primary comparison should also include the best unconditional predictor so that marginal and contextual information are separated.

### [CONJECTURE] Empirical statement

A local predictor achieves held-out log loss below both the marginal-only predictor and the corresponding balanced-sequence baseline.

### Experiment

Fit context-frequency or smoothed Markov predictors on training matrices and evaluate log loss on held-out matrices or equivalence classes. Report calibration and sample support as well as aggregate loss.

### Limitation

Training and evaluating on positions from the same matrix may measure memorization rather than transferable Hadamard structure.

### Proposed note title

*Out-of-Sample Local Prediction in Hadamard Ensembles*

## Note 3 / Experiment C: Conditional entropy and mutual information

**Narrative role:** quantifies how “hard to predict” and “informative” coexist: conditional entropy can remain near one bit while mutual information is small but positive.

### Question

How many bits of information does a bounded context contain about the next sign?

### [KNOWN] Proposition: bias and information

If $X_{t+1}$ is marginally unbiased, then

$$
I(X_{t+1};C_k)
=
\mathbb E_{C_k}
\left[
D_{\mathrm{KL}}
\left(
\operatorname{Bern}(p_k(C_k))
\middle\|
\operatorname{Bern}\left(\frac12\right)
\right)
\right].
$$

With natural logarithms, Pinsker's inequality implies

$$
2\,\mathbb E
\left[
\left(p_k(C_k)-\frac12\right)^2
\right]
\le
I(X_{t+1};C_k),
$$

and therefore

$$
\varepsilon_k^{\mathrm{avg}}
\le
\sqrt{\frac{I(X_{t+1};C_k)}{2}}.
$$

### [CONJECTURE] Empirical statement

Bounded context carries positive but small mutual information about the next sign after controlling for balance and marginal bias.

### Experiment

Estimate conditional entropy and mutual information with held-out evaluation or finite-sample corrections. Report values in bits or nats consistently and include the estimator used.

### Limitation

Naive plug-in entropy estimators are biased when the number of contexts is large relative to the sample size.

### Proposed note title

*Local Predictive Information in Hadamard Matrices*

## Note 4 / Experiment D: Dependence on context length

**Narrative role:** identifies the scale at which “local” is meaningful and tests whether bounded context stays weak as matrix order grows.

### Question

At what context scale does Hadamard structure become visible?

### [KNOWN] Proposition: monotonicity with nested context

For a fixed target variable and genuinely nested contexts,

$$
H(X_{t+1}\mid C_{k+1})
\le
H(X_{t+1}\mid C_k),
$$

so

$$
I(X_{t+1};C_{k+1})
\ge
I(X_{t+1};C_k).
$$

The population quantities $\varepsilon_k^{\mathrm{avg}}$ and $\varepsilon_k^{\max}$ are likewise nondecreasing for nested contexts. This follows because each coarser conditional expectation is an average of finer conditional expectations and absolute value is convex.

### [CONJECTURE] Empirical statement

Predictive information grows with $k$ but remains small for a useful regime such as bounded $k$ relative to increasing $d$.

### Experiment

Sweep $k=1,\ldots,K$ without selecting only favorable values. Plot average bias, maximum supported bias, mutual information, sample coverage, and held-out log loss.

### Limitation

Finite-sample estimates need not look monotone because longer contexts become sparse. The population theorem is not a license to monotonize noisy estimates silently.

### Proposed note title

*The Context Scale of Predictability in Hadamard Matrices*

## Note 5 / Experiment E: Row and column traversal

**Narrative role:** tests whether local unpredictability is a property of the chosen ensemble or an artifact of how the globally structured matrix is read.

### Question

Is local predictability intrinsic to the ensemble, or produced by how matrices are represented and traversed?

### [DERIVED] Proposition: transpose invariance

If the matrix distribution satisfies

$$
H\overset{d}=H^\top
$$

and positions and boundaries are sampled symmetrically, then every population statistic under row traversal equals its corresponding statistic under column traversal. In particular,

$$
\varepsilon_{k,\mathrm{row}}
=
\varepsilon_{k,\mathrm{column}}
$$

and the corresponding mutual informations are equal.

The proof is the measure-preserving correspondence between row observations of $H$ and column observations of $H^\top$.

### [OPEN] Diagnostic statement

An observed row--column difference must be traced to sampling variation or to a failure of transpose invariance in the ensemble, representative selection, normalization, boundary rules, or family composition.

### Experiment

Run identical estimators for paired row and column traversals. Test the dataset and preprocessing pipeline for transpose closure before interpreting any difference structurally.

### Limitation

A difference in a non-transpose-invariant dataset is not evidence that Hadamard matrices in general have an intrinsic directional asymmetry.

### Proposed note title

*Transpose Symmetry and Traversal Dependence in Hadamard Data*

## Note 6 / Experiment F: Statistical branch ordering

**Narrative role:** tests the final clause directly: whether weak local information is useful enough to guide an exact first-solution search while preserving completeness.

### Question

Can weak local information reduce the work required to find a valid completion without making the solver incomplete?

### [DERIVED] Theorem: completeness under branch ordering

Suppose pruning uses only sound impossibility conditions and every unpruned child is eventually explored. Reordering children using a statistical predictor does not change completeness.

For a fixed finite search tree, ordering can change the number of nodes visited before the first solution. If the whole tree is exhaustively enumerated and no stateful learning changes the tree, ordering alone does not change the total set of visited nodes.

**Proof.** A branch policy permutes the order of a node's children but does not change which children exist. Sound pruning removes no path to a valid completion. Because every surviving child is eventually explored, every valid root-to-leaf path is eventually visited regardless of the permutations. If traversal continues to exhaustion, the same argument at every node shows that every policy visits the same fixed tree; only the visitation order differs.

### [CONJECTURE] Empirical statement

A predictor trained on held-out local data reduces expected nodes visited before the first valid Hadamard completion relative to lexicographic and random branch ordering.

### Experiment

Compare lexicographic, random, empirical $k$-Markov, and optionally learned policies using identical normalization, constraints, instances, stopping conditions, and seeds. Treat node count and backtracks as primary; timing is secondary.

### Limitation

A branch-ordering claim requires a first-solution or otherwise order-sensitive stopping rule. It cannot reduce the node count of a fixed tree that is fully enumerated.

### Proposed note title

*Complete Hadamard Search with Statistical Branch Ordering*

## Note 7 / Experiment G: Constraint ablation

**Narrative role:** closes the arc by separating gains caused by global choreography and safe pruning from the additional gain caused by local statistical ordering.

### Question

Which gains come from exact global structure, and which come from local statistical guidance?

### [DERIVED] Proposition: nested exact search spaces

Let $P_1$ and $P_2$ be sound pruning systems, with every constraint in $P_1$ also present in $P_2$. Then

$$
\mathcal T(P_2)\subseteq\mathcal T(P_1),
$$

where $\mathcal T(P)$ is the set of nodes surviving pruning system $P$. Adding a sound feasibility condition cannot enlarge the complete search tree or remove a valid solution.

**Proof.** A node surviving $P_2$ violates none of the constraints in $P_2$. Because every constraint in $P_1$ also belongs to $P_2$, the node violates none of the constraints in $P_1$, proving the set inclusion. Soundness ensures that any node removed by the additional constraints has no valid completion.

Canonical symmetry breaking is slightly different: it may remove equivalent valid matrices, so its obligation is to preserve at least one representative of every equivalence class in scope.

### [CONJECTURE] Empirical statement

Normalization, balance, orthogonality, partial-inner-product pruning, and symmetry breaking produce distinct reductions in search size, while the local model supplies an additional first-solution ordering gain.

### Experiment

Benchmark the cumulative sequence

```text
naive
+ normalization
+ balance
+ row orthogonality
+ partial-inner-product pruning
+ symmetry breaking
+ local branch ordering
```

Use the same verifier and instance set throughout. Report both cumulative and marginal changes, noting that interactions mean marginal gains can depend on the order of the ablation.

### Limitation

An ablation attributes performance within the tested solver design; it does not prove that the same contribution will hold for every solver architecture.

### Proposed note title

*Exact and Statistical Sources of Efficiency in Hadamard Search*

## Narrative arc

The proposed notes form the following chain:

$$
\text{global balance creates a calculable local dependence}
$$

$$
\Downarrow
$$

$$
\text{Hadamard orthogonality may contribute additional information}
$$

$$
\Downarrow
$$

$$
\text{bias, log loss, and entropy quantify that information}
$$

$$
\Downarrow
$$

$$
\text{context and transpose tests identify its scale and source}
$$

$$
\Downarrow
$$

$$
\text{the signal guides a complete first-solution search}
$$

$$
\Downarrow
$$

$$
\text{ablations separate classical constraint gains from statistical gains}.
$$

## Execution order

1. **Complete:** freeze the row-reset probability model and primary held-out metric.
2. **Complete:** assemble and independently verify the small-order corpus and matched controls.
3. **Complete:** run the repeated class splits, leakage audits, order sweep, and context sweep for Note 1.
4. **Complete:** establish that canonical representatives carry held-out local signal but that no practically meaningful residual beyond balance is detected after equivalence-preserving permutation at the primary comparison.
5. **Complete:** write Note 1 as a representation-dependence result, with the fixed-catalog and small-order limitations explicit.
6. **Next:** test transpose/traversal dependence separately if needed for the later local-statistics arc.
7. Implement the exact solver and verify all pruning logic with unit tests.
8. Benchmark whether the representation-dependent predictor improves branch ordering under a first-solution stopping rule.
9. Run the full search ablation and select the strongest supported paper arc.

The first decision point is now resolved: the invariant residual is not the signal to build on. Any search heuristic should instead test the strong canonical-coordinate signal under a solver using the same representation convention.

## Standard structure for each short note

Each note should contain:

1. question and motivation;
2. exact probability or search model;
3. definitions;
4. mathematical statement and proof;
5. smallest falsification test;
6. experimental method;
7. results with uncertainty;
8. interpretation;
9. what the result does not establish;
10. reproducibility metadata and next question.

The final paper should be selected from results that survive held-out testing, controls, and replication across orders or families. The narrative should follow the evidence rather than requiring every proposed note to support its initial conjecture.
