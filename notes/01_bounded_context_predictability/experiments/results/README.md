# Result Artifacts

- `smoke.csv` and `smoke_metadata.json`: generated Sylvester train-orders 4/8/16, held-out order 32.
- `corpus_controls.csv` and metadata: orders 16/20/24/28, seed `20260814`, with Hadamard, permuted-equivalent, balanced-row, and normalized-IID variants.
- `corpus_controls_seed_20260815.csv` and metadata: independent orders 24/28 replication seed.
- `robustness_raw.csv`: $3{,}840$ evaluations from 20 paired repetitions, four orders, four variants, and context lengths $1$--$12$ under the row-reset traversal.
- `robustness_raw_summary.csv`: bootstrap mean intervals for each variant and paired differences between canonical, permuted-equivalent, balanced-row, and IID conditions.
- `robustness_raw_metadata.json`: command/environment metadata, all class-level splits, and 80 passing leakage audits.

CSV files contain one row per order, variant, traversal configuration, and context length. JSON files record commands, environment, Git state, split indices, and experiment parameters.

The first three result pairs are pilot artifacts. The robustness artifacts are the current Note 1 evidence and were generated from the tested implementation in the same working tree. Regenerate them after the implementation is committed to attach a clean commit identifier to the archival version.
