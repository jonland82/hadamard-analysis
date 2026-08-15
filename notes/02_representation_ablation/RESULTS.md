# Note 2 Results: From Serialized Signal to Constraint State

The one-sentence narrative is:

> Hadamard matrices are globally choreographed, locally elusive entry by entry, yet regionally predictable through their evolving constraint state—structure that may guide an exact search.

Note 1 showed that catalog representatives are locally predictable on held-out equivalence classes, while arbitrary equivalent presentations are not meaningfully better than balanced-row controls. Note 2 localizes that difference: the signal is carried mainly by the coordinate order *within* each predicted row or column, not by the order in which independent rows or columns are pooled and not primarily by normalization anchors.

## Part I: Where the serialized signal lives

### Formal setup

For row-reset traversal, let

$$
N_k^H(c,x)
$$

denote the number of occurrences of context $c\in\{-1,+1\}^k$ followed by $x\in\{-1,+1\}$, with contexts forbidden to cross row boundaries. The smoothed predictor is

$$
\widehat p_k(+1\mid c)
=
\frac{N_k^{\mathrm{train}}(c,+1)+\alpha}
{N_k^{\mathrm{train}}(c,+1)+N_k^{\mathrm{train}}(c,-1)+2\alpha},
\qquad \alpha=\frac12.
$$

For held-out targets $X_i$, define the gain over the fair coin in nats per entry by

$$
G_k
=
\log 2
-
\left(
-\frac1n\sum_{i=1}^n
\log \widehat p_k(X_i\mid C_{k,i})
\right).
$$

Positive $G_k$ means that the bounded-context model predicts held-out signs better than a fair coin.

### Exact statements

### Lemma 1: pooling invariance

Let $P$ be any row-permutation matrix. Under row-reset traversal,

$$
N_k^{PH}(c,x)=N_k^H(c,x)
$$

for every $c$ and $x$. Dually, for any column-permutation matrix $Q$, column-reset traversal satisfies

$$
N_{k,\mathrm{column}}^{HQ}(c,x)
=
N_{k,\mathrm{column}}^H(c,x).
$$

**Proof.** Row-reset counts are sums of within-row counts. Left multiplication by $P$ only reorders those summands. The column statement follows by the same argument. $\square$

### Proposition 2: within-sequence sensitivity

A column permutation may change row-reset counts, because it changes adjacency within every row. A row permutation may analogously change column-reset counts. Neither change is forbidden by Hadamard equivalence.

**Proof.** For row-reset traversal, right multiplication by a permutation matrix maps the sequence $(H_{i1},\ldots,H_{id})$ to a coordinate permutation of that sequence. General coordinate permutations do not preserve length-$k$ substrings. The dual statement follows by exchanging rows and columns. $\square$

### Proposition 3: transpose correspondence

For every matrix $H$ and every $k$,

$$
N_{k,\mathrm{column}}^H(c,x)
=
N_{k,\mathrm{row}}^{H^\top}(c,x).
$$

**Proof.** The columns of $H$ are exactly the rows of $H^\top$, in the same coordinate order. $\square$

These statements predict two exact negative controls: whole-row permutation cannot affect row-reset prediction, and whole-column permutation cannot affect column-reset prediction.

### Experiment

The experiment uses all $60$ order-$24$ and $487$ order-$28$ equivalence-class representatives in the verified McKay corpus. Each of $20$ repetitions makes an $80/20$ class-level train/test split: $48/12$ matrices at order $24$ and $390/97$ at order $28$. Every split passes digest and source-index leakage audits.

For each split and $k=1,\ldots,12$, the paired conditions are:

- catalog representatives;
- permutations of nonfirst rows, preserving the normalized anchor;
- permutations of nonfirst columns, preserving the normalized anchor;
- permutations of both nonfirst axes;
- unrestricted permutations of both axes followed by renormalization;
- row-reset and column-reset traversal;
- catalog prediction using all entries, excluding the first row, excluding the first column, or using only the strict interior.

Intervals below are percentile $95\%$ intervals from $10{,}000$ paired bootstrap resamples over the $20$ repetitions. The primary comparison retains Note 1's $k=8$ reference point.

### Results

### Axis localization at $k=8$

