# Algorithms

## 1. Naive brute force

A completely naive search tests matrices

$$
H\in\{-1,+1\}^{d\times d},
$$

so the raw candidate count is

$$
2^{d^2}.
$$

For each candidate, test

$$
HH^\top=dI.
$$

This is useful only as a conceptual baseline.

---

## 2. Normalize symmetries first

Fix the first row and first column to $+1$.

This removes row/column sign symmetries and reduces the number of free entries.

Every nonfirst row must also be balanced.

A candidate row with first coordinate fixed to $+1$ has

$$
\binom{d-1}{d/2}
$$

possible balanced completions rather than $2^{d-1}$.

Further symmetry breaking can fix a canonical second row.

---

## 3. Row-wise exact backtracking

Construct normalized rows one at a time.

For each candidate row $r$:

1. enforce balance;
2. require $\langle r,r_j\rangle=0$ for every previously accepted row $r_j$;
3. recurse;
4. backtrack on failure.

Pseudocode:

```text
search(rows):
    if len(rows) == d:
        return rows

    for r in balanced_candidates_in_canonical_order:
        if orthogonal_to_all(r, rows):
            ans = search(rows + [r])
            if ans exists:
                return ans

    return failure
```

This is already dramatically better than testing all $2^{d^2}$ matrices, but still combinatorial.

---

## 4. Coordinate-wise exact pruning

When constructing rows incrementally by coordinates, maintain

$$
S_{ij}(k)
=
\sum_{\ell=1}^{k}H_{i\ell}H_{j\ell}.
$$

With $d-k$ positions remaining, eventual orthogonality requires

$$
|S_{ij}(k)|\le d-k.
$$

If not, prune.

Also enforce feasibility of final row balance. If a partial row currently has $p$ pluses and $m$ minuses, the remaining $d-k$ slots must be capable of bringing both totals to $d/2$.

This converts global structure into local impossibility tests.

---

## 5. Constraint-guided branch ordering

Suppose a local model gives

$$
\hat p(+1\mid C_k).
$$

At a branch:

```text
if p_hat >= 1/2:
    try +1 first, then -1
else:
    try -1 first, then +1
```

All exact Hadamard feasibility constraints remain authoritative.

This preserves completeness: a poor predictor can make the search slower, but cannot eliminate a valid matrix if both branches remain available.

### Important distinction

**Safe pruning**

```text
discard branch because a mathematical constraint proves no completion exists
```

versus

**Heuristic ordering**

```text
try one branch first because a statistical model says it is more promising
```

Never conflate them.

---

## 6. Suggested solver architecture

```text
HadamardSearch
├── normalization
├── balance_constraints
├── orthogonality_constraints
├── partial_sum_pruning
├── symmetry_breaking
├── branch_policy
│   ├── lexicographic
│   ├── random
│   ├── k_markov
│   └── learned
├── instrumentation
│   ├── nodes_visited
│   ├── branches_pruned
│   ├── backtracks
│   ├── depth_histogram
│   └── wall_time
└── verifier
```

The verifier should be independent of the search implementation.

---

## 7. Benchmark metrics

For each $d$ and search policy, record:

$$
N_{\text{nodes}},
\quad
N_{\text{backtracks}},
\quad
N_{\text{pruned}},
\quad
T_{\text{wall}},
\quad
T_{\text{cpu}}.
$$

Primary algorithmic comparison:

$$
\text{speedup}
=
\frac{N_{\text{nodes, baseline}}}
     {N_{\text{nodes, proposed}}}.
$$

Node count is often a cleaner research metric than wall time because it is less hardware-dependent.

---

## 8. Near-term coding targets

1. implement a trusted Hadamard verifier;
2. implement normalized balanced row generation;
3. implement exact row-wise backtracking;
4. add partial inner-product pruning;
5. add canonical symmetry breaking;
6. add instrumentation;
7. add row/column $k$-gram statistics;
8. add a Markov branch-ordering policy;
9. compare against lexicographic and random branch ordering;
10. only after this, explore learned branch policies.
