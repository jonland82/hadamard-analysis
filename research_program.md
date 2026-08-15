# Research Program: Mathematical Notes and Experiments

## Purpose

The canonical one-sentence research narrative is:

> Hadamard matrices reveal how global order can make local summaries predictable without making local decisions wise: the constraint state tells us what the next region should look like, but not which plausible region can belong to a complete whole.

The work will be developed as a sequence of short notes. Each experiment is paired with a precise mathematical statement, an empirical hypothesis, and an explicit limitation. The strongest compatible sequence can later be consolidated into a final paper.

The completed Note 1 robustness study narrows the intended reading: catalog representatives are locally predictable at moderate context length, but nearly all of that serialized gain disappears after equivalence-preserving row and column permutations. Note 2 first localizes that effect to within-sequence coordinate order, then shifts from predicting individual entries to regional summaries of a partial construction. Exact balance and partial-inner-product state predicts next-block composition under randomized equivalent presentations, while serialized context adds no residual gain after randomization. Note 3 embeds that signal in a complete solver. It often improves on weak or stochastic ordering but loses to lexicographic search with increasing construction depth, so regional information is established while general online utility is not.

## Narrative-to-experiment map

| One-sentence clause | What must be established | Experiments and notes |
|---|---|---|
| **Globally choreographed** | The full matrix obeys exact orthogonality, normalization, balance, symmetry, and partial feasibility constraints. | Structural lemmas establish this; Experiment G will measure their separate algorithmic effects. |
| **Locally elusive entry by entry** | Short serialized contexts do not retain strong next-sign information across equivalent presentations. | Note 1 and Note 2's representation ablations establish this for the tested corpus. |
| **Regionally predictable through constraint state** | Partial sums fix remaining sign and agreement inventories, producing held-out next-block information. | Note 2 derives and tests the regional laws at $b=2,4,8$. |
| **Local decisions need not be wise** | The all-pair score orders feasible blocks without becoming an unsafe pruning rule, but marginal plausibility is not residual completability. | Note 3 finds conditional gains over weak baselines and a depth-dependent reversal against lexicographic construction. |

This table is not merely organizational. It records the dependency structure that has redirected the project twice: the serialized signal failed the representation test, so Note 2 moved to constraint-state regions; marginal regional likelihood then failed to beat structural search at depth, so the next target must be residual completability beyond a strong baseline.

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

**Narrative role:** distinguishes unavoidable balance dependence from representation-specific adjacency and begins the test of “locally elusive entry by entry.”

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

## Experiment B: Predictive log loss (completed within Note 1)

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

### [EMPIRICAL] Result

The smoothed context predictor improves held-out log loss substantially for catalog representatives. Under unrestricted equivalence-preserving permutations, its order-$28$, $k=8$ gain becomes statistically indistinguishable from the balanced-row baseline. This experiment was incorporated into Note 1 rather than reserved for a separate note.

### Experiment

Fit context-frequency or smoothed Markov predictors on training matrices and evaluate log loss on held-out matrices or equivalence classes. Report calibration and sample support as well as aggregate loss.

### Limitation

Training and evaluating on positions from the same matrix may measure memorization rather than transferable Hadamard structure.

## Deferred supporting experiment C: Conditional entropy and mutual information

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

## Deferred supporting experiment D: Dependence on context length

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

## Note 2 / Experiment E: From representation diagnosis to constraint-state regions

**Narrative role:** shows why serialized adjacency is the wrong invariant local object, then replaces it with the evolving balance and orthogonality state.

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

### [DERIVED] Lemma: pooled-sequence invariance

With row boundaries reset, permuting whole rows leaves every row-reset context count unchanged. Dually, permuting whole columns leaves every column-reset context count unchanged. A permutation of the opposite axis changes coordinate order within each sequence and may change the counts.

### [EMPIRICAL] Result

Both exact negative controls pass to numerical precision. At $k=8$, disrupting within-row coordinate order reduces catalog gain by $0.13361$ nats/entry at order $24$ and $0.10895$ at order $28$; the column-reset experiment gives the dual result. Strict-interior prediction retains most of the catalog gain, so deterministic normalization anchors are not its main source.

This negative result motivates a different local object. For a partial row, balance fixes the number of remaining plus signs, and each partial inner product fixes the number of remaining agreements with a completed row. Under randomized remaining-coordinate order, next-block counts are hypergeometric. The completed extension tests block sizes $b=2,4,8$ and finds positive early-, middle-, and late-stage held-out gain under both fixed-anchor and unrestricted equivalent randomizations. At unrestricted randomized order $28$, $b=8$, early gains are $0.05724$ nats for row composition and $0.12014$ nats for the agreement count with the most-pressured previous row.

