# Python Experiment Plan

## Current implementation

The package now provides:

- exact integer Hadamard construction, normalization, and verification;
- parsing and cached download of Brendan McKay's equivalence-class corpus;
- row-major context extraction with explicit boundary and normalization ablations;
- smoothed fixed-context prediction;
- training and held-out log loss, accuracy, unseen-context rate, entropy, and bias metrics;
- Sylvester smoke tests and same-order equivalence-class holdouts;
- permuted-Hadamard, balanced-row, and normalized-IID controls;
- deterministic CSV and JSON metadata output.

The implementation uses vectorized integer context encoding and NumPy counting. The controlled orders 16--28 sweep runs locally in well under a minute after data download.

## Commands

From this directory in PowerShell:

```powershell
python -m pytest
$env:PYTHONPATH = "src"
python -m hadamard_note1.cli smoke --max-context 8 --output results/smoke.csv
python -m hadamard_note1.cli corpus --orders 16,20,24,28 --max-context 8 --seed 20260814 --include-controls --output results/corpus_controls.csv
python -m hadamard_note1.cli robustness --orders 16,20,24,28 --max-context 12 --base-seed 20260814 --repetitions 20 --bootstrap-resamples 10000 --output results/robustness_raw.csv
```

The corpus command downloads missing raw files from the [McKay Hadamard collection](https://users.cecs.anu.edu.au/~bdm/data/hadamard.html), verifies every matrix exactly, and caches the source files under the ignored `data/raw/` directory.

The robustness command runs the five finalized checks using paired class-level splits, fresh equivalent presentations and controls, a $k=1,\ldots,12$ sweep, explicit leakage audits, and percentile bootstrap intervals across repetitions. It writes raw results, a summary table, and JSON metadata containing every audited split.

## First implementation milestone

Build the smallest auditable pipeline that can:

1. load a matrix;
2. normalize it;
3. verify exactly that its entries are signs and that $HH^\top=dI_d$;
4. flatten it in row-major order;
5. extract $(C_k,X_{t+1})$ observations with explicit boundary rules;
6. fit a smoothed binary context-frequency model;
7. report training and held-out log loss against declared baselines.

## Initial configurations

Run each matrix under:

```text
full_row_major
reset_at_row_boundary
exclude_first_row
exclude_first_column
random_row_permutation
random_column_permutation
```

Use the same interface for controls:

```text
iid_rademacher
uniform_balanced_rows
shuffled_hadamard
```

## Initial context sweep

Begin with

$$
k=1,2,\ldots,8.
$$

Increase $K$ only after inspecting context support. There are $2^k$ possible binary contexts, so sparse counts and overfitting grow quickly.

## Evaluation

The primary metric is held-out log loss:

$$
L
=
-\frac1N\sum_t
\log \widehat p(X_{t+1}\mid C_k).
$$

Also record:

- fair-coin and marginal-only log loss;
- context counts and unseen-context rate;
- $\widehat\varepsilon_k^{\mathrm{avg}}$ and $\widehat\varepsilon_k^{\max}$;
- accuracy as a secondary metric;
- matrix order, identity, family, normalization, traversal, boundary rule, split, and seed.

## Split discipline

Do not use a random position split as the primary result. The primary split must hold out complete matrices or equivalence classes. Position-level splits may be reported only as a deliberately weak comparison.

## Reproducibility

Every generated result must record:

```text
command
git_commit
python_version
dependency_versions
matrix_source
matrix_hash
order_d
context_length_k
configuration
split
seed
```

Raw counts and metrics should be written in machine-readable form. Figures and tables must be reproducible from those outputs rather than assembled manually.

## Note 3 exact-search extension

The package now also contains `hadamard_note1.note3_solver`, a complete blockwise Hadamard completion solver used to test constraint-state branch ordering. It keeps exact feasibility and symmetry rules fixed across policies, records node, backtrack, budget, timing, and digest audits, and independently verifies every returned matrix. Commands and final outputs are documented in [`../../03_exact_search/`](../../03_exact_search/).