| Order | Traversal | Catalog gain | Cross-coordinate permutation gain | Paired loss of gain |
|---:|:---|---:|---:|---:|
| $24$ | rows | $0.16573$ | $0.03212$ | $0.13361\ [0.12498,0.14186]$ |
| $24$ | columns | $0.15928$ | $0.03311$ | $0.12617\ [0.11704,0.13481]$ |
| $28$ | rows | $0.13935$ | $0.03041$ | $0.10895\ [0.10808,0.10975]$ |
| $28$ | columns | $0.12361$ | $0.03037$ | $0.09323\ [0.09249,0.09395]$ |

“Cross-coordinate permutation” means column permutation for row traversal and row permutation for column traversal. Along the pooled-sequence axis, the corresponding same-axis permutation effect is zero to numerical precision; the largest absolute discrepancy over both orders and all $k$ is below

$$
4\times10^{-17}.
$$

Thus the exact invariance controls pass, while disrupting within-sequence coordinate order removes most of the predictive gain.

### Normalization ablation at $k=8$

| Order | Traversal | All entries | Strict interior |
|---:|:---|---:|---:|
| $24$ | rows | $0.16573$ | $0.15113$ |
| $24$ | columns | $0.15928$ | $0.14035$ |
| $28$ | rows | $0.13935$ | $0.11929$ |
| $28$ | columns | $0.12361$ | $0.10625$ |

Removing both deterministic anchors reduces gain by $0.01459$--$0.02006$ nats/entry, but leaves most of the catalog effect intact. Moreover, after both axes are randomized, fixed-anchor and unrestricted-permutation-plus-renormalization gains differ by at most $0.00039$ nats/entry at $k=8$. The representation effect is therefore not mainly a first-row or first-column artifact.

### Context sweep

Catalog gain continues to increase through the prespecified maximum $k=12$, reaching $0.27354$ and $0.24624$ nats/entry for row traversal at orders $24$ and $28$. Randomized conditions peak near $0.033$ nats/entry at $k=8$ or $10$. This is evidence of longer within-coordinate regularity in the catalog representatives, but $k=12$ is an endpoint and not an established optimal scale.

## Part II: State-aware regional prediction

Part I showed that adjacency in an arbitrary serialization is not an intrinsic local object. The constructive response is to define locality by a partial exact-search state.

After $m$ entries of normalized nonfirst row $i$ have been fixed, write

$$
R_i(m)=\sum_{\ell=1}^{m}H_{i\ell},
\qquad
S_{ij}(m)=\sum_{\ell=1}^{m}H_{i\ell}H_{j\ell},
\qquad
r=d-m.
$$

Balance and orthogonality require the remaining region to satisfy

$$
\sum_{\ell=m+1}^{d}H_{i\ell}=-R_i(m),
\qquad
\sum_{\ell=m+1}^{d}H_{i\ell}H_{j\ell}=-S_{ij}(m).
$$

Consequently, the remaining row contains exactly

$$
P_i(m)=\frac{r-R_i(m)}{2}
$$

plus signs, while the remaining products with row $j$ contain exactly

$$
A_{ij}(m)=\frac{r-S_{ij}(m)}{2}
$$

agreements. If the remaining coordinates are uniformly reordered, the plus count $Y_b$ and pair-agreement count $Z_b$ in the next block of size $b$ obey

$$
\Pr(Y_b=q\mid R_i(m))
=
\frac{\binom{P_i(m)}{q}\binom{r-P_i(m)}{b-q}}
{\binom{r}{b}},
$$

and

$$
\Pr(Z_b=q\mid S_{ij}(m))
=
\frac{\binom{A_{ij}(m)}{q}\binom{r-A_{ij}(m)}{b-q}}
{\binom{r}{b}}.
$$

These are exact finite-population laws under randomized remaining-coordinate order. They convert global correction obligations into local regional forecasts.

### Experiment

For $b\in\{2,4,8\}$ and a serialized context of length $4$, the experiment predicts two categorical summaries:

- `row_plus_count`: $Y_b$, the number of plus signs in the next block;
- `pressured_pair_agreement_count`: $Z_b$ for the previous nonfirst row maximizing $|S_{ij}(m)|$, the constraint currently under greatest pairwise pressure.

Four predictors are evaluated on the same $20$ class-level splits:

1. fair binomial regional guessing;
2. a smoothed serialized-context table;
3. the exact constraint-state hypergeometric distribution;
4. a state-plus-context table shrunk toward the exact state distribution.

The experiment is repeated for catalog matrices, fixed-anchor permutations of both axes, and unrestricted permutations followed by renormalization. Results are stratified into early, middle, and late construction so terminal forcedness cannot masquerade as early search guidance.

### Representation-resilient result