Serialized context adds no gain beyond constraint state after randomization. It retains a large catalog-only residual, cleanly separating representation-specific adjacency from representation-resilient correction pressure.

The completed nonterminal ranking closure enumerates every $b\le8$ candidate, filters by immediate exact feasibility, and ranks observed valid continuations. The all-pair composite score outperforms balance-only, random-pair, pressured-pair, and minimum-worst-pressure policies under both randomized presentations. At unrestricted randomized order $28$, $b=8$, it reaches the $0.8481$ percentile early and $0.9316$ percentile in the middle.

### Experiment

First run paired axis, traversal, and normalization ablations. Then predict next-block row composition and pressured-pair agreement at $b=2,4,8$ from the exact partial state under catalog and randomized presentations. Finally enumerate immediately feasible nonterminal blocks and compare random, balance-only, one-pair, all-pair, and minimum-pressure ranking policies. Reuse identical class splits and report paired intervals throughout.

### Limitation

A difference in a non-transpose-invariant catalog is not evidence that Hadamard matrices in general have an intrinsic directional asymmetry. The regional state laws are exact under randomized remaining-coordinate order, but Note 3 shows that their predictive success does not generally reduce search work against lexicographic ordering.

### Results

The completed four-page manuscript is [*The Shape of What Remains*](notes/02_representation_ablation/paper/note2.pdf); full result tables and metadata are in [`notes/02_representation_ablation/`](notes/02_representation_ablation/).

## Note 3 / Experiment F: Statistical branch ordering

**Narrative role:** tests the final clause directly: whether the regional all-pair score guides an exact first-solution search while preserving completeness.

### Question

Can weak local information reduce the work required to find a valid completion without making the solver incomplete?

### [DERIVED] Theorem: completeness under branch ordering

Suppose pruning uses only sound impossibility conditions and every unpruned child is eventually explored. Reordering children using a statistical predictor does not change completeness.

For a fixed finite search tree, ordering can change the number of nodes visited before the first solution. If the whole tree is exhaustively enumerated and no stateful learning changes the tree, ordering alone does not change the total set of visited nodes.

**Proof.** A branch policy permutes the order of a node's children but does not change which children exist. Sound pruning removes no path to a valid completion. Because every surviving child is eventually explored, every valid root-to-leaf path is eventually visited regardless of the permutations. If traversal continues to exhaustion, the same argument at every node shows that every policy visits the same fixed tree; only the visitation order differs.

### [DERIVED] Proposition: perfect residual-completability guidance

For feasible state $s$ and child $x$, define

$$
V(s,x)=mathbf{1}\{\text{the subtree below }(s,x)\text{ contains a completion}\}.
$$

If the root is satisfiable and a policy always selects a child with $V(s,x)=1$, it reaches a solution without backtracking. This identifies the ideal online target and distinguishes it from next-block marginal likelihood.

### [DERIVED] Proposition: offline ranking does not imply online efficiency

For every $\varepsilon>0$ and integer $M$, a finite satisfiable search tree can have a policy that selects the successful child on at least a $1-\varepsilon$ fraction of offline successful-path states yet visits at least $M$ nodes before its first solution. Put little offline mass at the root, rank a large dead subtree first there, and rank the demonstrated child correctly downstream. The construction formalizes the distribution-shift failure tested by Note 3.

### [EMPIRICAL] Result

The all-pair regional policy often reduces first-solution nodes relative to balance-only, random, and minimum-pressure ordering, but it does not consistently reduce nodes relative to lexicographic ordering. Its relative performance deteriorates as more rows must be constructed.

### Experiment

Compare lexicographic, random, balance-only, minimum-pressure, all-pair, and lex-tied all-pair policies using identical normalization, constraints, instances, stopping conditions, and seeds. Treat node count and backtracks as primary; include solve rate under budget and wall time with ranking overhead.

### Results

The completed experiment suite and four-page manuscript [*Prediction Is Not a Search Policy*](notes/03_exact_search/paper/note3.pdf) are in [`notes/03_exact_search/`](notes/03_exact_search/). Its four final result families contain $2{,}070$ runs and $1{,}952$ independently verified solutions.

In the main $12$ order/depth/block conditions, randomized-tie all-pair ordering has a lower median node count than balance-only in $11$, random in $9$, minimum-pressure in $10$, and lexicographic in only $1$. In the $20$-presentation $b=8$ closure with six hidden rows, the lex-tied hybrid costs $6.72$ times the paired-median lexicographic nodes at order $16$. At order $20$ it solves $39/60$ runs versus lexicographic's $60/60$ and costs $5.51$ times the nodes among jointly solved pairs. In full order-$12$ construction, both policies solve all $15$ runs, but the hybrid costs $7.59$ times the paired-median nodes and $15.21$ times the wall time.

