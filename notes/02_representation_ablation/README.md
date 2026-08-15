# Note 2: From Serialized Windows to Constraint State

## Question

Note 1 found strong held-out bounded-context predictability in catalog representatives, but nearly all of it disappeared under equivalence-preserving permutations. Note 2 now asks two linked questions:

1. Where does the catalog-dependent signal live?
2. If individual serialized entries are not robustly predictable, do the exact global constraints make nearby *regional summaries* predictable from a partial construction state?

The revised canonical narrative is:

> Hadamard matrices reveal how global order can make local summaries predictable without making local decisions wise: the constraint state tells us what the next region should look like, but not which plausible region can belong to a complete whole.

The shift is that “local” now means local to the evolving solver state, not merely adjacent in a printed matrix.

## Experiments

### Part I: representation diagnosis

Across orders $24$ and $28$, context lengths $k=1,\ldots,12$, and $20$ paired class-level splits, the experiment compares catalog matrices with fixed-anchor and unrestricted equivalent permutations, row and column traversal, and normalization-anchor ablations.

### Part II: state-aware regional prediction

For next-block sizes $b\in\{2,4,8\}$, the experiment predicts:

- the number of plus signs in the next block;
- the agreement count between that block and the previously completed row under greatest current orthogonality pressure.

The models are a fair binomial baseline, serialized length-$4$ context, exact balance/orthogonality state, and state plus serialized context. They are evaluated in catalog, fixed-anchor-randomized, and unrestricted-permuted-and-renormalized presentations, separately at early, middle, and late construction stages.

### Part III: nonterminal candidate-block ranking

At sampled early and middle states, every block in $\{-1,+1\}^b$ is enumerated and filtered by exact immediate balance and pairwise-orthogonality feasibility. The observed valid continuation is ranked by random order, balance only, balance plus a random pair, balance plus the most-pressured pair, the composite likelihood over all prior pairs, and minimum worst remaining pressure. Terminal and already forced states are excluded.

Every condition uses the same source-class split. Exact source-index and digest leakage audits are applied to every split.

## Workshop manuscript

- [`paper/note2.pdf`](paper/note2.pdf) is the compiled four-page, single-column manuscript, *The Shape of What Remains*.
- [`paper/note2.tex`](paper/note2.tex) is the LaTeX source; [`paper/references.bib`](paper/references.bib) is its bibliography.

Build from `paper/` with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error note2.tex
```

## Mathematical statements

1. **Pooling invariance:** whole-row permutation cannot change pooled row-reset counts; the column-reset dual also holds.
2. **Within-sequence sensitivity:** opposite-axis permutation changes coordinate adjacency and may change serialized context counts.
3. **Exact correction burden:** after $m$ positions, the remaining row sum and every remaining pair-product sum are fixed by the current partial sums.
4. **Regional state law:** under a uniformly randomized remaining coordinate order, next-block plus and agreement counts have explicit hypergeometric distributions.
5. **Search safety:** regional probabilities may rank feasible blocks, but only proved infeasibility may prune them.

## Commands

From `notes/01_bounded_context_predictability/experiments/`:

```powershell
$env:PYTHONPATH = "src"
python -m hadamard_note1.note2 --orders 24,28 --max-context 12 --repetitions 20 --output ../../02_representation_ablation/results/note2_raw.csv
python -m hadamard_note1.note2_state --orders 24,28 --block-sizes 2,4,8 --context-length 4 --repetitions 20 --output ../../02_representation_ablation/results/state_regional_raw.csv
python -m hadamard_note1.note2_ranking --orders 24,28 --block-sizes 2,4,8 --max-states-per-stage 500 --repetitions 20 --output ../../02_representation_ablation/results/candidate_ranking_raw.csv
```

## Status

- **[DERIVED]:** the pooling, transpose, exact correction-burden, and hypergeometric statements follow from the definitions and Hadamard balance/orthogonality.
- **[EMPIRICAL]:** Part I contains $7{,}680$ measurements and $40$ passing leakage audits. It localizes the catalog signal to within-sequence coordinate order rather than pooled-sequence order or normalization anchors.
- **[EMPIRICAL]:** Part II contains $11{,}520$ measurements and $40$ passing leakage audits. Constraint state predicts regional summaries under randomized equivalent representations at every block size and every construction stage.
- **[EMPIRICAL]:** for unrestricted randomized order-$28$ matrices at $b=8$, early-stage gains over fair regional guessing are $0.05724$ nats for row composition and $0.12014$ nats for pressured-pair agreement. Middle-stage gains are $0.20139$ and $0.54619$.
- **[EMPIRICAL]:** serialized context adds no gain beyond constraint state after randomization, while retaining a large catalog-only residual.
- **[EMPIRICAL]:** on unrestricted randomized order-$28$ matrices at $b=8$, the all-pair score ranks observed valid blocks at the $84.8$th percentile early and $93.2$nd percentile in the middle; $58.6\%$ and $80.0\%$ fall in the top decile. Balance alone reaches only the $56.3$rd and $62.7$th percentiles.
- **[COMPLETE]:** the mathematical and experimental arc is written as the four-page Note 2 manuscript, revised to state the Note 3 online-search boundary.
- **[RESOLVED BY NOTE 3]:** the ranking often reduces nodes relative to random, balance-only, and pressure policies, but does not consistently beat lexicographic search and degrades with construction depth. See [`../03_exact_search/`](../03_exact_search/).

The complete formalism, tables, limitations, and narrative interpretation are in [`RESULTS.md`](RESULTS.md). Raw measurements, bootstrap summaries, and run metadata are under [`results/`](results/).
