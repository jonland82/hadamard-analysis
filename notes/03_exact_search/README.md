# Note 3: Exact Search

This note tests whether the regional predictability established in Note 2 reduces the work required to construct or complete a Hadamard matrix when the prediction is used only to order exact-search branches.

The canonical project sentence is:

> Hadamard matrices reveal how global order can make local summaries predictable without making local decisions wise: the constraint state tells us what the next region should look like, but not which plausible region can belong to a complete whole.

Note 3 explains the second half of that sentence. Regional guidance often improves on random, balance-only, and minimum-pressure ordering, especially in shallow completions, but it does not consistently beat a simple lexicographic policy. Its advantage weakens or reverses as more rows must be composed into a complete matrix.

## Manuscript

- [`paper/note3.pdf`](paper/note3.pdf) is the compiled four-page, single-column manuscript, *Prediction Is Not a Search Policy*.
- [`paper/note3.tex`](paper/note3.tex) is the LaTeX source; [`paper/references.bib`](paper/references.bib) is its bibliography.

Build from `paper/` with:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error note3.tex
```

## Exact solver

The solver starts from pairwise-orthogonal normalized seed rows and constructs the remaining rows from left to right in blocks of size $b$. If a partial new row has sum $R$ and partial inner products $S_j$ with the completed nonfirst rows, with $r$ coordinates still unassigned, it retains the state only when

$$
|R|\le r,
\qquad
|S_j|\le r,
$$

and each target correction has the parity of a sum of $r$ signs. These are exact feasibility tests. Newly constructed rows are placed in strict sign-code order to remove their row-permutation symmetry; revealed seed rows are excluded from this ordering constraint so they do not leak the hidden target order.

Every policy sees the same feasible children and the same pruning. Policies differ only in child order:

- lexicographic;
- randomized order;
- balance-only regional probability;
- all-pair composite regional probability;
- minimum remaining maximum pressure;
- all-pair probability with lexicographic tie-breaking.

The hidden completed matrix is used only to manufacture satisfiable benchmark prefixes and to record an audit digest. It is never supplied to the solver. Every returned matrix is independently checked against

$$
HH^\top=dI_d.
$$

The manuscript's formal spine is:

1. **Exact scalar correctability:** magnitude and parity are necessary and sufficient for a signed sum to be repaired by the remaining coordinates.
2. **Policy-independent completeness:** reordering a fixed exact tree changes first-solution work but not its reachable solutions.
3. **Perfect-oracle benchmark:** always choosing a residually completable child reaches a solution without backtracking.
4. **Offline/online separation:** arbitrarily strong average ranking on successful-path states can still enter an arbitrarily large dead subtree during deployment.

## Final experiments

The retained result families contain $2{,}070$ exact-search runs:

1. [`note3_raw.csv`](results/note3_raw.csv): $900$ runs over orders $16$ and $20$, $4$ or $6$ hidden rows, $b\in\{2,4,8\}$, five randomized presentations, three tie repetitions, and five primary policies.
2. [`note3_hybrid_raw.csv`](results/note3_hybrid_raw.csv): $360$ paired runs testing whether lexicographic tie-breaking rescues the all-pair score.
3. [`note3_full12_raw.csv`](results/note3_full12_raw.csv): $90$ order-$12$ runs with only two rows revealed, so the solver constructs the other ten rows.
4. [`note3_primary_b8_raw.csv`](results/note3_primary_b8_raw.csv): $720$ targeted robustness runs with $20$ randomized presentations per order/depth condition at $b=8$.

Each job has a budget of $300{,}000$ entered feasible block nodes and $30$ seconds. A capped job is reported as budget-limited, never as a proof of nonexistence.

## Headline result

Across the $12$ order/depth/block conditions in the main benchmark, randomized-tie all-pair ordering has a lower median node count than balance-only in $11$, random ordering in $9$, minimum-pressure ordering in $10$, and lexicographic ordering in only $1$.

The $20$-presentation $b=8$ closure makes the depth effect clear. For four hidden rows at order $16$, the lex-tied all-pair hybrid uses a paired median $0.74$ times as many nodes as lexicographic search and $0.84$ times as much wall time. At order $20$, the corresponding ratios are $1.27$ and $1.27$. With six hidden rows, the ratios deteriorate to $6.72$ nodes and $7.75$ time at order $16$. At order $20$, lexicographic solves all $60$ runs, while the hybrid solves $39$; among the $39$ jointly solved runs, its median node and time ratios are $5.51$ and $5.28$.

In the full order-$12$ construction test, lexicographic and lex-tied all-pair both solve all $15$ runs. Lexicographic needs a median of $74$ nodes and $0.063$ seconds; the hybrid needs $1{,}385$ nodes and $1.083$ seconds. Randomized-tie all-pair solves only $3$ of $15$ within budget.

All $1{,}952$ reported solutions across the four final result families pass independent Hadamard verification. Full tables and interpretation are in [`RESULTS.md`](RESULTS.md).

## Interpretation

The Note 2 signal is real but is not yet a generally effective exact-construction policy. It predicts the next block on a trajectory drawn from a completed matrix; a live solver also visits counterfactual states, and locally probable blocks can compose into globally poor paths. Lexicographic ordering appears to exploit strong construction-aligned regularity that the marginal regional score does not represent.

Therefore the planned transfer into a mature SAT/CAS solver is not yet justified. The next useful question is narrower: can regional state predict *residual success beyond a structural baseline*, or identify when lexicographic search is likely to fail? AWS was not needed for the present experiments.

## Reproduction

From `notes/01_bounded_context_predictability/experiments/`, set the local package path and run:

```powershell
$env:PYTHONPATH='src'
python -m hadamard_note1.note3_solver --orders 16,20 --hidden-rows 4,6 --block-sizes 2,4,8 --policies lexicographic,random_order,balance_only,all_pair_product,minimum_max_pressure --instances-per-condition 5 --tie-repetitions 3 --max-nodes 300000 --max-seconds 30 --workers 8 --output ../../03_exact_search/results/note3_raw.csv
python -m hadamard_note1.note3_solver --orders 16,20 --hidden-rows 4,6 --block-sizes 8 --policies lexicographic,all_pair_product,all_pair_lexicographic --instances-per-condition 20 --tie-repetitions 3 --max-nodes 300000 --max-seconds 30 --workers 8 --output ../../03_exact_search/results/note3_primary_b8_raw.csv
python -m hadamard_note1.note3_solver --orders 12 --hidden-rows 10 --block-sizes 8 --policies lexicographic,random_order,balance_only,all_pair_product,all_pair_lexicographic,minimum_max_pressure --instances-per-condition 5 --tie-repetitions 3 --max-nodes 300000 --max-seconds 30 --workers 8 --output ../../03_exact_search/results/note3_full12_raw.csv
```

The hybrid ablation command is recorded in [`note3_hybrid_raw_metadata.json`](results/note3_hybrid_raw_metadata.json). Every metadata file records the exact command, environment, seeds, source digests, budgets, and instance audit.