### Limitation

A branch-ordering claim requires a first-solution or otherwise order-sensitive stopping rule. It cannot reduce the node count of a fixed tree that is fully enumerated.

### Note title

*Prediction Is Not a Search Policy*

## Beyond Note 3: solver transfer

**Narrative role:** determines whether a branch-ordering effect established in the controlled solver remains useful inside stronger exact-search machinery.

### Decision gate: not met

Proceed only if a controlled policy shows a robust reduction in first-solution nodes and a credible net wall-clock improvement against the strongest structural baseline. Note 3 does not meet this requirement, so integration of the present marginal all-pair policy is deferred.

### Deferred engineering step

If a future residual policy first beats lexicographic search, embed that policy into either a mature SAT/CAS workflow or an optimized solver for a structured Hadamard family. Exact propagation, algebraic filtering, canonical symmetry breaking, and solution verification remain authoritative. Statistical information may choose variable polarity, cube priority, candidate-block order, or restart priority, but it may not remove a branch unless an independent exact rule proves that branch impossible.

### Evaluation

Compare the host solver with and without regional guidance on identical instances, budgets, symmetry rules, and hardware. Report conflicts or search nodes, backtracks, wall-clock time, time-to-first-solution distributions, ranking overhead, and verified completions. Test whether the gain survives:

- stronger constraint propagation than the controlled backtracker;
- canonicalization and symmetry breaking;
- higher orders and multiple structured construction families;
- incremental rather than recomputed state scores;
- difficult completion instances, not only orders with immediate formulaic constructions.

### Interpretation

A positive transfer would show that the residual statistic contributes information not already captured by a mature solver's native heuristics. Note 3 shows why this gate matters: predictive signal can beat weak policies while remaining redundant with, or opposed to, a simple structural heuristic.

## Deferred companion experiment G: Constraint ablation

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
\text{global balance and orthogonality create exact correction inventories}
$$

$$
\Downarrow
$$

$$
\text{serialized adjacency proves representation-sensitive}
$$

$$
\Downarrow
$$

$$
\text{partial constraint state yields regional hypergeometric laws}
$$

$$
\Downarrow
$$

$$
\text{held-out experiments verify representation-resilient block prediction}
$$

$$
\Downarrow
$$

$$
\text{the all-pair score ranks ambiguous nonterminal blocks}
$$

$$
\Downarrow
$$

$$
\text{controlled search separates regional information from online utility}.
$$

$$
\Downarrow
$$

$$
\text{the next target is residual completability beyond structural search}.
$$

## Execution order

1. **Complete:** freeze the row-reset probability model and primary held-out metric.
2. **Complete:** assemble and independently verify the small-order corpus and matched controls.
3. **Complete:** run the repeated class splits, leakage audits, order sweep, and context sweep for Note 1.
4. **Complete:** establish that canonical representatives carry held-out local signal but that no practically meaningful residual beyond balance is detected after equivalence-preserving permutation at the primary comparison.
5. **Complete:** write Note 1 as a representation-dependence result, with the fixed-catalog and small-order limitations explicit.
6. **Complete:** localize the catalog signal with paired row/column traversal, axis-permutation, and normalization ablations.
7. **Complete:** derive and test state-aware next-block composition laws under randomized equivalent presentations.
8. **Complete:** show that the all-pair state score ranks ambiguous, nonterminal valid blocks above random, balance-only, one-pair, and minimum-pressure policies.
9. **Complete:** write Note 2 and revise the canonical narrative around the established global-to-regional result.
10. **Complete:** implement the controlled exact solver and verify its pruning and solution checks with unit tests.
11. **Complete:** run $2{,}070$ paired exact-search jobs across completion, robustness, hybrid, and full-construction conditions.
12. **Complete:** establish conditional gains over weak baselines and the depth-dependent failure against lexicographic search.
13. **Complete:** write Note 3 as the boundary between offline predictive information and online construction utility.
14. Develop and test residual branch-survival or completion-count prediction on top of a structural baseline.
15. **Conditional:** transfer a policy into mature SAT/CAS or optimized structured search only after it beats the controlled structural baseline in nodes and net time.

The first five decision points are resolved: the serialized invariant residual is not the signal to build on; the catalog effect lives mainly in within-sequence coordinate order; exact constraint pressure produces a separate, representation-resilient regional signal; the all-pair score strongly ranks observed valid blocks offline; and that marginal score does not compose into a generally superior online policy. The next decision is whether constraint state can predict residual branch survival beyond lexicographic structure.

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