The table reports constraint-state gain over fair regional guessing, in held-out nats per block, for unrestricted permuted-and-renormalized matrices at $b=8$.

| Order | Target | Early gain | Middle gain | Late gain |
|---:|:---|---:|---:|---:|
| $24$ | row plus count | $0.08509\ [0.08491,0.08528]$ | $0.38506\ [0.38454,0.38560]$ | $1.61627\ [1.61560,1.61700]$ |
| $24$ | pressured-pair agreements | $0.16700\ [0.15622,0.17809]$ | $0.90181\ [0.88778,0.91708]$ | $2.50250\ [2.48059,2.52455]$ |
| $28$ | row plus count | $0.05724\ [0.05720,0.05728]$ | $0.20139\ [0.20114,0.20162]$ | $1.63785\ [1.63761,1.63811]$ |
| $28$ | pressured-pair agreements | $0.12014\ [0.11727,0.12273]$ | $0.54619\ [0.54202,0.54999]$ | $2.66587\ [2.66021,2.67123]$ |

All early-stage intervals are above zero for every tested $b=2,4,8$ at both orders. The fixed-anchor randomized presentation gives nearly the same result. Thus this signal does survive changes of representation, provided prediction is expressed through the evolving correction state rather than coordinate adjacency.

At unrestricted randomized order $28$, $b=8$, the constraint predictor also reduces early pressured-pair count RMSE from $1.30558$ to $1.16500$ and middle RMSE from $1.65017$ to $0.97291$.

### What serialized context adds

In randomized presentations, the state-plus-context model is slightly worse than the exact state model in every nonterminal comparison; for example, its order-$28$, $b=8$ residual gains are $-0.00337$ nats early and $-0.02004$ middle for pressured-pair agreement. The finite context table adds estimation noise but no detectable representation-robust information.

In catalog order, context retains a large residual. At order $28$, $b=8$, it adds $0.17693$ nats early and $0.39279$ middle for pressured-pair agreement, and $0.58389$ early and $0.76112$ middle for row composition. This cleanly separates the two phenomena:

$$
\text{constraint-state regional signal}
\quad\text{survives randomized representation},
$$

whereas

$$
\text{serialized-context residual}
\quad\text{belongs to catalog coordinate order}.
$$

## Part III: Nonterminal candidate-block ranking

Regional prediction is useful for search only if it distinguishes candidate continuations. For a partial state, let $\mathcal F_b$ be the blocks $x\in\{-1,+1\}^b$ that pass the immediate exact balance and pairwise feasibility conditions after assignment. Terminal states and states with $|\mathcal F_b|=1$ are excluded.

For candidate $x$, let $q_0(x)$ be its plus count and $q_j(x)$ its agreement count with prior row $j$. The all-pair score is the composite log likelihood

$$
L_{\mathrm{all}}(x)
=
\log \Pr(Y_b=q_0(x)\mid R_i(m))
+
\sum_{j<i}
\log \Pr(Z_{b,j}=q_j(x)\mid S_{ij}(m)).
$$

Because the pair constraints are dependent, $L_{\mathrm{all}}$ is a ranking score rather than a claimed joint probability. It is compared with random order, balance alone, balance plus a random prior pair, balance plus the most-pressured pair, and the heuristic that minimizes the worst absolute partial sum after the block.

Each repetition samples at most $500$ ambiguous states per order, block size, stage, and presentation. The metric is the tie-aware percentile of the observed valid block among $\mathcal F_b$, with $0.5$ representing random order.

### Candidate-ranking result

For unrestricted permuted-and-renormalized matrices at $b=8$:

| Order | Stage | Balance percentile | Pressured-pair percentile | All-pair percentile | All-pair top-decile rate |
|---:|:---|---:|---:|---:|---:|
| $24$ | early | $0.5827$ | $0.6543$ | $0.8760\ [0.8739,0.8781]$ | $0.6436$ |
| $24$ | middle | $0.6224$ | $0.6508$ | $0.8592\ [0.8562,0.8621]$ | $0.7371$ |
| $28$ | early | $0.5634$ | $0.6209$ | $0.8481\ [0.8447,0.8515]$ | $0.5857$ |
| $28$ | middle | $0.6270$ | $0.7324$ | $0.9316\ [0.9293,0.9339]$ | $0.8004$ |

The interval shown is for the all-pair percentile minus the random value $0.5$, translated back to percentile. The all-pair effect is positive for every $b=2,4,8$, order, stage, and presentation. Under unrestricted randomization its percentile ranges are:

