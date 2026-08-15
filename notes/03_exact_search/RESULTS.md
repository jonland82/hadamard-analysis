# Note 3 Exact-Search Results

The canonical project sentence is:

> Hadamard matrices reveal how global order can make local summaries predictable without making local decisions wise: the constraint state tells us what the next region should look like, but not which plausible region can belong to a complete whole.

The controlled exact-search experiment supports a narrower reading of the final clause: regional state can guide search relative to weak or stochastic baselines, but the current marginal all-pair policy is not competitive with a simple structure-aligned lexicographic policy at meaningful construction depth.

## 1. Question

Note 2 established that the partial balance and orthogonality state predicts the composition of a next block from a known completed Hadamard matrix. Note 3 asks the operational question:

> If an exact solver uses those probabilities to choose its next feasible block, does it find any complete Hadamard matrix with fewer nodes and less time?

The distinction between *the known continuation* and *any completable continuation* is essential. Offline ranking evaluates one trajectory sampled from the solution set. Online search creates its own state distribution and may enter feasible states with no full completion.

## 2. Solver and exactness

Let $H_1,\ldots,H_t$ be completed normalized rows, and let $x=(x_1,\ldots,x_m)$ be the exposed prefix of the next row. Define

$$
R(m)=\sum_{\ell=1}^{m}x_\ell,
\qquad
S_j(m)=\sum_{\ell=1}^{m}x_\ell H_{j\ell},
\qquad
r=d-m.
$$

A necessary and sufficient condition for a sum $u$ to be correctable by $r$ remaining signs is

$$
|u|\le r
\qquad\text{and}\qquad
r-u\equiv0\pmod 2.
$$

The solver applies this test to $R(m)$ and every $S_j(m)$ after each candidate block. At a row boundary it requires exact balance and exact orthogonality. At a matrix boundary it independently verifies

$$
HH^\top=dI_d.
$$

### Proposition: policy-independent completeness

Fix the seed rows, row-order symmetry rule, candidate block size, and exact pruning predicates. If the node and time budgets are removed, every tested policy explores the same finite feasible tree in a different order. Therefore every policy is complete for the same restricted completion problem.

**Proof.** Candidate generation and feasibility do not inspect the policy. Policy scoring is applied only after the feasible child set has been constructed. Hence a policy permutes each node's children but neither adds nor deletes a child. Depth-first exhaustion consequently visits the same tree under every policy. The first solution may change, but existence and exhaustive completeness do not. $\square$

The finite experimental budgets truncate this complete procedure. A budget termination is censored and is not an unsatisfiability result.

## 3. Instances and controls

For orders $16$ and $20$, a catalog Hadamard matrix is subjected to a fixed-anchor random column permutation and random nonfirst-row ordering. A prefix of completed rows is revealed and either $4$ or $6$ rows are hidden. The solver receives only the revealed rows. The hidden target supplies a satisfiability witness and digest but is not available to branch ordering.

The construction test at order $12$ reveals only the normalized first row and one nonfirst row, leaving ten rows to construct. Since any normalized second row can be placed into the standard half-plus, half-minus form by column permutation, this is the practical full-from-symmetry-broken-start condition.

Newly generated rows are required to increase in the code that maps $+1\mapsto0$ and $-1\mapsto1$. Revealed rows are not included in that lower bound. This breaks permutation symmetry only among interchangeable newly generated rows and avoids the pilot artifact in which a sorted revealed prefix leaked the next target row to lexicographic search.

The policies are:

1. **Lexicographic:** try $+1$ before $-1$ within every block.
2. **Random:** deterministic hash order indexed by the tie seed.
3. **Balance-only:** descending exact hypergeometric probability for block plus count.
4. **All-pair:** balance log probability plus the marginal agreement log probabilities for all completed nonfirst rows.
5. **Minimum pressure:** minimize the largest absolute post-block balance or inner-product debt.
6. **All-pair/lex hybrid:** all-pair score first and lexicographic order within score ties.

All policies use identical exact pruning, instance data, budgets, and stopping conditions. Probability calculation and sorting time is included in wall time only for policies that require it.

## 4. Main benchmark

The main benchmark contains $900$ runs:

$$
2\text{ orders}
\times2\text{ depths}
\times3\text{ block sizes}
\times5\text{ presentations}
\times3\text{ tie repetitions}
\times5\text{ policies}.
$$

Across its $12$ order/depth/block conditions, randomized-tie all-pair ordering attains a lower median node count than:

| Baseline | Conditions with lower all-pair median |
|---|---:|
| balance-only | $11/12$ |
| random | $9/12$ |
| minimum maximum pressure | $10/12$ |
| lexicographic | $1/12$ |

This establishes that the pairwise regional state contributes something beyond balance alone. It does not establish a generally superior search policy.

At four hidden rows, the best all-pair effects occur at $b=8$. Relative to random ordering, its paired median node ratios are $0.36$ at order $16$ and $0.40$ at order $20$. Relative to balance-only, the ratios are $0.54$ and $0.37$. But relative to lexicographic ordering they are $0.96$ and $1.34$.