| Block size | Order-$24$ early/middle | Order-$28$ early/middle |
|---:|:---:|:---:|
| $2$ | $0.6602/0.7307$ | $0.6542/0.7384$ |
| $4$ | $0.7447/0.8322$ | $0.7467/0.8447$ |
| $8$ | $0.8760/0.8592$ | $0.8481/0.9316$ |

At order $28$, $b=8$, minimum-worst-pressure reaches percentiles $0.7357$ early and $0.8655$ middle, below the all-pair score's $0.8481$ and $0.9316$. Thus the distributional score adds information beyond a simple “repair the worst constraint” rule.

The ablation also resolves an important question. Balance-only ranking is positive but modest; one pair improves it; combining all prior-row orthogonality obligations is decisively stronger. The regional guidance is therefore not merely row balance in disguise.

This is an offline ranking result on observed valid continuations. It does not establish that the highest-ranked counterfactual block has a full Hadamard completion or that the policy reduces solver nodes. Those require a complete search benchmark.

## Interpretation for the narrative

Part I establishes why individual serialized entries remain locally elusive rather than an equivalence-invariant local law:

$$
\text{catalog coordinate order}
\Longrightarrow
\text{transferable bounded-context signal},
$$

while

$$
\text{arbitrary equivalent coordinate order}
\Longrightarrow
\text{only the small baseline-scale residual}.
$$

The negative Part I conclusion still holds for individual serialized windows, but it no longer ends the search arc. Part II identifies representation-resilient regional predictability derived directly from global choreography. The revised hinge is:

> Hadamard structure may be locally unpredictable entry by entry, yet globally imposed correction pressures make regional behavior predictable enough to become a candidate guide for exact construction.

The constraint-state predictor is available during search and needs no catalog coordinate convention. Part III now shows that its all-pair score strongly ranks observed valid nonterminal blocks, including after unrestricted representation randomization. Probabilities remain unsafe as pruning rules, and the offline ranking result does not yet show a reduction in nodes or time. A first-solution solver benchmark is the next falsification test and the natural start of the next note.

## Reproducibility

From [`experiments/`](../01_bounded_context_predictability/experiments/):

```powershell
$env:PYTHONPATH = "src"
python -m hadamard_note1.note2 --orders 24,28 --max-context 12 --base-seed 20260814 --repetitions 20 --bootstrap-resamples 10000 --output ../../02_representation_ablation/results/note2_raw.csv
```

The run completed locally in approximately $240$ seconds. Outputs are:

- [`note2_raw.csv`](results/note2_raw.csv): $7{,}680$ condition-level measurements;
- [`note2_raw_summary.csv`](results/note2_raw_summary.csv): means, paired differences, and bootstrap intervals;
- [`note2_raw_metadata.json`](results/note2_raw_metadata.json): environment, command, seeds, splits, and audits.

The state-aware regional run is:

```powershell
$env:PYTHONPATH = "src"
python -m hadamard_note1.note2_state --orders 24,28 --block-sizes 2,4,8 --context-length 4 --base-seed 20260814 --repetitions 20 --bootstrap-resamples 10000 --output ../../02_representation_ablation/results/state_regional_raw.csv
```

It completed locally in approximately $1{,}199$ seconds. Outputs are:

- [`state_regional_raw.csv`](results/state_regional_raw.csv): $11{,}520$ held-out measurements;
- [`state_regional_raw_summary.csv`](results/state_regional_raw_summary.csv): repetition means and paired-bootstrap intervals;
- [`state_regional_raw_metadata.json`](results/state_regional_raw_metadata.json): environment, command, seeds, splits, and audits.

The nonterminal ranking run is:

```powershell
$env:PYTHONPATH = "src"
python -m hadamard_note1.note2_ranking --orders 24,28 --block-sizes 2,4,8 --context-length 4 --max-states-per-stage 500 --base-seed 20260814 --repetitions 20 --bootstrap-resamples 10000 --output ../../02_representation_ablation/results/candidate_ranking_raw.csv
```

It completed locally in approximately $118$ seconds. Outputs are:

- [`candidate_ranking_raw.csv`](results/candidate_ranking_raw.csv): $4{,}320$ paired policy measurements;
- [`candidate_ranking_raw_summary.csv`](results/candidate_ranking_raw_summary.csv): means and repetition-bootstrap intervals;
- [`candidate_ranking_raw_metadata.json`](results/candidate_ranking_raw_metadata.json): environment, command, samples, splits, and audits.