At six hidden rows, lexicographic ordering dominates. Depending on order and block size, the randomized-tie all-pair median node ratio over lexicographic ranges from $6.42$ to $13.12$ at order $16$ and from $10.86$ to $11.58$ among the fully solved order-$20$, $b\in\{2,4\}$ conditions. At order $20$, $b=8$, lexicographic solves all $15$ runs while all-pair solves $9$.

## 5. Primary $b=8$ robustness closure

The targeted closure increases each order/depth condition to $20$ randomized presentations and three tie repetitions, giving $60$ runs per policy and condition.

| Order | Hidden rows | Guided policy | Guided solved | Lex solved | Median node ratio | Median time ratio |
|---:|---:|---|---:|---:|---:|---:|
| $16$ | $4$ | all-pair, random ties | $60/60$ | $60/60$ | $1.38$ | $1.30$ |
| $16$ | $4$ | all-pair, lex ties | $60/60$ | $60/60$ | $0.74$ | $0.84$ |
| $20$ | $4$ | all-pair, random ties | $60/60$ | $60/60$ | $1.27$ | $1.24$ |
| $20$ | $4$ | all-pair, lex ties | $60/60$ | $60/60$ | $1.27$ | $1.27$ |
| $16$ | $6$ | all-pair, random ties | $60/60$ | $60/60$ | $7.45$ | $8.38$ |
| $16$ | $6$ | all-pair, lex ties | $60/60$ | $60/60$ | $6.72$ | $7.75$ |
| $20$ | $6$ | all-pair, random ties | $38/60$ | $60/60$ | $5.79$ | $5.85$ |
| $20$ | $6$ | all-pair, lex ties | $39/60$ | $60/60$ | $5.51$ | $5.28$ |

Ratios use only jointly solved pairs; one-sided solve counts remain visible. Lexicographic tie-breaking makes the regional policy deterministic and helps in the shallow order-$16$ condition, but does not repair the depth failure.

## 6. Full order-$12$ construction

At $b=8$, five randomized presentations and three tie repetitions give $15$ runs per policy.

| Policy | Solved | Median nodes among solved | Median seconds among solved |
|---|---:|---:|---:|
| lexicographic | $15/15$ | $74$ | $0.063$ |
| all-pair, lex ties | $15/15$ | $1{,}385$ | $1.083$ |
| all-pair, random ties | $3/15$ | $23{,}056$ | $16.427$ |
| balance-only | $2/15$ | $1{,}090$ | $0.897$ |
| minimum maximum pressure | $1/15$ | $2{,}509$ | $1.940$ |
| random | $1/15$ | $25{,}033$ | $17.432$ |

Both lexicographic and the lex-tied hybrid are reliable, but the paired hybrid-over-lex median is $7.59$ for nodes and $15.21$ for time. The difference between randomized and lexicographic ties also shows that much of the raw regional policy's instability comes from large tied score classes. Even after that instability is removed, the regional preference itself remains inferior to lexicographic construction.

## 7. What the result says

### Supported

- The solver is exact when allowed to exhaust its finite tree; statistical scores only reorder branches.
- Regional all-pair information usually improves on balance-only and often improves on random or pressure-based ordering in shallow and moderate completion tasks.
- Lexicographic tie-breaking stabilizes the regional policy and is essential in the full order-$12$ test.
- Every one of the $1{,}952$ solutions reported among $2{,}070$ final runs passes independent exact verification.

### Not supported

- The current all-pair regional score does not generally reduce first-solution work relative to lexicographic ordering.
- Offline continuation percentile is not sufficient evidence of online search acceleration.
- The present result does not justify transferring the policy unchanged into a mature SAT/CAS solver.

### Explanation suggested by the evidence

The hypergeometric laws predict a block on a trajectory already known to belong to a completed matrix. During search, a greedy choice changes the distribution of future states. A block can satisfy every immediate marginal correction pressure and still lead to a region with few or no full completions. Those errors compound with construction depth. Lexicographic search, meanwhile, appears aligned with regular representatives or implicit algebraic structure in these small-order spaces.

This is an inference from the experiment, not yet a theorem.

## 8. Next research decision

The conditional post-Note 3 engineering gate required robust node reduction and a credible wall-clock gain against the strongest controlled baseline. That gate is not met. AWS is unnecessary for repeating the present benchmark.

A better next hypothesis is residual rather than replacement guidance:

> Given a strong structural baseline, can constraint state predict which apparently feasible branches will remain completable, or identify states where the structural heuristic is likely to fail?

Possible tests include predicting bounded look-ahead survival, estimating completion counts, using regional state to choose among algebraic templates, or learning a correction to lexicographic/SAT activity rather than using marginal block likelihood as the primary policy. Integration into mature SAT/CAS machinery should wait until one of those controlled tests beats the structural baseline.

## 9. Files and audit

Each result family includes:

- a raw run table;
- a policy summary;
- jointly solved paired effects;
- a paired summary that retains one-sided and two-sided budget failures;
- metadata containing commands, environment, source information, seeds, budgets, target/seed digests, and the verification audit.

The final raw tables contain $900$, $360$, $90$, and $720$ rows. Their job keys are unique. Solved rows have nonempty solution digests and `verification_passed=True`; capped rows have no solution digest and are never labeled unsatisfiable. Deterministic solved policies reproduce identical node counts, backtracks, and solution digests across nominal tie repetitions.
